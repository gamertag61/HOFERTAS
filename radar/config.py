"""Configuración: heleos_config.json (fuera de git) y, si existen, variables de entorno.

Las claves nunca van en el código. Prioridad: variable de entorno > heleos_config.json > valor por defecto.
"""
import json
import os

ARCHIVO = "heleos_config.json"

DEFECTOS = {
    "repo": "",
    "token": "",
    "rama": "main",
    "intervalo_min": 30,
    "gemini_api_key": "",
    "gemini_modelo": "gemini-3.1-flash-lite",
    "ia_max_por_vuelta": 12,      # productos que la IA procesa como máximo en cada vuelta
    "ia_minutos_por_vuelta": 6,   # tiempo máximo (con esperas incluidas) que la IA usa por vuelta
    "reglas": {},                 # umbrales anti-fraude que quieras cambiar (ver radar/reglas.py)
}

ENTORNO = {"HELEOS_REPO": "repo", "HELEOS_TOKEN": "token", "GEMINI_API_KEY": "gemini_api_key"}


def cargar(ruta=ARCHIVO):
    cfg = dict(DEFECTOS)
    try:
        # utf-8-sig: el Bloc de notas a veces guarda con BOM
        with open(ruta, encoding="utf-8-sig") as f:
            cfg.update(json.load(f))
    except FileNotFoundError:
        pass
    except json.JSONDecodeError as e:
        raise SystemExit(f"{ruta} tiene un error de formato en la línea {e.lineno}: {e.msg}. "
                         "Revisa comas y comillas (ver heleos_config.ejemplo.json).")
    for var, clave in ENTORNO.items():
        if os.environ.get(var):
            cfg[clave] = os.environ[var].strip()
    for clave in ("token", "gemini_api_key"):
        if str(cfg.get(clave, "")).startswith("PEGA_AQUI"):
            cfg[clave] = ""
    cfg["intervalo_min"] = max(15, int(cfg.get("intervalo_min") or 30))
    return cfg


def oculto(secreto):
    """Muestra una clave sin revelarla (para los mensajes del radar)."""
    if not secreto:
        return "(sin configurar)"
    return secreto[:4] + "…" + secreto[-4:] if len(secreto) > 12 else "…"
