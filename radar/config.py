"""Configuración. Cero claves en el código.

Clave de Gemini: variable de entorno GEMINI_API_KEY (GitHub Actions la inyecta desde GitHub Secrets). Si no existe,
se usa "GEMINI_API_KEY" de heleos_config.json (para correr en una laptop). Si no está en ninguno, el script se detiene.
heleos_config.json es opcional (no existe en GitHub Actions) y nunca se sube a git.
GitHub: "repo"/"token" (o GITHUB_REPO/GITHUB_TOKEN) del archivo; si faltan, las variables de entorno
GITHUB_REPOSITORY (la pone Actions), GITHUB_REPO, HELEOS_REPO y GITHUB_TOKEN, HELEOS_TOKEN.
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

ENTORNO = {"repo": ("GITHUB_REPOSITORY", "GITHUB_REPO", "HELEOS_REPO"), "token": ("GITHUB_TOKEN", "HELEOS_TOKEN")}
# Nombres aceptados en el archivo para los datos de GitHub (el primero que tenga valor gana)
ALIAS = {"repo": ("repo", "GITHUB_REPO", "HELEOS_REPO"), "token": ("token", "GITHUB_TOKEN", "HELEOS_TOKEN")}


def limpiar_repo(repo):
    """Acepta "usuario/repo" o la URL completa (https://github.com/usuario/repo.git)."""
    repo = str(repo or "").strip().rstrip("/")
    if "github.com/" in repo:
        repo = repo.split("github.com/", 1)[1]
    return repo[:-4] if repo.endswith(".git") else repo


def valida(valor):
    v = str(valor or "").strip()
    return "" if v.startswith("PEGA_AQUI") else v


def cargar(ruta=ARCHIVO):
    cfg, archivo = dict(DEFECTOS), {}
    try:
        # utf-8-sig: el Bloc de notas a veces guarda con BOM
        with open(ruta, encoding="utf-8-sig") as f:
            archivo = json.load(f)
    except FileNotFoundError:
        pass  # normal en GitHub Actions: todo llega por variables de entorno
    except json.JSONDecodeError as e:
        sys.exit(f"Error: {ruta} tiene un error de formato en la línea {e.lineno}: {e.msg}. "
                 "Revisa comas y comillas (ver heleos_config.ejemplo.json).")
    cfg.update({k: v for k, v in archivo.items() if k not in ("GEMINI_API_KEY", "gemini_api_key")})
    for clave, nombres in ALIAS.items():
        cfg[clave] = next((valida(archivo[n]) for n in nombres if valida(archivo.get(n))), "")
        if not cfg[clave]:
            cfg[clave] = next((valida(os.environ[v]) for v in ENTORNO[clave] if valida(os.environ.get(v))), "")
    cfg["repo"] = limpiar_repo(cfg["repo"])

    clave, origen = valida(os.environ.get("GEMINI_API_KEY")), "variable de entorno GEMINI_API_KEY"
    if not clave:
        clave, origen = valida(archivo.get("GEMINI_API_KEY") or archivo.get("gemini_api_key")), ruta
    if not clave:
        sys.exit("Error: falta la clave de Gemini. Defínela en la variable de entorno GEMINI_API_KEY "
                 f"(en GitHub Actions: Settings > Secrets and variables > Actions) o en {ruta}.")
    cfg["gemini_api_key"], cfg["origen_clave"] = clave, origen
    cfg["intervalo_min"] = max(15, int(cfg.get("intervalo_min") or 30))
    return cfg


def ultimos4(secreto):
    """Solo los últimos 4 caracteres, para confirmar qué clave se leyó sin mostrarla."""
    return "…" + secreto[-4:] if secreto else "(vacía)"
