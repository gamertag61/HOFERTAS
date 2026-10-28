---
name: Heleos
description: Vitrina nocturna de ofertas verificadas de Mercado Libre, mobile-first, en azul noche y ámbar.
colors:
  azul-noche: "#070b14"
  noche-media: "#0a1220"
  noche-profunda: "#060a12"
  superficie: "#0b121d"
  superficie-alta: "#0f1826"
  borde-vitrina: "#1b2a3d"
  ambar-oferta: "#ffb340"
  azul-resplandor: "#2f8fff"
  texto-principal: "#f4f4f5"
  texto-tarjeta: "#e4e4e7"
  texto-secundario: "#a1a1aa"
  texto-tachado: "#71717a"
typography:
  display:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"SF Pro Display\", \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif"
    fontSize: "3.75rem"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"SF Pro Display\", \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif"
    fontSize: "1.875rem"
    fontWeight: 600
    lineHeight: 1.2
  title:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"SF Pro Display\", \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.55
    letterSpacing: "-0.025em"
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"SF Pro Display\", \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.25rem
  label:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"SF Pro Display\", \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1rem
rounded:
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
  xxl: "48px"
components:
  boton-comprar:
    backgroundColor: "{colors.ambar-oferta}"
    textColor: "{colors.azul-noche}"
    typography: "{typography.body}"
    rounded: "{rounded.pildora}"
    padding: "10px 0"
  boton-comprar-heroe:
    backgroundColor: "{colors.ambar-oferta}"
    textColor: "{colors.azul-noche}"
    rounded: "{rounded.pildora}"
    padding: "12px 36px"
  pildora-descuento:
    backgroundColor: "{colors.azul-noche}"
    textColor: "{colors.ambar-oferta}"
    typography: "{typography.label}"
    rounded: "{rounded.pildora}"
    padding: "4px 10px"
  pildora-descuento-heroe:
    textColor: "{colors.ambar-oferta}"
    typography: "{typography.label}"
    rounded: "{rounded.pildora}"
    padding: "2px 10px"
  tarjeta-producto:
    backgroundColor: "{colors.superficie}"
    textColor: "{colors.texto-tarjeta}"
    rounded: "{rounded.tarjeta}"
    padding: "12px"
  cabecera:
    backgroundColor: "{colors.azul-noche}"
    textColor: "{colors.texto-principal}"
    padding: "12px 16px"
  menu-lateral:
    backgroundColor: "{colors.noche-profunda}"
    textColor: "{colors.texto-principal}"
    padding: "16px 24px 32px"
  boton-icono:
    textColor: "{colors.texto-principal}"
    rounded: "{rounded.pildora}"
    size: "40px"
---

# Design System: Heleos

> Encabezados de sección en inglés a propósito: son los nombres canónicos del formato DESIGN.md y las herramientas los leen tal cual. Todo el contenido está en español.
> Fuente extraída: `index.html` (catálogo "H | Ofertas"). Los tokens del frontmatter son normativos; la prosa explica cómo aplicarlos.

## Overview

**Creative North Star: "Vitrina nocturna"**

Una tienda iluminada de noche. El producto flota bajo un foco de luz azul fría, todo lo demás se hunde en el azul noche, y el ámbar aparece solo donde está el dinero: el precio, el descuento y el botón de compra. El ojo no tiene que buscar; la luz ya decidió qué mirar.

La densidad es baja y táctil. Pensado primero para un pulgar en el celular que viene de TikTok: un héroe deslizable con tres ofertas, una cinta de categorías en movimiento y una cuadrícula de tarjetas de dos columnas que crece a tres y cuatro. Las superficies son translúcidas o con degradado vertical sutil sobre el fondo, con borde fino `borde-vitrina`; la profundidad se construye con luz (halos, resplandores, brillo del precio), no con capas de sombra gris.

El movimiento es parte del escaparate: las piezas suben en cascada al cargar, el producto del héroe entra desenfocado y se enfoca, el halo respira y la imagen flota. Todo se apaga con `prefers-reduced-motion`.

**Key Characteristics:**
- Fondo azul noche con degradado vertical y un foco de luz azul en la parte superior.
- Ámbar como única voz de acción y de dinero.
- Azul resplandor solo como luz ambiental, nunca como color de interfaz.
- Formas muy redondeadas: píldoras para acciones y etiquetas, esquinas amplias en contenedores.
- Tipografía del sistema (SF Pro en Apple), seminegrita y apretada en titulares.
- Motion de entrada generoso y lento; respuestas de interacción cortas.

## Colors

Una noche azul casi negra, iluminada por dos luces: ámbar cálido para la oferta y azul frío para la atmósfera.

### Primary
- **Ámbar oferta** (`ambar-oferta`): precio actual, píldora de descuento, botón "Comprar", punto de marca con brillo, barra de avance del día, relleno de los indicadores del héroe, hover del menú lateral y anillo de foco. Es el único color que pide acción.

### Secondary
- **Azul resplandor** (`azul-resplandor`): luz ambiental exclusivamente. Halo detrás del producto del héroe, brillo radial superior del fondo (14 % de opacidad), borde y resplandor de tarjeta en hover (55 %), y separadores de la cinta. Oficializado como color de atmósfera; no se usa en botones, texto ni rellenos sólidos.

### Neutral
- **Azul noche** (`azul-noche`): fondo de página, `theme-color`, texto sobre botones ámbar y base translúcida de cabecera (80 %) y píldoras sobre imagen.
- **Noche media** (`noche-media`): punto medio del degradado vertical del fondo.
- **Noche profunda** (`noche-profunda`): fondo del menú lateral, un escalón más oscuro que la página para separarlo.
- **Superficie** (`superficie`): parte inferior del degradado de tarjetas; superficie secundaria oficial.
- **Superficie alta** (`superficie-alta`): parte superior del degradado de tarjetas.
- **Borde vitrina** (`borde-vitrina`): bordes de tarjetas, héroe, menú, cabecera (70 %) y separadores; también la pista vacía de los indicadores.
- **Texto principal** (`texto-principal`): marca, titulares, ítems del menú.
- **Texto tarjeta** (`texto-tarjeta`): título del producto en tarjeta.
- **Texto secundario** (`texto-secundario`): descripción del héroe, cinta, "Expiran pronto", mensajes de carga/vacío/error.
- **Texto tachado** (`texto-tachado`): precio original tachado.

### Named Rules
**The Ámbar Es Dinero Rule.** El ámbar solo marca precio, descuento y la acción de comprar (más el foco y el progreso). Si algo ámbar no es dinero ni acción, sobra.

**The Luz No Es Botón Rule.** El azul resplandor es luz, no interfaz: siempre difuso (halo, blur, sombra, opacidad ≤ 62 %). Nunca un relleno sólido, un texto ni un botón azul.

**The Paleta Cerrada Rule.** Ningún color de marca fuera de este frontmatter sin preguntar. Los grises de texto son la escala zinc de Tailwind; no se agregan acentos nuevos (ni rojo TikTok, ni verde de "éxito") sin decisión explícita.

## Typography

**Display Font:** pila del sistema: `-apple-system`, `SF Pro Display` (con Segoe UI, Roboto, Helvetica, Arial)
**Body Font:** la misma pila.

**Character:** Sin fuente web: carga instantánea y aspecto nativo en el iPhone del comprador. La personalidad viene del peso (seminegrita) y del interletrado apretado en titulares, no de una tipografía decorativa.

### Hierarchy
- **Display** (600, 2.25rem en móvil → 3.75rem desde 768 px, interlineado 1.05, `-0.025em`): titular del héroe, las primeras 5 palabras del título del producto.
- **Headline** (600, 1.875rem): precio en el héroe, en ámbar.
- **Title** (600, 1.125rem, `-0.025em`): nombre de marca en la cabecera y precio en tarjeta. Los ítems del menú lateral usan 1.25rem en peso 500.
- **Body** (400, 0.875rem, interlineado 1.25rem): títulos de tarjeta (2 líneas máximo, altura mínima reservada de 2.5rem), descripción del héroe (2 líneas, máx. ~28rem), botones.
- **Label** (600, 0.75rem): píldoras de descuento y textos auxiliares de cabecera.

### Named Rules
**The Precio Manda Rule.** En cualquier tarjeta, el precio actual es el texto más fuerte después de la imagen: ámbar, seminegrita, con brillo. El precio original va al lado, más chico, gris y tachado.

**The Dos Líneas Rule.** Los títulos de Mercado Libre son largos; siempre se cortan a 2 líneas con altura reservada para que la cuadrícula no baile.

## Layout

- **Contenedor:** ancho máximo 72rem (1152 px), centrado, con margen lateral de 16 px.
- **Cabecera:** fija arriba (sticky), translúcida con desenfoque; debajo, una línea de 1 px que se llena en ámbar según la hora del día.
- **Héroe:** carrusel horizontal con scroll-snap; en móvil la imagen va arriba (proporción 5:4) y el texto abajo; desde 768 px son dos columnas, texto a la izquierda e imagen cuadrada (máx. 500 px) a la derecha. Avance automático cada 5 s, pausa al tocar y cuando la pestaña está oculta.
- **Cinta:** franja entre bordes superior e inferior con las categorías desplazándose en bucle.
- **Cuadrícula:** 2 columnas en móvil, 3 desde 768 px, 4 desde 1024 px. Separación de 12 px en móvil y 20 px desde 640 px.
- **Ritmo vertical:** 16 px bajo la cabecera, 24 px héroe → cinta, 32 px cinta → cuadrícula, 64 px al final.
- **Puntos de quiebre:** los de Tailwind: 640, 768 y 1024 px.

## Elevation & Depth

Profundidad por luz, no por sombras grises. Las superficies en reposo son planas (degradado sutil + borde fino). La elevación aparece como respuesta: la tarjeta sube 3 px y se ilumina en azul al pasar el cursor; el botón del héroe y el precio brillan en ámbar. Las únicas sombras oscuras son para despegar el producto del héroe y el menú lateral del fondo.

### Shadow Vocabulary
- **Resplandor de tarjeta** (`box-shadow: 0 0 34px -8px rgba(47,143,255,.55)`): hover de tarjeta, junto con borde azul al 55 %.
- **Resplandor ámbar de acción** (`box-shadow: 0 0 28px -4px rgba(255,179,64,.6)`): botón "Comprar" del héroe.
- **Punto de marca** (`box-shadow: 0 0 14px 3px rgba(255,179,64,.55)`): el punto ámbar junto a "H | Ofertas".
- **Brillo de precio** (`filter: drop-shadow(0 0 10px rgba(255,179,64,.35))`): precio en tarjeta.
- **Producto flotante** (`box-shadow: 0 30px 80px -20px rgba(0,0,0,.8)`): imagen del héroe.
- **Panel lateral** (`box-shadow: 20px 0 60px -20px rgba(0,0,0,.9)`): menú lateral abierto, con velo negro al 60 % y desenfoque detrás.
- **Halo** (degradado radial azul 62 % → 28 % → transparente, `blur(8px)`): detrás del producto del héroe, respirando cada 5 s.

### Named Rules
**The Foco Rule.** La luz azul vive detrás del producto o alrededor de lo que el usuario está tocando. Nunca ilumina un área vacía ni un bloque de texto.

## Shapes

Formas suaves y generosas. Contenedores con esquinas amplias que se anidan de mayor a menor: héroe 2rem → tarjeta 1.5rem → imagen dentro de la tarjeta 1rem. Toda acción y toda etiqueta es una píldora completa. Bordes de 1 px en `borde-vitrina`; no hay bordes gruesos ni esquinas rectas. Las imágenes de producto se recortan en cuadrado (`object-cover`).

## Components

### Buttons
Confiados y táctiles: píldora ámbar llena, sin contorno.
- **Shape:** píldora completa (9999px).
- **Primario "Comprar" (tarjeta):** ámbar lleno, texto azul noche seminegrita 0.875rem, ancho completo, 10 px de alto interno.
- **Primario "Comprar" (héroe):** igual, más ancho (36 px laterales), con resplandor ámbar.
- **Hover / Active:** brillo +10 % al pasar el cursor; escala 0.95 al presionar.
- **Focus:** anillo ámbar de 2 px a 3 px de distancia.
- **Botón de icono (menú/cerrar):** círculo de 40 px, transparente; hover con blanco al 5 %; escala 0.95 al presionar.

### Chips
- **Píldora de descuento:** texto ámbar seminegrita 0.75rem. Sobre imagen: fondo azul noche al 80 % con desenfoque, esquina superior izquierda (10 px). En el héroe: fondo ámbar al 15 %.

### Cards / Containers
- **Corner Style:** 1.5rem.
- **Background:** degradado vertical de `superficie-alta` a `superficie`.
- **Shadow Strategy:** ninguna en reposo; resplandor azul en hover (ver Elevation & Depth).
- **Border:** 1 px `borde-vitrina`, pasa a azul resplandor al 55 % en hover.
- **Internal Padding:** 12 px; textos con 4 px extra a los lados.
- **Contenido en orden:** imagen cuadrada (con zoom 1.05 en hover, 500 ms) → píldora de descuento sobre la imagen → título (2 líneas) → precio + tachado → botón "Comprar".
- **Héroe:** contenedor de 2rem con borde `borde-vitrina` sobre azul noche al 60 %.

### Navigation
- **Cabecera:** botón de menú + punto ámbar + "H | Ofertas" (título 1.125rem) a la izquierda; "Expiran pronto" en label gris a la derecha. Fondo azul noche al 80 % con desenfoque y borde inferior.
- **Menú lateral:** entra desde la izquierda (78 % del ancho, máx. 20rem) en 0.45 s; ítems 1.25rem peso 500 separados por líneas `borde-vitrina`, con flecha a la derecha y hover ámbar; entran en cascada de 70 ms. Se cierra con Escape, con el velo o con el botón; el foco va y vuelve al botón que lo abrió.
- **Indicadores del héroe:** barras de 36×4 px en píldora; la activa se llena en ámbar durante 5 s.

### Barra del día (firma)
Línea de 1 px bajo la cabecera que se llena en ámbar según la hora actual. Refuerza "Expiran pronto" sin texto extra.

### Estados de carga, vacío y error
Texto gris secundario centrado con 64 px de aire vertical, en el lugar de la cuadrícula; el héroe se oculta. Mensajes cortos en español: "Cargando ofertas…", "Hoy no hay ofertas nuevas. Vuelve en unas horas.", "No pudimos cargar las ofertas. Recarga en un momento."

### Motion
- **Entrada en cascada:** sube 18 px y aparece en 0.8 s con `cubic-bezier(.2,.7,.2,1)`, 90 ms entre piezas.
- **Producto del héroe:** entra de escala 1.3, desplazado 6 % y desenfocado 16 px hasta su lugar en 1.3 s con `cubic-bezier(.16,.8,.2,1)`; el texto lo sigue en cascada de 150 ms.
- **Ambiente:** halo respira (5 s), producto flota 8 px (6 s), cinta recorre en 32 s.
- **Interacción:** tarjeta 0.4 s; menú 0.45 s con `cubic-bezier(.2,.8,.2,1)`; velo 0.35 s.
- **Movimiento reducido:** todas las animaciones y transiciones se desactivan y el contenido aparece en su estado final.

## Do's and Don'ts

### Do:
- **Do** usar `ambar-oferta` solo para precio, descuento, comprar, foco y progreso.
- **Do** usar `azul-resplandor` únicamente como luz difusa: halos, brillo de fondo, hover de tarjetas.
- **Do** construir tarjetas translúcidas o con degradado sobre azul noche, con borde 1 px `borde-vitrina` y esquinas de 1.5rem.
- **Do** formatear precios en MXN sin centavos (`es-MX`) y mostrar siempre el original tachado junto al actual.
- **Do** diseñar primero para móvil de 2 columnas y verificar en 375 px de ancho.
- **Do** respetar `prefers-reduced-motion` y mantener el anillo de foco ámbar en todo elemento interactivo.
- **Do** marcar los enlaces de afiliado con `rel="noopener noreferrer sponsored"` y abrirlos en pestaña nueva.

### Don't:
- **Don't** introducir colores fuera del frontmatter sin preguntar: ni el rosa TikTok `#ff0050` ni los azules/rojos de Tailwind que hoy usa `studio.html`.
- **Don't** hacer botones, textos o rellenos sólidos en azul resplandor.
- **Don't** usar sombras grises para separar tarjetas en reposo; la profundidad es luz.
- **Don't** usar esquinas rectas ni botones que no sean píldora.
- **Don't** cargar fuentes web; la pila del sistema es parte del rendimiento.
- **Don't** inventar datos en tarjetas (envío gratis, reseñas, stock): solo lo que trae `ofertas.json`.

## Flujo de diseño con skills

Toda interfaz que se toque pasa por las tres skills instaladas, en este orden:

1. **Impeccable** (`/impeccable`): fuente de verdad del contexto. Lee `PRODUCT.md` y este `DESIGN.md` antes de editar; usar sus comandos según la tarea (`shape` para planear, `critique`/`audit` para revisar, `polish` antes de publicar). Si el sistema cambia, volver a correr `/impeccable document`.
2. **Taste Skill** (`design-taste-frontend`): dirección de arte y control anti-genérico. En el catálogo (público) aplica su flujo de páginas; en el Centro de Mando aplica su flujo de pantallas de trabajo (dashboards). Siempre dentro de esta paleta y estas formas.
3. **Emil Kowalski** (`emilkowalski-motion`): al final, cuando la interfaz ya existe, para micro-interacciones y transiciones. Respetar la gramática de Motion de arriba: entradas lentas y suaves, respuestas de interacción cortas, todo desactivable con movimiento reducido.

Revisión visual: Playwright en la laptop principal (nunca como dependencia de `heleos_radar.py`).
