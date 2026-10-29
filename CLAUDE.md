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

### Fase A: Centro de Control (`dashboard.html`) — panel vertical (2026-10-28)

Pedido por el usuario el 2026-10-28. Ya **no** carga Mercado Libre: el `<iframe>` y la ventana acoplada se quitaron porque Mercado Libre bloquea el iframe con `frame-ancestors` (comprobado). Es un panel 100 % vertical (`w-full h-[100dvh]`, máx. 48rem) pensado para acoplarse a un lado de la pantalla en Windows, junto a Mercado Libre abierto aparte. Sin textos visibles "Heleos" ni "radar" (se publica en GitHub Pages).

- **Arriba · Enlaces (altura fija `h-56`):** cada pegado (Ctrl+V) queda en su línea y el cursor baja al renglón siguiente; Enter limpia y salta; conteo, borrador en `localStorage`; "Guardar enlaces" agrega a `enlaces.txt` sin duplicar (GitHub si hay token; si no, File System Access API o descarga `enlaces_nuevos.txt`). La caja crece solo mientras está abierta la conexión con GitHub.
- **Abajo · Módulo IA (`flex-1`, scroll interno):** feed de súper ofertas con las mismas tarjetas que `app.html` (foto, nombre corto, specs, precio lima y tachado) y dos botones: "Buscar fondos" (Pinterest con el nombre corto + "aesthetic wallpaper") y "Guion" (teleprompter a pantalla completa con la plantilla de datos reales).
- Las claves de `localStorage` siguen siendo `heleos.municion` y `heleos.github` para no perder el borrador ni el token ya guardados.
### App del creador (`app.html`) — nueva (2026-10-28)

Mobile-first (`max-w-md`), para usar en el celular al grabar TikToks. Feed compacto de `ofertas.json` (foto, título a 2 líneas, specs sacadas del título, tachado y precio lima) con "Buscar fondos" (Pinterest) y "Ver guion": teleprompter a pantalla completa con un guion armado por plantilla con los datos reales (no hay IA conectada), botón lima grande para cerrar, A−/A+ y Escape.

- Se sirve con `python -m http.server 8765` (`.claude/launch.json`) → `http://localhost:8765/dashboard.html`.

### Fase B: Radar v2 (2026-10-28) — código listo y probado en local; falta instalarlo en la laptop viejita con las claves

Arquitectura: **GitHub es el bus de datos**. Solo el radar depende de una máquina encendida (laptop viejita). Pasos para el usuario: `INSTALAR.md` (claves en `heleos_config.json`, fuera de git: `"GEMINI_API_KEY"` se lee solo del archivo y, si falta, el radar se detiene; las variables de entorno se ignoran para Gemini porque en la laptop principal existe una `GEMINI_API_KEY` vieja e inválida).

- **Código:** `heleos_radar.py` (orquestador: `--loop`, `--probar-ia`, `--debug`) + paquete `radar/`:
  - `extraer.py`: requests + BS4 (JSON-LD → meta → pantalla). Precio, tachado, ID `MLM…`, disponibilidad y cupón del producto principal (ignora las tarjetas `poly-card`/recomendaciones, que traen cupones de otros productos).
  - `db.py`: `precios.db` (SQLite, WAL; gitignored, solo en la laptop del radar). Tablas `productos`, `observaciones`, `enriquecimiento_ia`, `alertas` (`super` | `baja`), `meta`. La primera vez importa `historial.json`.
  - `reglas.py`: anti-fraude con umbrales configurables (`"reglas"` en la config). Referencia = mediana de 30 días de nuestro historial sin las últimas 24 h; con menos de 7 días se usa el tachado. Súper oferta: caída ≥ 8 % contra hace ~1 h (ventana 45–90 min), descuento real ≥ 15 %, mínimo de 30 días y segunda lectura de confirmación 5 min después. Lecturas a más de 70 % de la mediana se descartan.
  - `ia.py`: Gemini por REST (solo requests), `responseMimeType: application/json` + `responseJsonSchema` (con respaldo a `responseSchema`). Modelo por defecto `gemini-2.5-flash` (pedido por el usuario) con respaldo automático ante 404: `gemini-3.1-flash-lite` → `gemini-2.5-flash-lite`. Con la clave real del usuario (2026-10-29), 2.5-flash dio 404 y respondió 3.1-flash-lite. Cola en SQLite: 429/5xx → espera exponencial respetando `retryDelay`; cuota diaria → pausa hasta mañana; clave inválida → reintento en 6 h. Nunca frena los precios: mientras tanto usa `respaldo()` (nombre, categoría y specs por reglas).
  - `exportar.py`: `datos.json` (`version: 2`, productos con `precio.antes` = referencia o tachado, `descuento`, `cupon`, `specs` con emoji + ícono, `senales`, `super_deal`, `historial` diario, `categorias`, `bajas`) y `alertas.json` (súper ofertas de 7 días, máx. 30). Publica ambos en un commit y retira `ofertas.json`/`historial.json` del repo.
  - `github.py`: commit único vía Git Data API (también borra archivos). `config.py` acepta `repo`/`token` o `GITHUB_REPO`/`GITHUB_TOKEN` (el usuario usa estos últimos; antes del 2026-10-29 no se reconocían y el radar quedaba en modo local sin avisar). `subir()` en `heleos_radar.py` imprime "Subiendo a GitHub…" y "Commit exitoso" o el error exacto, sin tumbar la vuelta.
- **Misiones de inventario (2026-10-29):** `heleos_asesor.py` (independiente del radar) cuenta categorías de `datos.json`, pide a Gemini (`Gemini.generar()` de `radar/ia.py`, misma cola de errores y respaldo de modelo) 3 sugerencias `{sugerencia, motivo}` con esquema JSON, escribe `misiones.json` (`version`, `generado`, `modelo`, `nicho`, `catalogo`, `misiones`) y lo sube con `radar/github.py`; `--local` no sube. `misiones.js` (panel y app) inyecta una hoja lateral oculta que solo abre el botón `[data-misiones]` "🎯 Misiones": lista de tareas con casillas (en `localStorage` `heleos.misiones`), progreso, enlace de búsqueda en Mercado Libre y conteo del catálogo; cierra con ×, Escape o clic fuera.
- **Caídas reales y cupones (2026-10-29):** `alertas.json` ya no trae solo súper ofertas: `exportar.caidas_vigentes()` publica una caída por producto (súper primero, luego bajas de 7 días) solo si el precio de hoy sigue abajo del precio anterior medido, con `tipo` (`super` | `baja`), `precio_actual`, `categoria`/`categoria_nombre`, `specs` y `cupon` de la IA. El feed del panel y la app lee **solo** `alertas.json` (`window.cargarAlertas()` en `datos.js`; "antes" = precio anterior medido, nunca el tachado). Cupones: Mercado Libre no tiene API pública, así que se escriben a mano en `cupones.json` (`activo`, `codigo`, `pct`, `categorias` con ids de la IA o `"*"`, `detalle`, `vence`; vencidos se ocultan). `cupones.js` (las tres páginas): `cargarCupones()`, `cuponPara(categoria)` (el de mayor `pct`), `etiquetaCupon()` → badge "🎟️ CODIGO (-15%)" junto al precio en las tarjetas de `index.html` (cuadrícula y oferta del día), `app.html` y `dashboard.html`; `pintarCupones()` → lista compacta de códigos vigentes (copiar al tocar; punto lima si aplica a una caída de hoy) en panel y app. Los ejemplos `TECH10`/`GAMER15` están apagados porque no son códigos reales.
- **Menú de `index.html`:** ya no tiene "Cómo buscamos los precios"; todo el contenido se desplaza junto; abajo, el apartado fijo "Cupones activos" (`#m-cupones`: código, % y "Válido en …"). `#m-cats` se arma con las categorías de la IA en `datos.json` (con conteo) y filtra la cuadrícula junto con el rango de precio; la categoría activa se ve y se quita con el botón `#cat-activa`. Elegir una categoría abre una vista exclusiva: oculta `#heroe` y `#monitoreo`, el título pasa a "Categoría: …", sube al inicio y cambia la dirección a `#categoria=<id>` (Atrás regresa al catálogo; el enlace directo abre esa vista). La X o "Todas las ofertas" restauran todo. Regla global `[hidden] { display: none !important }` porque las clases de Tailwind (`inline-flex`) le ganaban a `hidden` y dejaban el chip vacío visible.
- **Oferta del día (`index.html`):** la súper oferta vigente o, si no hay, la de mayor descuento de `datos.json`; cambia sola con cada vuelta del radar (antes prefería siempre un teclado).
- **Frontend:** `datos.js` (compartido por las tres páginas) carga `datos.json` y, si no existe, el formato anterior; lo normaliza a la forma `{t, o, n, i, link, nombre, specs, super}`. `nombres.js` (las tres páginas): `NOMBRES` escritos a mano por enlace → `p.nombre` (IA o respaldo) → recorte automático.
- **Pruebas:** `python -m unittest discover tests` (reglas, cola de IA con saturación simulada, capa HTTP de Gemini contra servidor local, exportación). Probado además con dos vueltas reales en modo local (26 productos, IDs `MLM` extraídos, una baja real detectada). Gemini probado con la clave real del usuario (`--probar-ia`, 2026-10-29). **No probado aún:** el modo GitHub del radar v2.
- **Panel**: "Guardar enlaces" escribe `enlaces.txt` en el repo vía API de GitHub (token fine-grained, solo Contents, en `localStorage` del navegador). Sin token usa el archivo local.
- Arranque 24/7: `iniciar_radar.bat` en `shell:startup`. GitHub Pages sirve `index.html`, `dashboard.html` y `app.html` (https://gamertag61.github.io/HOFERTAS/).
