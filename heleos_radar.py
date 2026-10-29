"""Radar de precios 24/7 (laptop de 4 GB): lee enlaces.txt, guarda cada precio en precios.db,
detecta descuentos reales y súper ofertas, limpia nombres con IA y publica datos.json + alertas.json.

Requiere:  pip install requests beautifulsoup4
Uso:       python heleos_radar.py              una vuelta
           python heleos_radar.py --loop       24/7: una vuelta cada `intervalo_min` minutos
           python heleos_radar.py --probar-ia  comprueba la clave de Gemini con un título de prueba
           python heleos_radar.py --debug      muestra qué trae la primera página (si falla un precio)

Cero claves en el código. La clave de Gemini sale de la variable de entorno GEMINI_API_KEY (GitHub Secrets en Actions)
o, en una laptop, de "GEMINI_API_KEY" en heleos_config.json (nunca se sube a git); si no está, el radar se detiene.
Con repo + token de GitHub (archivo o variables de entorno, ver radar/config.py), lee enlaces.txt del repositorio y publica ahí en un solo commit; sin ellos, trabaja local.
"""
import hashlib
import json
import logging
import logging.handlers
import os
import random
import sys
import time

from radar import config, exportar, ia, reglas
from radar.db import DB
from radar.extraer import diagnostico, extraer, nueva_sesion
from radar.github import GitHub

ENLACES, DATOS, ALERTAS, BASE = "enlaces.txt", "datos.json", "alertas.json", "precios.db"
LEGADO = ("ofertas.json", "historial.json")   # formato anterior: se importa una vez y se retira del repo
PAUSA = (2.0, 5.0)                            # segundos aleatorios entre páginas
DIA = 86400

log = logging.getLogger("radar")


def preparar_log():
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    archivo = logging.handlers.RotatingFileHandler("radar.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    archivo.setFormatter(fmt)
    consola = logging.StreamHandler(sys.stdout)
    consola.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(archivo)
    log.addHandler(consola)


def huella(titulo):
    return hashlib.md5((titulo or "").encode("utf-8")).hexdigest()[:12]


def leer_enlaces(gh):
    txt = gh.leer(ENLACES, "") if gh else (open(ENLACES, encoding="utf-8").read() if os.path.exists(ENLACES) else "")
    return list(dict.fromkeys(u.strip() for u in txt.splitlines() if u.strip().startswith("http")))


def importar_legado(db, gh):
    """Primera vez: pasa el historial diario de historial.json a precios.db (la memoria de 30 días no empieza en cero)."""
    if db.hay_observaciones():
        return
    try:
        txt = gh.leer(LEGADO[1], None) if gh else (open(LEGADO[1], encoding="utf-8").read() if os.path.exists(LEGADO[1]) else None)
        hist = json.loads(txt) if txt else {}
    except Exception as e:
        return log.warning("No se pudo importar el historial anterior: %s", e)
    n = 0
    for link, dias in hist.items():
        pid = db.asegurar_producto(link)
        for d in dias:
            ts = time.mktime(time.strptime(d["fecha"] + " 12:00", "%Y-%m-%d %H:%M"))
            db.guardar_observacion(pid, {"precio": d["precio"], "fuente": "importado"}, ts=ts)
            n += 1
    if n:
        log.info("Historial anterior importado: %d precios diarios de %d productos", n, len(hist))


def leer_producto(db, sesion, link, R):
    """Lee un enlace, lo guarda y devuelve (pid, lectura, evaluación) o None si falló."""
    try:
        lec = extraer(sesion, link)
    except Exception as e:
        log.warning("  ERROR %s: %s (se conserva su último dato)", link, e)
        return None
    pid = db.guardar_producto(lec)
    ahora = time.time()
    previo = [(o["ts"], o["precio"]) for o in db.historial(pid, ahora - (R["dias_referencia"] + 1) * DIA)]
    if reglas.es_sospechosa(lec["precio"], [p for _, p in previo], R):
        db.guardar_observacion(pid, lec, sospechosa=True)
        log.warning("  lectura sospechosa ($%.0f lejos de lo habitual): se descarta", lec["precio"])
        return None
    db.guardar_observacion(pid, lec)
    ev = reglas.evaluar(lec["precio"], lec["tachado"], previo, ahora, R)
    if previo and reglas.es_baja(lec["precio"], previo[-1][1], R):
        db.guardar_alerta(pid, "baja", previo[-1][1], lec["precio"], ev["referencia_30d"],
                          reglas.pct(previo[-1][1], lec["precio"]), ev["descuento_real_pct"], "baja de precio")
        log.info("  ¡BAJA! $%.0f → $%.0f", previo[-1][1], lec["precio"])
    if db.encolar_ia(pid, huella(lec["titulo"])):
        log.info("  en cola para la IA")
    log.info("  $%.2f | -%d%% %s | %s%s | %s", lec["precio"], ev["descuento_pct"],
             "(real)" if ev["suficiente"] else "(tachado)", lec["fuente"],
             " | cupón" if lec["cupon"] else "", lec["titulo"][:40])
    return pid, lec, ev


def confirmar(db, sesion, candidatos, R):
    """Súper oferta solo si una segunda lectura, minutos después, sostiene el precio."""
    log.info("Confirmando %d posible(s) súper oferta(s) en %d s…", len(candidatos), R["confirmacion_seg"])
    time.sleep(R["confirmacion_seg"])
    for pid, lec, ev in candidatos:
        try:
            nueva = extraer(sesion, lec["link"])
        except Exception as e:
            log.warning("  no se pudo confirmar %s: %s", lec["link"], e)
            continue
        if nueva["precio"] <= lec["precio"] * 1.01:
            db.guardar_observacion(pid, nueva)
            db.guardar_alerta(pid, "super", ev["precio_1h"], nueva["precio"], ev["referencia_30d"], ev["caida_1h_pct"],
                              reglas.pct(ev["referencia_30d"], nueva["precio"]), ev["motivo"])
            log.info("  ★ SÚPER OFERTA confirmada: %s a $%.0f (%s)", lec["titulo"][:40], nueva["precio"], ev["motivo"])
        else:
            log.info("  descartada: %s volvió a $%.0f", lec["titulo"][:40], nueva["precio"])


def vuelta(db, gh, cfg, R, cliente_ia):
    urls = leer_enlaces(gh)
    if not urls:
        return log.info("%s está vacío: nada que rastrear", ENLACES)
    db.sincronizar_activos(urls)
    sesion, candidatos = nueva_sesion(), []
    for u in urls:
        log.info("Rastreando: %s", u)
        res = leer_producto(db, sesion, u, R)
        if res and res[2]["super_deal"]:
            candidatos.append(res)
        time.sleep(random.uniform(*PAUSA))
    if candidatos:
        confirmar(db, sesion, candidatos, R)

    if cliente_ia:
        listos = ia.procesar_cola(db, cliente_ia, cfg["ia_max_por_vuelta"], cfg["ia_minutos_por_vuelta"] * 60, log)
        log.info("IA: %d listo(s), %d pendiente(s)", listos, db.cuenta_pendientes_ia())

    datos, alertas = exportar.construir(db, R, time.time())
    txt_datos, txt_alertas = exportar.a_texto(datos), exportar.a_texto(alertas)
    for nombre, txt in ((DATOS, txt_datos), (ALERTAS, txt_alertas)):  # copia local siempre (respaldo y modo sin GitHub)
        with open(nombre, "w", encoding="utf-8") as f:
            f.write(txt)
    resumen = f"{len(datos['productos'])} ofertas, {len(alertas['alertas'])} súper"
    log.info("Listo: %s → %s y %s (copia local)", resumen, DATOS, ALERTAS)
    if gh:
        subir(gh, {DATOS: txt_datos, ALERTAS: txt_alertas}, f"Precios: {resumen}")
    else:
        log.info("Sin subir a GitHub: falta GITHUB_REPO o GITHUB_TOKEN en %s", config.ARCHIVO)


def subir(gh, archivos, mensaje):
    """Commit directo vía API REST. Un fallo se informa con el error exacto y el radar sigue (se reintenta en la próxima vuelta)."""
    log.info("Subiendo a GitHub (%s, rama %s): %s…", gh.repo, gh.rama, ", ".join(archivos))
    try:
        sha = gh.publicar(archivos, mensaje, borrar=LEGADO)
    except Exception as e:
        log.error("ERROR al subir a GitHub: %s", e)
        if "HTTP 401" in str(e):
            log.error("  → El token no es válido o venció. Genera otro en GitHub (Settings → Developer settings).")
        elif "HTTP 403" in str(e):
            log.error("  → El token no tiene permiso de escritura: dale «Contents: Read and write» sobre %s.", gh.repo)
        elif "HTTP 404" in str(e):
            log.error("  → No se encontró %s o la rama %s, o el token no tiene acceso a ese repositorio.", gh.repo, gh.rama)
        return None
    if sha:
        log.info("Commit exitoso: %s → https://github.com/%s/commit/%s", sha[:7], gh.repo, sha)
    else:
        log.info("Commit exitoso: nada que subir, los archivos en GitHub ya estaban iguales.")
    return sha


def probar_ia(cfg):
    titulo = "Teclado Inalámbrico Mecánico Attack Shark X85 Pro 82 Teclas Teclado RGB con Pantalla TFT 4000mAh"
    cliente = ia.Gemini(cfg["gemini_api_key"], cfg["gemini_modelo"])
    print(f"Clave leída de {cfg['origen_clave']}: {config.ultimos4(cfg['gemini_api_key'])} | modelo: {cfg['gemini_modelo']}")
    for _ in range(4):  # el respaldo de modelo (404) y el cambio de esquema reintentan solos
        try:
            print(json.dumps(cliente.enriquecer(titulo), ensure_ascii=False, indent=2))
            return print(f"La clave de Gemini funciona (modelo {cliente.modelo}).")
        except ia.Saturada as e:
            if e.espera > 5:
                return print(f"Gemini está saturado ahora mismo ({e}). La clave sí respondió; vuelve a probar en un minuto.")
        except Exception as e:
            return print(f"No funcionó: {e.__class__.__name__}: {e}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consolas de Windows en cp1252
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    cfg = config.cargar()
    if "--probar-ia" in sys.argv:
        return probar_ia(cfg)
    preparar_log()
    gh = GitHub(cfg["repo"], cfg["token"], cfg["rama"]) if cfg["repo"] and cfg["token"] else None
    if bool(cfg["repo"]) != bool(cfg["token"]):
        log.warning("Ojo: en %s hay %s pero falta %s; el radar trabajará solo en local.", config.ARCHIVO,
                    *(("GITHUB_REPO", "GITHUB_TOKEN") if cfg["repo"] else ("GITHUB_TOKEN", "GITHUB_REPO")))
    if "--debug" in sys.argv:
        urls = leer_enlaces(gh)
        return diagnostico(nueva_sesion(), urls[0]) if urls else print("enlaces.txt vacío")
    R = reglas.con_ajustes(cfg.get("reglas"))
    cliente_ia = ia.Gemini(cfg["gemini_api_key"], cfg["gemini_modelo"])
    log.info("Modo: %s | IA: %s | cada %d min", f"GitHub {gh.repo}" if gh else "local",
             f"{cfg['gemini_modelo']} (clave de {cfg['origen_clave']}: {config.ultimos4(cfg['gemini_api_key'])})",
             cfg["intervalo_min"])
    db = DB(BASE)
    importar_legado(db, gh)
    if "--loop" not in sys.argv:
        return vuelta(db, gh, cfg, R, cliente_ia)
    while True:
        inicio = time.time()
        log.info("=== Vuelta %s ===", time.strftime("%Y-%m-%d %H:%M"))
        try:
            vuelta(db, gh, cfg, R, cliente_ia)
        except Exception as e:  # una caída de red o de GitHub no debe tumbar el radar 24/7
            log.exception("FALLÓ la vuelta: %s", e)
        espera = max(60, cfg["intervalo_min"] * 60 - (time.time() - inicio))
        log.info("Próxima vuelta en %.0f min", espera / 60)
        time.sleep(espera)


if __name__ == "__main__":
    main()