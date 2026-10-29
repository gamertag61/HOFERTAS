"""Limpieza con IA (Gemini por REST, solo requests) y cola de reintentos que nunca frena los precios.

Cada producto tiene SIEMPRE datos: mientras la IA no lo procese, se usa `respaldo()` (reglas locales).
Si Gemini se satura, se espera y se reintenta; si se acaba el tiempo de la vuelta o la cuota del día,
el producto queda reprogramado en precios.db y se retoma en la siguiente vuelta.
"""
import datetime
import json
import random
import re
import time

import requests

URL = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
CATEGORIAS = ["Teclados", "Mouse", "Monitores", "Audio", "Escritorios", "Sillas", "Iluminación",
              "Componentes", "Controles", "Accesorios"]
MAX_NOMBRE = 48
ESPERA_MAX = 900  # 15 min

# Ícono SVG que dibuja la web para cada spec (la web no usa emoji); el emoji queda para la app y TikTok.
ICONOS = [
    (r"\bhz\b|refresco", "rayo", "⚡"),
    (r'pulgada|"|”|pantalla|resoluci|full hd|qhd|4k|ips', "pantalla", "🖥️"),
    (r"\bms\b|respuesta|latencia", "reloj", "⏱️"),
    (r"inal[aá]mbric|bluetooth|wi-?fi|2\.4\s?g", "wifi", "📶"),
    (r"al[aá]mbric|usb|cable", "cable", "🔌"),
    (r"mec[aá]nic|magn[eé]tic|tecla|switch|hot-?swap", "tecla", "⌨️"),
    (r"rgb|led|luz|luces|ilumina", "luz", "💡"),
    (r"mah|bater[ií]a|horas|recargable", "bateria", "🔋"),
    (r"\bgb\b|\btb\b|ssd|memoria|n[uú]cleo|core|ghz|hilos", "disco", "💾"),
    (r"\banc\b|cancelaci|sonido|audio|driver|bocina|subwoofer|\bw\b|watts", "audio", "🎧"),
]
REGLAS_SPECS = [
    (r"(\d{2,3})\s?hz", lambda m: f"{m[1]} Hz"),
    (r"(\d{2}(?:[.,]\d)?)\s?(?:\"|”|''|pulgadas|pulg\b)", lambda m: f'{m[1].replace(",", ".")}"'),
    (r"\b(\d(?:\.\d)?)\s?ms\b", lambda m: f"{m[1]} ms"),
    (r"inal[aá]mbric|bluetooth|wireless|\bbt\b", lambda m: "Inalámbrico"),
    (r"(?<!in)al[aá]mbric|(?<!-)\bwired\b", lambda m: "Alámbrico"),
    (r"mec[aá]nic|magn[eé]tic", lambda m: "Magnético" if re.match(r"magn", m[0], re.I) else "Mecánico"),
    (r"cancelaci[oó]n|\banc\b", lambda m: "ANC"),
    (r"(\d{3,5})\s?mah", lambda m: f"{m[1]} mAh"),
    (r"(\d{2,4})\s?(gb|tb)\b", lambda m: f"{m[1]} {m[2].upper()}"),
    (r"\brgb\b", lambda m: "RGB"),
]
CAT_PALABRAS = [  # el orden importa: "Lámpara de escritorio" es Iluminación, "Silla de escritorio" es Sillas
    ("Teclados", r"teclado"), ("Mouse", r"\bmouse\b|rat[oó]n"), ("Monitores", r"monitor"),
    ("Audio", r"aud[ií]fono|bocina|altavoz|headset|diadema|soundbar"), ("Sillas", r"\bsilla"),
    ("Iluminación", r"l[aá]mpara|\bfoco"), ("Componentes", r"procesador|ryzen|intel core|\bram\b|\bssd\b|tarjeta de video|gpu|motherboard"),
    ("Controles", r"\bcontrol\b|\bmando\b|gamepad|joystick"), ("Escritorios", r"escritorio|\bmesa"),
]

ESQUEMA = {
    "type": "object",
    "properties": {
        "nombre": {"type": "string", "description": f"Nombre comercial corto, máximo {MAX_NOMBRE} caracteres"},
        "categoria": {"type": "string", "enum": CATEGORIAS},
        "specs": {"type": "array", "minItems": 3, "maxItems": 3, "items": {
            "type": "object",
            "properties": {"emoji": {"type": "string"}, "texto": {"type": "string"}},
            "required": ["emoji", "texto"]}},
    },
    "required": ["nombre", "categoria", "specs"],
}

PROMPT = """Eres editor de una tienda de ofertas de tecnología en México. A partir del título de Mercado Libre,
devuelve:
- "nombre": nombre comercial limpio y corto en español (máximo {max} caracteres): tipo de producto + marca + modelo.
  Sin colores, medidas de empaque, compatibilidades largas ni palabras de relleno.
- "categoria": una sola de esta lista: {cats}.
- "specs": exactamente 3 especificaciones técnicas clave, cada una muy breve (máximo 18 caracteres, ej. "165 Hz",
  "Inalámbrico", "4000 mAh") con un emoji representativo. Solo datos que estén en el título; no inventes.

Título: {titulo}"""


class Saturada(Exception):
    """429 por minuto, 5xx o red: esperar `espera` segundos y reintentar."""
    def __init__(self, msg, espera):
        super().__init__(msg)
        self.espera = espera


class CuotaDiaria(Exception):
    """Se acabó la cuota del día: pausar la IA hasta mañana (los precios siguen)."""


class ClaveInvalida(Exception):
    """Clave o modelo mal configurados: no tiene caso reintentar enseguida."""


def icono_de(texto):
    for regex, icono, emoji in ICONOS:
        if re.search(regex, texto, re.I):
            return icono, emoji
    return "etiqueta", "🏷️"


# ---------- Respaldo local (sin IA) ----------
def nombre_respaldo(titulo):
    pal, out = re.split(r"[,|(–]| - ", titulo)[0].strip().split(), []
    for w in pal:
        if len(out) >= 3 and re.fullmatch(r"(con|para|de|del|y|sin|rgb|led|\d+(\.\d+)?)", w, re.I):
            break
        out.append(w)
        if len(out) == 6:
            break
    return re.sub(r"\s+(en|de|del|con|para|y|la|el)$", "", " ".join(out), flags=re.I)


def categoria_respaldo(titulo):
    for cat, regex in CAT_PALABRAS:
        if re.search(regex, titulo, re.I):
            return cat
    return "Accesorios"


def specs_respaldo(titulo):
    out = []
    for regex, f in REGLAS_SPECS:
        m = re.search(regex, titulo, re.I)
        if m:
            out.append(f(m))
        if len(out) == 3:
            break
    return [{"texto": t, "emoji": icono_de(t)[1], "icono": icono_de(t)[0]} for t in out]


def respaldo(titulo):
    return {"nombre": nombre_respaldo(titulo), "categoria": categoria_respaldo(titulo),
            "specs": specs_respaldo(titulo), "fuente": "reglas"}


# ---------- Gemini ----------
def validar(d):
    """Lanza ValueError si la IA no respetó el formato; normaliza lo demás."""
    if not isinstance(d, dict):
        raise ValueError("la respuesta no es un objeto")
    nombre = re.sub(r"\s+", " ", str(d.get("nombre") or "")).strip()
    if not 3 <= len(nombre) <= MAX_NOMBRE + 12:
        raise ValueError(f"nombre inválido: {nombre!r}")
    if len(nombre) > MAX_NOMBRE:
        nombre = nombre[:MAX_NOMBRE].rsplit(" ", 1)[0]
    cat = d.get("categoria")
    if cat not in CATEGORIAS:
        raise ValueError(f"categoría fuera de la lista: {cat!r}")
    specs = d.get("specs")
    if not isinstance(specs, list) or len(specs) != 3:
        raise ValueError("no vinieron exactamente 3 specs")
    limpias = []
    for s in specs:
        texto = re.sub(r"\s+", " ", str((s or {}).get("texto") or "")).strip()[:24]
        if not texto:
            raise ValueError("spec vacía")
        icono, emoji_defecto = icono_de(texto)
        limpias.append({"texto": texto, "emoji": str(s.get("emoji") or emoji_defecto).strip()[:4], "icono": icono})
    return {"nombre": nombre, "categoria": cat, "specs": limpias, "fuente": "ia"}


def _segundos(txt):
    m = re.match(r"([\d.]+)s", str(txt or ""))
    return float(m.group(1)) if m else None


class Gemini:
    def __init__(self, clave, modelo, sesion=None, url=URL):
        self.clave, self.modelo, self.url = clave, modelo, url.format(modelo=modelo)
        self.s = sesion or requests.Session()
        self.esquema_legado = False  # por si el modelo solo acepta el formato anterior "responseSchema"

    def _cuerpo(self, titulo):
        gen = {"responseMimeType": "application/json", "temperature": 0.2, "maxOutputTokens": 512}
        if self.esquema_legado:
            gen["responseSchema"] = _a_legado(ESQUEMA)
        else:
            gen["responseJsonSchema"] = ESQUEMA
        texto = PROMPT.format(max=MAX_NOMBRE, cats=", ".join(CATEGORIAS), titulo=titulo)
        return {"contents": [{"role": "user", "parts": [{"text": texto}]}], "generationConfig": gen}

    def enriquecer(self, titulo):
        try:
            r = self.s.post(self.url, headers={"x-goog-api-key": self.clave}, json=self._cuerpo(titulo), timeout=60)
        except requests.RequestException as e:
            raise Saturada(f"red: {e.__class__.__name__}", 30)
        if r.status_code == 200:
            try:
                d = r.json()
                texto = d["candidates"][0]["content"]["parts"][0]["text"]
                return validar(json.loads(texto))
            except (KeyError, IndexError, ValueError, TypeError) as e:
                raise Saturada(f"respuesta inválida: {e}", 10)
        err = {}
        try:
            err = r.json().get("error", {})
        except ValueError:
            pass
        msg = f"HTTP {r.status_code} {err.get('status', '')}: {str(err.get('message', r.text))[:160]}"
        detalles = err.get("details") or []
        espera = next((_segundos(x.get("retryDelay")) for x in detalles if "RetryInfo" in x.get("@type", "")), None)
        cuotas = " ".join(v.get("quotaId", "") for x in detalles for v in x.get("violations", []) or [])
        if r.status_code == 429:
            if "PerDay" in cuotas:
                raise CuotaDiaria(msg)
            raise Saturada(msg, espera or 30)
        if r.status_code in (500, 502, 503, 504):
            raise Saturada(msg, espera or 20)
        if r.status_code == 400 and not self.esquema_legado and "responseJsonSchema" in msg:
            self.esquema_legado = True
            raise Saturada("el modelo pide el esquema anterior; se reintenta", 1)
        if r.status_code in (400, 401, 403, 404):
            raise ClaveInvalida(msg)
        raise Saturada(msg, espera or 60)


def _a_legado(esq):
    """Convierte el JSON Schema al formato "responseSchema" (tipos en mayúsculas)."""
    out = {}
    for k, v in esq.items():
        if k == "type":
            out[k] = v.upper()
        elif k == "properties":
            out[k] = {p: _a_legado(s) for p, s in v.items()}
        elif k == "items":
            out[k] = _a_legado(v)
        else:
            out[k] = v
    return out


def manana(ahora):
    d = datetime.datetime.fromtimestamp(ahora) + datetime.timedelta(days=1)
    return d.replace(hour=0, minute=5, second=0, microsecond=0).timestamp()


def procesar_cola(db, cliente, max_items, segundos, log, reloj=time.time, dormir=time.sleep):
    """Procesa productos pendientes. Nunca lanza excepciones; devuelve cuántos quedaron listos."""
    if not cliente:
        return 0
    inicio, listos = reloj(), 0
    for fila in db.pendientes_ia(reloj(), max_items):
        intento = fila["intentos"]
        while True:
            restante = segundos - (reloj() - inicio)
            try:
                datos = cliente.enriquecer(fila["titulo"])
                db.ia_ok(fila["producto_id"], datos, json.dumps(datos["specs"], ensure_ascii=False), cliente.modelo)
                listos += 1
                log.info("  IA ✓ %s → %s (%s)", fila["titulo"][:40], datos["nombre"], datos["categoria"])
                break
            except Saturada as e:
                espera = min(ESPERA_MAX, max(e.espera, 5 * 2 ** min(intento, 8)) + random.uniform(0, 3))
                intento += 1
                if espera < restante:
                    log.info("  IA saturada (%s). Reintento en %.0f s", e, espera)
                    dormir(espera)
                    continue
                db.ia_reprogramar(fila["producto_id"], reloj() + espera, e)
                log.info("  IA saturada; se retoma en la próxima vuelta (%s)", e)
                return listos
            except CuotaDiaria as e:
                db.ia_pausar_todos(manana(reloj()), e)
                log.warning("  IA: se acabó la cuota del día. Se reanuda mañana; los precios siguen. (%s)", e)
                return listos
            except ClaveInvalida as e:
                db.ia_pausar_todos(reloj() + 6 * 3600, e)
                log.error("  IA: clave o modelo inválidos (%s). Revisa gemini_api_key y gemini_modelo. "
                          "Se reintenta en 6 h; mientras, se usan nombres de respaldo.", e)
                return listos
            except Exception as e:  # cualquier sorpresa: reprogramar, nunca tumbar el radar
                db.ia_reprogramar(fila["producto_id"], reloj() + 600, e)
                log.warning("  IA: error inesperado con %s: %s", fila["titulo"][:40], e)
                break
    return listos
