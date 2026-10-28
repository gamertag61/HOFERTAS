# Heleos

Ecosistema de afiliados de Mercado Libre compuesto por:
- **Centro de Mando Todo-en-Uno**: panel para gestionar ofertas, enlaces y estadísticas.
- **Catálogo Web estilo "Voltio"**: tarjetas de producto con píldoras de datos clave (precio, descuento, envío, etc.).
- **Radar** (`heleos_radar.py`): script que rastrea ofertas y alimenta `ofertas.json` / `historial.json`.

## Paleta oficial

Desde 2026-10-28 (rediseño de `index.html` con referencia "Voltio", pedido por el usuario): grafito y verde lima.

| Uso | Color |
|---|---|
| Fondo principal (grafito casi negro) | `#0a0b0d` |
| Fondo secundario / paneles | `#101215` |
| Tarjetas (gris oscuro mate) | `#15171b` (superficie alta `#1b1e23`) |
| Bordes de tarjetas | `#24272d` |
| Acento exclusivo (verde lima): palabras clave, botones principales, píldoras de valor y precios | `#c6f135` |
| Texto secundario / terciario | `#9aa0a8` / `#6b7079` |

El verde lima también se usa como luz difusa (halo detrás del producto). Tipografía: Poppins (títulos en 800) + JetBrains Mono para datos (precios, specs, log del radar). No introducir colores de marca fuera de esta paleta sin preguntar.

Las tres superficies (`index.html`, `dashboard.html`, `app.html`) usan esta paleta desde 2026-10-28.

## Regla de hardware

- El catálogo y el centro de mando se programan en la laptop principal (8 GB RAM).
- `heleos_radar.py` corre 24/7 en una laptop secundaria de **4 GB RAM**:
  - **Prohibido** usar Selenium, Playwright o cualquier navegador headless dentro de `heleos_radar.py`.
  - Solo `requests` + `BeautifulSoup` (y librería estándar). Mantener bajo consumo de memoria y CPU.
- Playwright sí se puede usar en la laptop principal para revisar visualmente el catálogo y el centro de mando, nunca como dependencia del radar.

## Diseño de interfaces

Para cada interfaz que se toque, usar las skills de diseño instaladas: **Impeccable**, **Emil Kowalski (motion)** y **Taste Skill**. Contexto de producto en `PRODUCT.md`; sistema visual ("Vitrina nocturna") en `DESIGN.md`.

## Estado del proyecto

### Fase A: Centro de Control (`dashboard.html`) — rediseñado a grafito/lima (2026-10-28)

Pedido por el usuario el 2026-10-28 (iframe 70 % + panel 30 % con caja de enlaces y "Módulo IA"). Sin textos visibles "Heleos" ni "radar" (se publica en GitHub Pages).

- **Área principal (70 %)**: `<iframe>` a `https://www.mercadolibre.com.mx/afiliados`. Mercado Libre lo bloquea con `frame-ancestors` (comprobado: el visor queda en blanco). **Ruta que sí funciona: "Abrir acoplado"**: abre Mercado Libre en una ventana de Chrome del mismo tamaño y posición que el visor, con la sesión real del usuario. Se descartó Electron.
- **Panel lateral (30 %)**, dos cajas:
  - Enlaces: cada pegado (Ctrl+V) queda en su línea y el cursor baja al renglón siguiente; Enter limpia y salta; conteo, borrador en `localStorage`; "Guardar enlaces" agrega a `enlaces.txt` sin duplicar (GitHub si hay token; si no, File System Access API o descarga `enlaces_nuevos.txt`).
  - Módulo IA: arriba alertas (bajas reales de `ofertas.json.alertas`/`historial.json` + "Simular alerta"; clic abre el producto en el visor); abajo buscador aesthetic (SKU/ID → Pinterest "aesthetic wallpaper").
  - Las claves de `localStorage` siguen siendo `heleos.municion` y `heleos.github` para no perder el borrador ni el token ya guardados.

### App del creador (`app.html`) — nueva (2026-10-28)

Mobile-first (`max-w-md`), para usar en el celular al grabar TikToks. Feed compacto de `ofertas.json` (foto, título a 2 líneas, specs sacadas del título, tachado y precio lima) con "Buscar fondos" (Pinterest) y "Ver guion": teleprompter a pantalla completa con un guion armado por plantilla con los datos reales (no hay IA conectada), botón lima grande para cerrar, A−/A+ y Escape.

- Se sirve con `python -m http.server 8765` (`.claude/launch.json`) → `http://localhost:8765/dashboard.html`.

### Fase B: Radar + despliegue sin laptop principal — SUBIDO a gamertag61/HOFERTAS (2026-10-27); falta activar Pages, token y radar en la laptop viejita

Arquitectura: **GitHub es el bus de datos**. Solo el radar depende de una máquina encendida (laptop viejita).

- **GitHub Pages** sirve `index.html`, `dashboard.html` y `app.html` (repositorio público `gamertag61/HOFERTAS` → https://gamertag61.github.io/HOFERTAS/).
- **Cockpit**: "Guardar Enlaces" escribe `enlaces.txt` en el repo vía API de GitHub (token fine-grained, solo Contents, guardado en `localStorage` del navegador del usuario; repo deducido de `usuario.github.io/repo`). Sin token usa el archivo local como antes.
- **Radar** (`heleos_radar.py`): con `heleos_config.json` (gitignored) lee `enlaces.txt` del repo y publica `ofertas.json` + `historial.json` en **un solo commit** (Git Data API, solo `requests`). `--loop` corre cada `intervalo_min` (mín. 15, default 180) y no se cae por errores de red. Detecta bajas de precio contra el último precio del historial y las guarda en `ofertas.json.alertas` (máx. 30); el Cockpit las muestra.
- Pasos de instalación para el usuario: `INSTALAR.md`. Arranque 24/7: `iniciar_radar.bat` en `shell:startup`.
- Probado: vuelta real local (25 ofertas, 5 bajas reales); modo GitHub del radar y del Cockpit con API simulada. **No probado aún contra GitHub real** (falta repo + token del usuario).
