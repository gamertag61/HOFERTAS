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

Mobile-first para quien llega desde TikTok. Héroe dividido (texto monumental + teclado que levita), carrusel horizontal de ofertas con scroll-snap y una sección "mini software" que dibuja el historial real de una baja de precio.

**Key Characteristics:**
- Grafito `#0a0b0d` con una luz lima muy tenue arriba a la derecha.
- Verde lima como acento exclusivo: palabras clave, botones primarios, píldoras de valor, precios.
- Titulares en Poppins 800 con interletrado apretado; datos en JetBrains Mono con cifras tabulares.
- Píldoras para toda acción y etiqueta; esquinas amplias en contenedores.
- Movimiento sobrio: aparición desde abajo al hacer scroll, teclado que flota, línea de precio que se dibuja.

## Colors

### Primary
- **Lima** (`lima`): palabra clave del titular, CTA primario, botón "Aprovechar oferta", píldora de descuento, precio actual, punto de marca, estado del radar, línea y puntos del gráfico, anillo de foco y selección de texto. También como luz difusa: halo radial detrás de cada producto (32 % → 8 % → transparente, `blur(18px)`) y relleno bajo la línea del gráfico.

### Neutral
- **Grafito** (`grafito`): fondo de página, `theme-color`, texto sobre lima, cabecera al 75 % con desenfoque.
- **Panel** (`panel`): menú lateral, bloque del radar, base del degradado del escenario.
- **Mate** (`mate`): tarjetas de oferta.
- **Mate alto** (`mate-alto`): parte superior del degradado de escenario e imagen, etiquetas del gráfico.
- **Línea** (`linea`): bordes de 1 px, guías punteadas del gráfico, bordes de píldoras técnicas.
- **Texto principal / tarjeta**: titulares y nombres de producto.
- **Humo** (`humo`): subtítulos y párrafos.
- **Ceniza** (`ceniza`): etiquetas de métricas, precio tachado, ejes del gráfico, pie de página.

### Named Rules
**The Lima Es Valor Rule.** El lima marca valor o acción: el dato que convence (palabra clave, precio, descuento, la baja en el gráfico) y el botón que lleva a Mercado Libre. Si algo lima no es valor ni acción, sobra.

**The Paleta Cerrada Rule.** Ningún color de marca fuera de este frontmatter sin preguntar. Sin rojos de "baja", sin azules, sin rosa TikTok.

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

- **Contenedor:** 72rem máx., centrado, margen lateral de 20 px (24 px desde 640 px).
- **Cabecera:** sticky, 64 px, tres columnas: menú hamburguesa a la izquierda, logo "H | Ofertas" con punto lima al centro, estado del radar a la derecha (desde 640 px).
- **Héroe:** una columna en móvil (texto arriba, teclado abajo); desde 768 px, dos columnas `1.05fr / .95fr`.
- **Carrusel de ofertas:** pista horizontal sin barra visible, `scroll-snap-type: x mandatory`; tarjetas de `78vw` (máx. 300 px) en móvil y 290 px desde 640 px; separación de 16 px; flechas desde 768 px. Desde 1200 px la primera tarjeta se alinea con el contenedor.
- **Radar:** una columna en móvil; desde 1024 px, texto `.8fr` + panel `1.2fr`.
- **Ritmo vertical:** secciones de 80 px (112 px desde 768 px), separadas por una línea blanca al 5 %.

## Elevation & Depth

Profundidad por luz lima difusa detrás del producto y por sombras oscuras con desplazamiento; nunca resplandores de color alrededor de botones.

### Shadow Vocabulary
- **Botón lima** (`0 6px 16px -8px rgba(0,0,0,.8)`; hover `0 10px 22px -10px rgba(0,0,0,.9)`).
- **Foto de producto** (`0 18px 30px -12px rgba(0,0,0,.7)`).
- **Teclado** (`drop-shadow(0 30px 40px rgba(0,0,0,.6))`) más una sombra elíptica en el piso que se encoge cuando sube.
- **Halo lima**: degradado radial desenfocado detrás de cada producto (ver Colors).

## Shapes

Héroe/escenario 2rem → tarjeta 1.5rem → imagen 1rem → foto 0.75rem. Toda acción y etiqueta es píldora. Bordes de 1 px en `linea`.

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
- **Tarjeta de oferta:** mate, borde `linea`, 1.5rem, 12 px de relleno. Orden: escenario con halo + foto sobre blanco + píldora de descuento → nombre (2 líneas) → píldoras técnicas → precio + tachado → botón. Hover: sube 3 px, el borde se aclara y la foto escala 1.04.

### Héroe
- **Escenario del teclado:** contenedor de 2rem con degradado `mate-alto → panel`, halo lima, teclado SVG en perspectiva (`rotateX(34deg) rotateZ(-9deg)`) con dos teclas lima, píldora "Oferta: $precio real" flotando y barra inferior con nombre, precio anterior y "Ver oferta". Todo apunta al teclado real con más descuento de `ofertas.json`.
- **Métricas:** ofertas verificadas (conteo real), "24/7" radar activo, "100%" precios reales.

### Radar (mini software)
Panel `panel` con barra superior (nombre del producto + botones de baja "-X %"), gráfico SVG del historial real (`historial.json` + la alerta), leyenda "antes → ahora" y log mono de las bajas detectadas. Sin bajas muestra "El radar no detectó bajas en su última vuelta."

### Estados
Carga con esqueletos brillantes en la pista; vacío: "Hoy no hay ofertas nuevas. Vuelve en unas horas."; error: "No pudimos cargar las ofertas. Recarga en un momento."

### Motion
- **Aparición:** sube 18 px y aparece (opacidad 0.7 s, transform 0.9 s, `cubic-bezier(.16,1,.3,1)`), con 70 ms entre piezas, por IntersectionObserver; sin JS todo es visible.
- **Teclado:** flota 14 px en 6 s; la sombra y la píldora lo acompañan.
- **Gráfico:** la línea se dibuja en 1.6 s; después aparecen el relleno y los puntos en cascada.
- **Interacción:** botones de 160 a 200 ms; menú 0.38 s.
- **Movimiento reducido:** se apagan los loops, los desplazamientos y el dibujo; solo queda un fundido corto.

## Do's and Don'ts

### Do:
- **Do** usar el lima solo para valor y acción.
- **Do** sacar todo número de `ofertas.json`/`historial.json`; MXN sin centavos (`es-MX`).
- **Do** marcar los enlaces de afiliado con `rel="noopener noreferrer sponsored"` y abrirlos en pestaña nueva.
- **Do** verificar en 375 px sin scroll horizontal y respetar `prefers-reduced-motion`.

### Don't:
- **Don't** poner resplandores de color alrededor de botones.
- **Don't** usar emojis como iconos; los iconos son SVG de trazo de 2 px.
- **Don't** inventar specs, reseñas, envío ni stock.
- **Don't** poner etiquetas pequeñas encima de los títulos.

## Flujo de diseño con skills

Toda interfaz que se toque pasa por las tres skills instaladas, en este orden:

1. **Impeccable** (`/impeccable`): fuente de verdad del contexto. Lee `PRODUCT.md` y este `DESIGN.md` antes de editar; usar sus comandos según la tarea (`shape` para planear, `critique`/`audit` para revisar, `polish` antes de publicar). Si el sistema cambia, volver a correr `/impeccable document`.
2. **Taste Skill** (`design-taste-frontend`): dirección de arte y control anti-genérico. En el catálogo (público) aplica su flujo de páginas; en el Centro de Mando aplica su flujo de pantallas de trabajo (dashboards). Siempre dentro de esta paleta y estas formas.
3. **Emil Kowalski** (`emilkowalski-motion`): al final, cuando la interfaz ya existe, para micro-interacciones y transiciones. Respetar la gramática de Motion de arriba, con respuestas de interacción cortas y todo desactivable con movimiento reducido.

Revisión visual: Playwright en la laptop principal (nunca como dependencia de `heleos_radar.py`).
