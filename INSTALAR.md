# Instalar el sistema (sin depender de la laptop principal)

```
 Panel (panel_h7x_secreto.html) ──escribe enlaces.txt──▶  GitHub (repositorio)  ◀──lee enlaces.txt──── Radar (laptop viejita, 24/7)
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
   - Panel: `https://gamertag61.github.io/HOFERTAS/panel_h7x_secreto.html`
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
   La primera línea dice de dónde leyó la clave y sus últimos 4 caracteres (deben coincidir con la tuya);
   al final debe decir **"La clave de Gemini funciona"**. Si no encuentra la clave en ningún lado, se detiene con
   `Error: falta la clave de Gemini…`.
5. Protege el archivo (opcional, recomendado): clic derecho en `heleos_config.json` → **Propiedades → Seguridad**
   y deja con acceso solo a tu usuario.
6. **Borra el .txt donde tenías las claves** (y vacía la Papelera). Desde ahora viven solo en `heleos_config.json`.

Reglas de oro:
- `heleos_config.json` está en `.gitignore`: **nunca lo subas** al repositorio ni lo mandes por chat o correo.
- El radar nunca imprime las claves completas (solo los últimos 4 caracteres).
- Si una clave se filtra: revócala (GitHub → Tokens / AI Studio → borrar clave), crea otra y pégala en `heleos_config.json`.

**Orden de lectura de la clave de Gemini:** primero la variable de entorno `GEMINI_API_KEY` (así la recibe GitHub Actions
desde GitHub Secrets: Settings → Secrets and variables → Actions → `GEMINI_API_KEY`) y, si no existe, `heleos_config.json`.
Si en una laptop tienes una variable de entorno `GEMINI_API_KEY` vieja, **bórrala**: ganaría sobre el archivo
(`[Environment]::SetEnvironmentVariable('GEMINI_API_KEY', $null, 'User')` en PowerShell y abre otra terminal).
En GitHub Actions no hace falta `heleos_config.json`: el repo sale de `GITHUB_REPOSITORY` y el token de `GITHUB_TOKEN`
(pásalo al paso con `env: GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}` y permiso `contents: write`).
(Para GitHub también se aceptan los nombres `GITHUB_REPO` / `GITHUB_TOKEN` en el archivo, y el repo puede ir como URL completa. Las variables de entorno `HELEOS_TOKEN` y `HELEOS_REPO` solo se usan si el archivo no trae ninguno. En cada vuelta la consola muestra "Subiendo a GitHub…" y luego "Commit exitoso" o el error exacto.)

## 3A. Radar en GitHub Actions (24/7 sin laptop, recomendado)

El archivo `.github/workflows/radar.yml` corre una vuelta del radar cada 30 minutos en los servidores de GitHub
(gratis en repositorios públicos) y publica `datos.json` y `alertas.json` en `main`.

1. **Secreto de Gemini:** en GitHub abre el repositorio → **Settings → Secrets and variables → Actions → New repository
   secret**. Nombre: `GEMINI_API_KEY`. Valor: tu clave de Gemini. (El token de GitHub no hace falta: Actions pone uno solo.)
2. **Conservar tu historial (opcional, recomendado):** copia `precios.db` de la laptop viejita a la carpeta del repositorio
   con el nombre **`precios.semilla.db`** y súbelo una vez. La primera ejecución parte de esa memoria (los 30 días
   anti-fraude); sin semilla empieza de cero y las súper ofertas tardan 7 días en aparecer. Solo contiene precios públicos.
3. **Primera prueba:** pestaña **Actions → Radar de precios → Run workflow**. En el registro del paso "Correr una vuelta
   del radar" debe salir `Modo: GitHub gamertag61/HOFERTAS`, `clave de variable de entorno GEMINI_API_KEY: …XXXX` y al final
   `Commit exitoso`. Después corre solo cada 30 min (GitHub puede retrasar las ejecuciones programadas unos minutos).
4. **Apaga el radar de la laptop** (quita `iniciar_radar.bat` de `shell:startup`): dos radares a la vez se pisan los commits.

La memoria (`precios.db`) viaja entre ejecuciones en la caché de Actions. Si el workflow se detiene más de 7 días, GitHub
borra la caché y la memoria vuelve a empezar (o a la semilla). Si Mercado Libre no devuelve ningún precio (por ejemplo,
si bloquea a los servidores de GitHub), la ejecución queda en rojo con ese mensaje y el sitio conserva los últimos datos.

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

Abre `https://gamertag61.github.io/HOFERTAS/panel_h7x_secreto.html`, toca el ícono de enlace junto al contador de enlaces,
pega tu token de GitHub y presiona **Conectar** (el repositorio se detecta solo). Desde ahí, **Guardar enlaces** escribe en el
`enlaces.txt` del repositorio y el radar los rastrea en su siguiente vuelta. Al agregar productos, suma su nombre comercial
en `nombres.js` si quieres uno escrito a mano (si no, se usa el de la IA).

## 4.1 Cupones de Mercado Libre

Mercado Libre no tiene API pública de cupones, así que se escriben a mano en `cupones.json`. Por cada cupón real pon
`"activo": true`, el `codigo`, el `pct` (número), las `categorias` donde aplica (`monitores`, `teclados`, `mouse`, … o
`"*"` para todas) y, si tiene, `vence` (AAAA-MM-DD; al vencer se oculta solo). Con eso, cada producto de esa categoría
muestra la etiqueta "🎟️ CODIGO (-15%)" junto al precio (catálogo, panel y app), el menú del catálogo lo lista en
"Cupones activos" y el panel y la app lo listan arriba del feed. Los ejemplos TECH10 y GAMER15 vienen apagados: no son
códigos reales.

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
