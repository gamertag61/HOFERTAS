"""Configuración: todo sale de heleos_config.json (fuera de git). Cero claves en el código.

La clave de Gemini se lee SOLO del archivo, con el nombre "GEMINI_API_KEY" (también se acepta "gemini_api_key").
Las variables de entorno de Windows se ignoran para la clave de Gemini, para que nunca se use una clave
distinta a la del archivo sin que lo notes.
"""
import json
import os
import sys

ARCHIVO = "heleos_config.json"

DEFECTOS = {
    "repo": "",
    "token": "",
    "rama": "main",
    "intervalo_min": 30,
    "gemini_modelo": "gemini-2.5-flash",
    "ia_max_por_vuelta": 12,      # productos que la IA procesa como máximo en cada vuelta
    "ia_minutos_por_vuelta": 6,   # tiempo máximo (con esperas incluidas) que la IA usa por vuelta
    "reglas": {},                 # umbrales anti-fraude que quieras cambiar (ver radar/reglas.py)
}

ENTORNO = {"HELEOS_REPO": "repo", "HELEOS_TOKEN": "token"}  # solo GitHub; Gemini sale únicamente del archivo
# Nombres aceptados en el archivo para los datos de GitHub (el primero que tenga valor gana)
ALIAS = {"repo": ("repo", "GITHUB_REPO", "HELEOS_REPO"), "token": ("token", "GITHUB_TOKEN", "HELEOS_TOKEN")}


def limpiar_repo(repo):
    """Acepta "usuario/repo" o la URL completa (https://github.com/usuario/repo.git)."""
    repo = str(repo or "").strip().rstrip("/")
    if "github.com/" in repo:
        repo = repo.split("github.com/", 1)[1]
    return repo[:-4] if repo.endswith(".git") else repo


def cargar(ruta=ARCHIVO):
    cfg = dict(DEFECTOS)
    try:
        # utf-8-sig: el Bloc de notas a veces guarda con BOM
        with open(ruta, encoding="utf-8-sig") as f:
            archivo = json.load(f)
    except FileNotFoundError:
        sys.exit(f"Error: No se encontró {ruta} en {os.getcwd()}")
    except json.JSONDecodeError as e:
        sys.exit(f"Error: {ruta} tiene un error de formato en la línea {e.lineno}: {e.msg}. "
                 "Revisa comas y comillas (ver heleos_config.ejemplo.json).")
    cfg.update({k: v for k, v in archivo.items() if k not in ("GEMINI_API_KEY", "gemini_api_key")})
    for clave, nombres in ALIAS.items():
        cfg[clave] = next((str(archivo[n]).strip() for n in nombres if str(archivo.get(n) or "").strip()), "")
    for var, clave in ENTORNO.items():
        if os.environ.get(var) and not cfg.get(clave):
            cfg[clave] = os.environ[var].strip()
    for clave in ("token",):
        if str(cfg.get(clave, "")).startswith("PEGA_AQUI"):
            cfg[clave] = ""
    cfg["repo"] = limpiar_repo(cfg["repo"])

    clave =str(archivo.get("GEMINI_API_KEY") or archivo.get("gemini_api_key") or "").strip()
    if not clave or clave.startswith("PEGA_AQUI"):
        sys.exit(f"Error: No se encontró la clave en {ruta}")
    cfg["gemini_api_key"] = clave
    cfg["intervalo_min"] = max(15, int(cfg.get("intervalo_min") or 30))
    return cfg


def ultimos4(secreto):
    """Solo los últimos 4 caracteres, para confirmar qué clave se leyó sin mostrarla."""
    return "…" + secreto[-4:] if secreto else "(vacía)"
