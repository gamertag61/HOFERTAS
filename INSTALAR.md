# Instalar Heleos (sin depender de la laptop principal)

```
 Cockpit (dashboard.html) ──escribe enlaces.txt──▶  GitHub (repositorio)  ◀──lee enlaces.txt── Radar (laptop viejita, 24/7)
 Catálogo (index.html)    ◀──lee ofertas.json────  + GitHub Pages        ◀──publica ofertas.json + historial.json──┘
```

- **GitHub Pages** sirve el catálogo y el Cockpit gratis y siempre encendidos.
- **El radar** es lo único que corre en tu casa: en la laptop viejita (4 GB), solo `requests` + `BeautifulSoup`.
- **Tu laptop principal** ya no hace falta encendida.

## 1. Repositorio y GitHub Pages (una sola vez)

1. En github.com crea un repositorio **público** llamado `HOFERTAS` (sin README) — hecho.
2. Sube esta carpeta (Claude deja el commit listo; `git push` te pedirá iniciar sesión en GitHub).
3. En el repositorio: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)` → Save**.
4. En 1–2 minutos quedan en línea:
   - Catálogo: `https://gamertag61.github.io/HOFERTAS/`
   - Cockpit: `https://gamertag61.github.io/HOFERTAS/dashboard.html`

## 2. Token de GitHub (lo creas tú)

GitHub → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**:

- Repository access: **Only select repositories → `HOFERTAS`**.
- Permissions → Repository → **Contents: Read and write** (nada más).
- Expiración: la que prefieras (cuando venza, crea otro y cámbialo en los dos lugares de abajo).

Ese token se usa en el radar y en el Cockpit. No lo subas al repositorio ni lo compartas.

## 3. Radar en la laptop viejita

1. Instala Python 3 (python.org, marca "Add python.exe to PATH").
2. En una terminal: `pip install requests beautifulsoup4`
3. Copia a una carpeta (p. ej. `C:\Heleos`): `heleos_radar.py`, `iniciar_radar.bat` y `heleos_config.ejemplo.json`.
4. Renombra `heleos_config.ejemplo.json` a `heleos_config.json` y llena `repo` (`gamertag61/HOFERTAS`) y `token`.
   `intervalo_min` = minutos entre vueltas (180 = cada 3 horas; mínimo 15).
5. Doble clic en `iniciar_radar.bat`. Debe decir `Modo: GitHub gamertag61/HOFERTAS` y al final `publicado en GitHub`.
6. Para que arranque solo: `Win + R` → `shell:startup` → pega ahí un acceso directo a `iniciar_radar.bat`.
7. Configura Windows para que la laptop no se suspenda (Configuración → Energía → Suspender: Nunca).

## 4. Cockpit

Abre `https://gamertag61.github.io/HOFERTAS/dashboard.html`, toca el ícono de enlace junto al contador de la Caja de municiones,
pega tu token y presiona **Conectar** (el repositorio se detecta solo). Desde ahí, **Guardar Enlaces** escribe en el `enlaces.txt`
del repositorio y el radar los rastrea en su siguiente vuelta.

## Probar en la laptop principal (opcional)

`python -m http.server 8765` → `http://localhost:8765/` y `http://localhost:8765/dashboard.html`.
Sin `heleos_config.json`, `python heleos_radar.py` trabaja con los archivos locales.
