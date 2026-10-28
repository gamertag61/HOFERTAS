---
name: Heleos
description: Landing "H | Ofertas" en grafito y verde lima, con datos reales del radar, inspirada en la referencia Voltio.
colors:
  grafito: "#0a0b0d"
  panel: "#101215"
  mate: "#15171b"
  mate-alto: "#1b1e23"
  linea: "#24272d"
  lima: "#c6f135"
  texto-principal: "#f2f3f5"
  texto-tarjeta: "#f4f4f5"
  humo: "#9aa0a8"
  ceniza: "#6b7079"
typography:
  display:
    fontFamily: "Poppins, ui-sans-serif, sans-serif"
    fontSize: "4.6rem"
    fontWeight: 800
    lineHeight: 0.98
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Poppins, ui-sans-serif, sans-serif"
    fontSize: "2.6rem"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Poppins, ui-sans-serif, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 600
    lineHeight: 1.4rem
  body:
    fontFamily: "Poppins, ui-sans-serif, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.75rem
  data:
    fontFamily: "\"JetBrains Mono\", ui-monospace, monospace"
    fontSize: "0.6875rem"
    fontWeight: 500
    lineHeight: 1.25rem
rounded:
  foto: "0.75rem"
  imagen: "1rem"
  tarjeta: "1.5rem"
  heroe: "2rem"
  pildora: "9999px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "20px"
  xl: "32px"
  xxl: "80px"
components:
  boton-primario:
    backgroundColor: "{colors.lima}"
    textColor: "{colors.grafito}"
    rounded: "{rounded.pildora}"
    padding: "14px 24px"
  boton-secundario:
    textColor: "{colors.texto-principal}"
    rounded: "{rounded.pildora}"
    padding: "14px 24px"
  boton-oferta:
    backgroundColor: "{colors.lima}"
    textColor: "{colors.grafito}"
    rounded: "{rounded.pildora}"
    padding: "12px 0"
  pildora-descuento:
    backgroundColor: "{colors.lima}"
    textColor: "{colors.grafito}"
    typography: "{typography.data}"
    rounded: "{rounded.pildora}"
    padding: "4px 10px"
  pildora-tecnica:
    textColor: "{colors.texto-tarjeta}"
    typography: "{typography.data}"
    rounded: "{rounded.pildora}"
    padding: "4px 10px"
  tarjeta-oferta:
    backgroundColor: "{colors.mate}"
    textColor: "{colors.texto-tarjeta}"
    rounded: "{rounded.tarjeta}"
    padding: "12px"
  cabecera:
    backgroundColor: "{colors.grafito}"
    textColor: "{colors.texto-principal}"
    height: "64px"
  menu-lateral:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.texto-principal}"
    padding: "16px 24px 32px"
---

# Design System: Heleos

> Encabezados de sección en inglés a propósito: son los nombres canónicos del formato DESIGN.md y las herramientas los leen tal cual. Todo el contenido está en español.
> Fuente extraída: `index.html` (landing "H | Ofertas", rediseño del 2026-10-28 sobre la referencia "Voltio"). Los tokens del frontmatter son normativos. `dashboard.html` (Cockpit) todavía usa la paleta anterior (azul noche y ámbar; ver CLAUDE.md) hasta que se migre.

## Overview

**Creative North Star: "Datos, no humo"**

Una herramienta de compra con aire de producto técnico: fondo grafito casi negro, tarjetas gris mate y un único acento verde lima que marca lo que importa (la palabra clave, el precio, la acción). La página no promete: muestra. Cada número sale del radar.

Mobile-first para quien llega desde TikTok, con la densidad de una tienda real en laptop. Héroe con titular arriba y la oferta del día debajo: la foto real del producto, con los bordes fundidos hacia el negro y los datos anclados a las esquinas, cuadrícula compacta de ofertas estilo Amazon/Mercado Libre y una sección "mini software" que dibuja el historial real de una baja de precio.

**Key Characteristics:**
- Grafito `#0a0b0d` con una luz lima muy tenue arriba a la derecha.
- Verde lima como acento exclusivo: palabras clave, botones primarios, píldoras de valor, precios.
- Titulares en Poppins 800 con interletrado apretado; datos en JetBrains Mono con cifras tabulares.
- Píldoras para toda acción y etiqueta; esquinas amplias en contenedores.
- Fotografía real, nunca ilustraciones planas de producto.
- Movimiento sobrio: aparición desde abajo al hacer scroll, deriva lenta de la foto del héroe, línea de precio que se dibuja.

## Colors

### Primary
- **Lima** (`lima`): palabra clave del titular, CTA primario, botón "Aprovechar oferta", píldora de descuento, precio actual, punto de marca, estado del radar, línea y puntos del gráfico, anillo de foco y selección de texto. También como luz difusa: luz ambiental detrás de la foto del héroe, resplandor tenue en hover y relleno bajo la línea del gráfico.

### Neutral
- **Grafito** (`grafito`): fondo de página, `theme-color`, texto sobre lima, cabecera al 75 % con desenfoque.
- **Panel** (`panel`): menú lateral, bloque del radar, fondo detrás de la foto del héroe.
- **Mate** (`mate`): tarjetas de oferta.
- **Mate alto** (`mate-alto`): etiquetas del gráfico.
- **Línea** (`linea`): bordes de 1 px, guías punteadas del gráfico, bordes de píldoras técnicas.
- **Texto principal / tarjeta**: titulares y nombres de producto.
- **Humo** (`humo`): subtítulos y párrafos.
- **Ceniza** (`ceniza`): etiquetas de métricas, precio tachado, ejes del gráfico, pie de página.

### Named Rules
**The Lima Es Valor Rule.** El lima marca valor o acción: el dato que convence (palabra clave, precio, descuento, la baja en el gráfico) y el botón que lleva a Mercado Libre. Si algo lima no es valor ni acción, sobra.

**The Paleta Cerrada Rule.** Ningún color de marca fuera de este frontmatter sin preguntar. Sin rojos de "baja" ni rosa TikTok.

## Typography

**Display Font:** Poppins (Google Fonts), pesos 400–800.
**Data Font:** JetBrains Mono (Google Fonts), solo para datos: precios en píldoras, specs, ejes y log del radar.

### Hierarchy
- **Display** (800, `clamp(2.1rem, 10.4vw, 2.75rem)` en móvil → 3.75rem desde 640 px → 4.6rem desde 1024 px, interlineado 0.98, `-0.035em`, `text-wrap: balance`): titular del héroe.
- **Headline** (700, 1.875rem → 2.6rem desde 640 px, `-0.025em`): títulos de sección.
- **Métrica** (700, 1.875rem, cifras tabulares): fila de confianza del héroe.
- **Precio** (700, 1.5rem, lima): precio actual en tarjeta.
- **Title** (600, 0.9375rem, 2 líneas con altura reservada): nombre corto del producto (primeras 8 palabras).
- **Body** (400, 1rem → 1.125rem en el héroe, interlineado 1.75rem, color humo).
- **Data** (JetBrains Mono 500–600, 0.6875–0.75rem): píldoras, leyenda y log del radar.

### Named Rules
**The Precio Manda Rule.** En la tarjeta, el precio actual en lima es el texto más fuerte después de la imagen; el original va al lado, más chico, ceniza y tachado.

## Layout

- **Contenedor:** `max-w-7xl` (80rem) centrado con `px-4 sm:px-6 lg:px-8`.
- **Cabecera:** sticky, 64 px, tres columnas: menú hamburguesa a la izquierda, logo "H | Ofertas" con punto lima al centro, estado del radar a la derecha (desde 640 px).
- **Héroe:** titular y CTAs arriba; debajo, la oferta del día a todo el ancho (ver Components › Héroe).
- **Cuadrícula de ofertas:** `md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4`, separación de 20 px. En móvil hay dos vistas que el usuario elige (se recuerda en `localStorage`): **lista** (fila estilo Amazon: foto de 108 px a la izquierda, datos a la derecha) y **cuadrícula** de 2 columnas. Se muestran 12 ofertas (orden por mayor descuento) y un botón "Ver N ofertas más". Arriba a la derecha, filtro de rango de precio: campos "Mín ($)" y "Máx ($)" en píldora `mate-alto` y un botón lima redondo con flecha; si no hay resultados aparece "Ninguna oferta entre … " con "Quitar filtro".
- **Radar:** una columna en móvil; desde 1024 px, texto `.8fr` + panel `1.2fr`.
- **Ritmo vertical:** secciones de 56–64 px en móvil y 80–96 px desde 768 px, separadas por una línea blanca al 5 %.

## Elevation & Depth

Profundidad por sombras oscuras con desplazamiento y por luz difusa: lima detrás del producto del héroe, y un resplandor lima muy tenue al pasar el cursor por tarjetas y botones (pedido por el usuario).

### Shadow Vocabulary
- **Botón lima** (`0 6px 16px -8px rgba(0,0,0,.8)`; hover: escala 1.03, brillo +8 % y `0 8px 22px -6px rgba(198,241,53,.45)`).
- **Tarjeta en hover** (sube 4 px, `0 10px 30px rgba(198,241,53,.10)`, borde verdoso).
- **Producto del héroe:** sin sombra ni borde; se funde con degradados lineales en sus 4 bordes.

## Shapes

Producto del héroe sin esquinas (bordes difuminados) → tarjeta 1rem → imagen de producto 0.75rem. Toda acción y etiqueta es píldora. Bordes de 1 px en `linea`.

## Components

### Buttons
- **Primario:** píldora lima llena, texto grafito 600, 14 × 24 px, con flecha.
- **Secundario:** píldora con borde `linea` y texto claro; hover con borde zinc-500 y fondo blanco al 3 %.
- **"Aprovechar oferta":** lima, ancho completo en la tarjeta.
- **Active:** escala 0.97. **Focus:** anillo lima de 2 px a 3 px de distancia.

### Chips
- **Descuento:** lima lleno, texto grafito, mono, en la esquina superior izquierda de la imagen.
- **Píldoras técnicas:** 3 por tarjeta, borde `linea`, fondo negro al 30 %, icono SVG lima + texto mono. Se extraen del título real (Hz, pulgadas, ms, inalámbrico/alámbrico, mecánico/magnético, ANC, mAh, GB/TB, RGB); si faltan, se completan con "-X %" y "Ahorras $Y".

### Cards
- **Tarjeta de oferta:** mate, borde `linea`, 1rem, 10–12 px de relleno. Orden: imagen cuadrada completa (`object-contain` centrada, fondo blanco y relleno de 12–16 px para que ningún producto se recorte) + píldora de descuento → título completo a 2 líneas → píldoras técnicas → precio lima + tachado (+ "Ahorras" desde 768 px) → botón. Botón: "Ver oferta" en móvil, "Aprovechar oferta" desde 768 px. Hover: sube 4 px y la foto escala 1.05.
- **Vista lista (móvil):** fila con foto de 108 px, 2 píldoras y el botón compacto a la derecha del precio. **Vista cuadrícula (móvil):** 2 columnas, 1 píldora.

### Héroe
- **Arriba:** titular a la izquierda y, desde 1024 px, subtítulo + CTAs + métricas a la derecha (`1.15fr / .85fr`).
- **Oferta del día (asimétrica, sin cajas):** contenedor `relative` de ancho completo, 460 px de alto (500 px desde 1280 px). La foto real del producto que extrae el radar ocupa el centro (cuadrada, alto completo, `object-contain` sobre su fondo blanco, escala 1.025 en 9 s). Sus 4 bordes se funden hacia `grafito` con degradados lineales absolutos: arriba 30 %, abajo 42 %, izquierda y derecha 32 %, con parada intermedia al 55–70 %. Nada de fotos de stock ni máscaras circulares.
  - **Superior derecha** (`top-6 right-6`): solo la píldora lima "-X%".
  - **Inferior izquierda** (`bottom-6 left-6`, máx. 30 %): nombre extrabold (1.9rem → 2.25rem, máx. 3 líneas) + píldoras técnicas.
  - **Inferior derecha** (`bottom-6 right-6`, máx. 30 %, alineado a la derecha): precio anterior tachado + precio lima de 3.75rem, "Ahorras $X · precio verificado por el radar" y botón lima grande "Aprovechar oferta →".
  - En móvil y tablet todo se apila (foto de máx. 460 px; nombre subiendo 64 px sobre el degradado inferior; botón de ancho completo en móvil); solo la píldora queda anclada arriba a la derecha.
  - Es el teclado real con más descuento de `ofertas.json` (o la mayor oferta si no hay teclados); se oculta si no hay ofertas o falla la carga. Sombra de texto oscura en los datos.
- **Métricas:** ofertas verificadas (conteo real), "24/7" radar activo, "100%" precios reales, sobre una línea `linea`.

### Radar (mini software)
Panel `panel` con barra superior (nombre del producto + botones de baja "-X %"), gráfico SVG del historial real (`historial.json` + la alerta), leyenda "antes → ahora" y log mono de las bajas detectadas. Sin bajas muestra "El radar no detectó bajas en su última vuelta."

### Estados
Carga con 8 esqueletos brillantes en la cuadrícula; vacío: "Hoy no hay ofertas nuevas. Vuelve en unas horas."; error: "No pudimos cargar las ofertas. Recarga en un momento."

### Motion
- **Aparición bidireccional:** sube 22 px y aparece al entrar en pantalla, y se oculta al salir, en ambos sentidos del scroll (opacidad 0.45 s, `translate` 0.6 s, `cubic-bezier(.16,1,.3,1)`), con 60 ms entre piezas (cascada por fila de 4), por IntersectionObserver (umbral 0.15, márgenes -4 % / -6 %); usa `translate` para no pisar el `transform` del hover; sin JS todo es visible.
- **Producto del héroe:** escala 1.025 en 9 s.
- **Gráfico:** la línea se dibuja en 1.6 s cada vez que el gráfico entra en pantalla; después aparecen el relleno y los puntos en cascada.
- **Interacción:** tarjetas y botones 200–300 ms; menú 0.38 s.
- **Movimiento reducido:** se apagan los loops, los desplazamientos y el dibujo; solo queda un fundido corto.

## Do's and Don'ts

### Do:
- **Do** usar el lima solo para valor y acción.
- **Do** sacar todo número de `ofertas.json`/`historial.json`; MXN sin centavos (`es-MX`).
- **Do** marcar los enlaces de afiliado con `rel="noopener noreferrer sponsored"` y abrirlos en pestaña nueva.
- **Do** verificar en 375 px sin scroll horizontal y respetar `prefers-reduced-motion`.

### Don't:
- **Don't** dibujar productos con CSS o vectores planos; usar fotos reales.
- **Don't** volver al carrusel horizontal de tarjetas gigantes.
- **Don't** usar emojis como iconos; los iconos son SVG de trazo de 2 px.
- **Don't** inventar specs, reseñas, envío ni stock.
- **Don't** poner etiquetas pequeñas encima de los títulos.

## Flujo de diseño con skills

Toda interfaz que se toque pasa por las tres skills instaladas, en este orden:

1. **Impeccable** (`/impeccable`): fuente de verdad del contexto. Lee `PRODUCT.md` y este `DESIGN.md` antes de editar; usar sus comandos según la tarea (`shape` para planear, `critique`/`audit` para revisar, `polish` antes de publicar). Si el sistema cambia, volver a correr `/impeccable document`.
2. **Taste Skill** (`design-taste-frontend`): dirección de arte y control anti-genérico. En el catálogo (público) aplica su flujo de páginas; en el Centro de Mando aplica su flujo de pantallas de trabajo (dashboards). Siempre dentro de esta paleta y estas formas.
3. **Emil Kowalski** (`emilkowalski-motion`): al final, cuando la interfaz ya existe, para micro-interacciones y transiciones. Respetar la gramática de Motion de arriba, con respuestas de interacción cortas y todo desactivable con movimiento reducido.

Revisión visual: Playwright en la laptop principal (nunca como dependencia de `heleos_radar.py`).
