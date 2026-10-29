"""Director de compras: mira el catálogo (datos.json), cuenta categorías y le pide a Gemini 3 misiones de inventario.

Requiere:  pip install requests
Uso:       python heleos_asesor.py           genera misiones.json y lo sube a GitHub (rama main)
           python heleos_asesor.py --local   solo genera misiones.json, sin subir

Usa las mismas claves que el radar, desde heleos_config.json (GEMINI_API_KEY y GITHUB_REPO + GITHUB_TOKEN).
No hay ninguna clave escrita en el código. Si Gemini falla, misiones.json no se toca: las misiones anteriores siguen.
"""
import collections
import json
import os
import sys
import time

from radar import config, ia
from radar.github import GitHub

DATOS, MISIONES = "datos.json", "misiones.json"
NICHO = "PC Gamer"
INTENTOS = 6

PROMPT = """Este es mi catálogo actual. Mi nicho es {nicho}. Sugiéreme 3 tipos de accesorios o componentes que faltan para equilibrar el catálogo.

Productos por categoría:
{conteo}

Productos que ya tengo:
{productos}

Reglas:
- "sugerencia": tipo de producto concreto y fácil de buscar en Mercado Libre, de 2 a 5 palabras (ej. "Mousepad RGB XL"). No repitas algo que ya tengo.
- "motivo": una frase corta en español de México que explique qué hueco del catálogo llena (máx. 90 caracteres).
- Exactamente 3 elementos."""

ESQUEMA = {
    "type": "array",
    "minItems": 3,
    "maxItems": 3,
    "items": {
        "type": "object",
        "properties": {
            "sugerencia": {"type": "string", "description": "Tipo de producto, 2 a 5 palabras"},
            "motivo": {"type": "string", "description": "Por qué equilibra el catálogo"},
        },
        "required": ["sugerencia", "motivo"],
    },
}


def leer_catalogo(gh):
    """datos.json local; si no está (laptop principal), el que el radar publicó en GitHub."""
    if os.path.exists(DATOS):
        with open(DATOS, encoding="utf-8") as f:
            return json.load(f)
    if gh:
        print(f"No hay {DATOS} local; se lee el de GitHub ({gh.repo}).")
        txt = gh.leer(DATOS)
        if txt:
            return json.loads(txt)
    sys.exit(f"Error: No se encontró {DATOS}. Corre primero el radar (python heleos_radar.py).")


def contar(catalogo):
    productos = catalogo.get("productos") or []
    nombres = {c["id"]: c["nombre"] for c in catalogo.get("categorias") or []}
    conteo = collections.Counter(nombres.get(p.get("categoria"), p.get("categoria") or "Sin categoría") for p in productos)
    return conteo, [p.get("nombre") or p.get("titulo") or "" for p in productos]


def validar(d):
    if not isinstance(d, list):
        raise ValueError("la respuesta no es una lista")
    misiones = []
    for m in d:
        sug = " ".join(str((m or {}).get("sugerencia") or "").split())[:60]
        mot = " ".join(str((m or {}).get("motivo") or "").split())[:140]
        if sug and mot:
            misiones.append({"sugerencia": sug, "motivo": mot})
    if len(misiones) < 3:
        raise ValueError(f"vinieron {len(misiones)} misiones válidas, se esperaban 3")
    return misiones[:3]


def pedir_misiones(cliente, texto):
    """Reintenta saturación (429/5xx) y cambio de modelo; cuota diaria o clave inválida detienen el script."""
    for intento in range(1, INTENTOS + 1):
        try:
            return validar(cliente.generar(texto, ESQUEMA, temperatura=0.6, max_tokens=1024))
        except ia.Saturada as e:
            espera = min(e.espera, 90)
            print(f"  Gemini ocupado ({e}); reintento {intento}/{INTENTOS} en {espera:.0f} s…")
            time.sleep(espera)
        except ValueError as e:
            print(f"  Respuesta con formato inválido ({e}); reintento {intento}/{INTENTOS}…")
            time.sleep(3)
        except ia.CuotaDiaria as e:
            sys.exit(f"Error: se acabó la cuota diaria de Gemini ({e}). Vuelve a intentarlo mañana.")
        except ia.ClaveInvalida as e:
            sys.exit(f"Error: Gemini rechazó la clave o el modelo ({e}).")
    sys.exit(f"Error: Gemini no respondió después de {INTENTOS} intentos. {MISIONES} no se modificó.")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consolas de Windows en cp1252
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    cfg = config.cargar()
    local = "--local" in sys.argv
    gh = GitHub(cfg["repo"], cfg["token"], cfg["rama"]) if cfg["repo"] and cfg["token"] else None
    if not gh and not local:
        print(f"Aviso: falta GITHUB_REPO o GITHUB_TOKEN en {config.ARCHIVO}; {MISIONES} solo se guardará en local.")

    catalogo = leer_catalogo(gh)
    conteo, productos = contar(catalogo)
    print(f"Catálogo: {len(productos)} productos en {len(conteo)} categorías")
    for cat, n in conteo.most_common():
        print(f"  {cat:<14} {n}")

    cliente = ia.Gemini(cfg["gemini_api_key"], cfg["gemini_modelo"])
    print(f"Consultando a Gemini ({cfg['gemini_modelo']}, clave {config.ultimos4(cfg['gemini_api_key'])})…")
    texto = PROMPT.format(nicho=NICHO, conteo="\n".join(f"- {c}: {n}" for c, n in conteo.most_common()),
                          productos="\n".join(f"- {p}" for p in productos if p))
    misiones = pedir_misiones(cliente, texto)

    salida = {
        "version": 1,
        "generado": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "modelo": cliente.modelo,
        "nicho": NICHO,
        "catalogo": [{"categoria": c, "total": n} for c, n in conteo.most_common()],
        "misiones": misiones,
    }
    txt = json.dumps(salida, ensure_ascii=False, indent=2) + "\n"
    with open(MISIONES, "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"Misiones guardadas en {MISIONES} (modelo {cliente.modelo}):")
    for i, m in enumerate(misiones, 1):
        print(f"  {i}. {m['sugerencia']} — {m['motivo']}")

    if gh and not local:
        print(f"Subiendo a GitHub ({gh.repo}, rama {gh.rama}): {MISIONES}…")
        try:
            sha = gh.publicar({MISIONES: txt}, f"Misiones de inventario: {', '.join(m['sugerencia'] for m in misiones)}")
        except Exception as e:
            sys.exit(f"ERROR al subir a GitHub: {e}")
        print(f"Commit exitoso: {sha[:7]} → https://github.com/{gh.repo}/commit/{sha}" if sha
              else "Commit exitoso: nada que subir, misiones.json en GitHub ya era igual.")


if __name__ == "__main__":
    main()
