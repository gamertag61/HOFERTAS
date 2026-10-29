# Instalar el sistema (sin depender de la laptop principal)

```
 Panel (dashboard.html) ──escribe enlaces.txt──▶  GitHub (repositorio)  ◀──lee enlaces.txt──── Radar (laptop viejita, 24/7)
 Sitio, panel y app      ◀──leen datos.json─────  + GitHub Pages        ◀──publica datos.json + alertas.json──┘
                                                                          precios.db (memoria de 30 días) se queda en la laptop
```

- **GitHub Pages** sirve el sitio, el panel y la app gratis y siempre encendidos.
- **El radar** es lo único que corre en tu casa: en la laptop viejita (4 GB), solo `requests` + `BeautifulSoup`.
- **Tu laptop principal** ya no hace falta encendida.

## 1. Repositorio y GitHub Pages (una sola vez)

1. Repositorio **público** `gamertag61/HOFERTAS` — hecho.
2. En el repositorio: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)` → Save**.
3. En 1–2 minutos quedan en línea:
   - Sitio: `https://gamertag61.github.io/HOFERTAS/`
   - Panel: `https://gamertag61.github.io/HOFERTAS/dashboard.html`
   - App del creador: `https://gamertag61.github.io/HOFERTAS/app.html`

## 2. Tus claves (token de GitHub y clave de Gemini)

### 2.1 Crear o revisar cada clave

**Token de GitHub** — GitHub → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**:
- Repository access: **Only select repositories → `HOFERTAS`**.
- Permissions → Repository → **Contents: Read and write** (nada más).
- Expiración: la que prefieras (cuando venza, crea otro y cámbialo en `heleos_config.json` y en el panel).

**Clave de Gemini** — en **Google AI Studio → Get API key** (https://aistudio.google.com/apikey).
Usa una clave de un proyecto dedicado a esto. El radar pide `gemini_modelo` (por defecto `gemini-2.5-flash`); si ese modelo
no está disponible para tu clave, prueba solo `gemini-3.1-flash-lite` y luego `gemini-2.5-flash-lite`.

### 2.2 Guardarlas en la laptop del radar (nunca en el código)

1. Copia a una carpeta, p. ej. `C:\Radar`: `heleos_radar.py`, la carpeta `radar\`, `iniciar_radar.bat`
   y `heleos_config.ejemplo.json`.
2. En esa carpeta, copia `heleos_config.ejemplo.json` y renombra la copia a **`heleos_config.json`**
   (en el Explorador activa **Vista → Mostrar → Extensiones de nombre de archivo** para no terminar con `heleos_config.json.txt`).
3. Ábrelo con el Bloc de notas y reemplaza solo los textos entre comillas:
   ```json
   {
     "repo": "gamertag61/HOFERTAS",
     "token": "github_pat_11ABC…",
     "rama": "main",
     "GEMINI_API_KEY": "tu-clave-de-gemini",
     "gemini_modelo": "gemini-2.5-flash",
     "intervalo_min": 30,
     "ia_max_por_vuelta": 12,
     "ia_minutos_por_vuelta": 6,
     "reglas": {}
   }
   ```
   - Pega cada clave completa, sin espacios antes ni después, dentro de las comillas.
   - No borres comas ni llaves. Guarda con **Archivo → Guardar** (codificación UTF-8).
4. Comprueba Gemini: abre una terminal en la carpeta y corre `python heleos_radar.py --probar-ia`.
   La primera línea muestra los últimos 4 caracteres de la clave que leyó del archivo (deben coincidir con la tuya);
   al final debe decir **"La clave de Gemini funciona"**. Si falta `GEMINI_API_KEY`, el radar se detiene con
   `Error: No se encontró la clave en heleos_config.json`.
5. Protege el archivo (opcional, recomendado): clic derecho en `heleos_config.json` → **Propiedades → Seguridad**
   y deja con acceso solo a tu usuario.
6. **Borra el .txt donde tenías las claves** (y vacía la Papelera). Desde ahora viven solo en `heleos_config.json`.

Reglas de oro:
- `heleos_config.json` está en `.gitignore`: **nunca lo subas** al repositorio ni lo mandes por chat o correo.
- El radar nunca imprime las claves completas (solo los últimos 4 caracteres).
- Si una clave se filtra: revócala (GitHub → Tokens / AI Studio → borrar clave), crea otra y pégala en `heleos_config.json`.

**La clave de Gemini solo se lee de `heleos_config.json`**: las variables de entorno de Windows se ignoran para ella.
(Para GitHub también se aceptan los nombres `GITHUB_REPO` / `GITHUB_TOKEN` en el archivo, y el repo puede ir como URL completa. Las variables de entorno `HELEOS_TOKEN` y `HELEOS_REPO` solo se usan si el archivo no trae ninguno. En cada vuelta la consola muestra "Subiendo a GitHub…" y luego "Commit exitoso" o el error exacto.)

## 3. Radar en la laptop viejita

1. Instala Python 3 (python.org, marca "Add python.exe to PATH").
2. En una terminal: `pip install requests beautifulsoup4`
3. Haz el paso 2.2.
4. Doble clic en `iniciar_radar.bat`. La primera línea debe decir `Modo: GitHub gamertag61/HOFERTAS | IA: gemini-…`
   y cada vuelta termina con `Subiendo a GitHub…` y `Commit exitoso` (o el error exacto).
5. Para que arranque solo: `Win + R` → `shell:startup` → pega ahí un acceso directo a `iniciar_radar.bat`.
6. Configura Windows para que la laptop no se suspenda (Configuración → Energía → Suspender: Nunca).

Qué hace cada vuelta (cada `intervalo_min` minutos, por defecto 30):
- Lee cada enlace, guarda el precio en `precios.db` y descarta lecturas absurdas.
- Detecta bajas y **súper ofertas** (caída de 8 % o más contra hace 1 hora, 15 % o más bajo su precio normal de 30 días y mínimo
  del mes, confirmada con una segunda lectura 5 minutos después). Con menos de 7 días de historial no hay súper ofertas.
- La IA limpia nombre, categoría y 3 specs. Si Gemini se satura, espera y reintenta; si se acaba la cuota del día,
  se pausa hasta mañana. Los precios nunca se detienen y mientras tanto se usan nombres de respaldo.
- Publica `datos.json` y `alertas.json` en un solo commit. Todo queda registrado en `radar.log`.

Otros comandos: `python heleos_radar.py` (una sola vuelta), `--debug` (si falla un precio),
`python -m unittest discover tests` (pruebas sin internet).

## 4. Panel

Abre `https://gamertag61.github.io/HOFERTAS/dashboard.html`, toca el ícono de enlace junto al contador de enlaces,
pega tu token de GitHub y presiona **Conectar** (el repositorio se detecta solo). Desde ahí, **Guardar enlaces** escribe en el
`enlaces.txt` del repositorio y el radar los rastrea en su siguiente vuelta. Al agregar productos, suma su nombre comercial
en `nombres.js` si quieres uno escrito a mano (si no, se usa el de la IA).

## 5. Misiones de inventario (director de compras)

`python heleos_asesor.py` lee `datos.json` (el local; si no hay, el de GitHub), cuenta productos por categoría y le pide a
Gemini 3 tipos de producto que faltan en el catálogo de PC Gamer. Guarda `misiones.json` y lo sube a GitHub (rama main)
con las mismas claves de `heleos_config.json`. `--local` solo lo guarda sin subir. Si Gemini falla, `misiones.json` no
se toca. Córrelo cuando quieras nuevas misiones (por ejemplo una vez por semana); no hace falta tenerlo encendido.

En el panel y en la app, el botón **🎯 Misiones** abre la lista como tareas: márcalas cuando consigas el producto (se
recuerda en ese navegador) y usa **Buscar en Mercado Libre** para encontrar candidatos.

## Probar en la laptop principal (opcional)

`python -m http.server 8765` → `http://localhost:8765/`. Sin `heleos_config.json`, `python heleos_radar.py` trabaja con
los archivos locales.
