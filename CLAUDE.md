# Heleos

Ecosistema de afiliados de Mercado Libre compuesto por:
- **Centro de Mando Todo-en-Uno**: panel para gestionar ofertas, enlaces y estadísticas.
- **Catálogo Web estilo "Voltio"**: tarjetas de producto con píldoras de datos clave (precio, descuento, envío, etc.).
- **Radar** (`heleos_radar.py`): script que rastrea ofertas y alimenta `ofertas.json` / `historial.json`.

## Paleta oficial

| Uso | Color |
|---|---|
| Fondo principal (azul noche profundo) | `#070b14` |
| Fondo secundario / superficies | `#0b121d` |
| Bordes de tarjetas translúcidas | `#1b2a3d` |
| Acentos y botones (amarillo brillante) | `#ffb340` |
| Luz ambiental: halos, brillos, hover (azul resplandor; nunca botones ni texto) | `#2f8fff` |

Las tarjetas son translúcidas (fondo semitransparente sobre el azul noche) con borde `#1b2a3d`. No introducir colores de marca fuera de esta paleta sin preguntar.

## Regla de hardware

- El catálogo y el centro de mando se programan en la laptop principal (8 GB RAM).
- `heleos_radar.py` corre 24/7 en una laptop secundaria de **4 GB RAM**:
  - **Prohibido** usar Selenium, Playwright o cualquier navegador headless dentro de `heleos_radar.py`.
  - Solo `requests` + `BeautifulSoup` (y librería estándar). Mantener bajo consumo de memoria y CPU.
- Playwright sí se puede usar en la laptop principal para revisar visualmente el catálogo y el centro de mando, nunca como dependencia del radar.

## Diseño de interfaces

Para cada interfaz que se toque, usar las skills de diseño instaladas: **Impeccable**, **Emil Kowalski (motion)** y **Taste Skill**. Contexto de producto en `PRODUCT.md`; sistema visual ("Vitrina nocturna") en `DESIGN.md`.

## Estado del proyecto

### Fase A: Front-End del Centro de Mando — TERMINADA Y APROBADA (2026-10-27)

`dashboard.html` (Cockpit) aprobado por el usuario. No rediseñar sin pedirlo.

- **Visor (70 %)**: Mercado Libre bloquea el `<iframe>` con `frame-ancestors` cuando hay cookies/sesión. **Ruta elegida: "Ventana acoplada"** (botón "Abrir acoplado"): abre Mercado Libre en una ventana de Chrome del mismo tamaño y posición que el visor, con la sesión real del usuario. Se descartó Electron.
- **Panel Heleos (30 %)**:
  - Caja de municiones: auto-salto de línea con Enter y al pegar, conteo de enlaces, borrador en `localStorage`; "Guardar Enlaces" agrega a `enlaces.txt` sin duplicar (File System Access API en Chrome/Edge; si no, descarga `enlaces_nuevos.txt`).
  - Alertas flash: bajas reales de `historial.json` + botón "Simular alerta"; clic abre el producto en el visor.
  - Centro TikTok: SKU/modelo → búsqueda en Pinterest "aesthetic wallpaper".
- Se sirve con `python -m http.server 8765` (`.claude/launch.json`) → `http://localhost:8765/dashboard.html`.

### Fase B: Radar + despliegue sin laptop principal — CÓDIGO LISTO (2026-10-27), FALTA SUBIR

Arquitectura: **GitHub es el bus de datos**. Solo el radar depende de una máquina encendida (laptop viejita).

- **GitHub Pages** sirve `index.html` y `dashboard.html` (repositorio público nuevo `heleos`, a crear por el usuario).
- **Cockpit**: "Guardar Enlaces" escribe `enlaces.txt` en el repo vía API de GitHub (token fine-grained, solo Contents, guardado en `localStorage` del navegador del usuario; repo deducido de `usuario.github.io/repo`). Sin token usa el archivo local como antes.
- **Radar** (`heleos_radar.py`): con `heleos_config.json` (gitignored) lee `enlaces.txt` del repo y publica `ofertas.json` + `historial.json` en **un solo commit** (Git Data API, solo `requests`). `--loop` corre cada `intervalo_min` (mín. 15, default 180) y no se cae por errores de red. Detecta bajas de precio contra el último precio del historial y las guarda en `ofertas.json.alertas` (máx. 30); el Cockpit las muestra.
- Pasos de instalación para el usuario: `INSTALAR.md`. Arranque 24/7: `iniciar_radar.bat` en `shell:startup`.
- Probado: vuelta real local (25 ofertas, 5 bajas reales); modo GitHub del radar y del Cockpit con API simulada. **No probado aún contra GitHub real** (falta repo + token del usuario).
