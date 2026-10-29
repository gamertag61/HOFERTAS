# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Comprador (catálogo público):** persona en México que llega desde un carrusel de TikTok, casi siempre en el celular. Viene con la atención de un scroll: tiene segundos para entender la oferta (qué es, cuánto cuesta, cuánto se ahorra) y saltar a Mercado Libre a comprar.
- **Dueño (Centro de Mando):** una sola persona, el operador del negocio de afiliados. Uso privado; no hay equipo ni roles.

## Product Purpose

Heleos es un ecosistema de afiliados de Mercado Libre. Convierte una lista curada de enlaces de afiliado (`meli.la`) en ofertas verificadas y publicadas, y en piezas para TikTok que llevan tráfico al catálogo. El éxito es un clic de salida hacia Mercado Libre con el enlace de afiliado: el catálogo existe para que el comprador confíe en la oferta y la abra.

## Positioning

Las ofertas no se escriben a mano ni se calculan con porcentajes: el Radar lee el precio real de cada página de Mercado Libre, guarda su historial diario y solo publica lo que tiene un descuento real (mínimo 5 %). Es una vitrina corta, curada y verificada por precio, alimentada por TikTok, no un agregador masivo.

## Operating Context

- **Flujo de datos:** `enlaces.txt` (lista curada) → `heleos_radar.py` (memoria en `precios.db`, reglas anti-fraude de 30 días, nombres con IA) → `datos.json` (catálogo con historial diario) + `alertas.json` (súper ofertas) → sitio, panel y app los leen con `fetch` (vía `datos.js`).
- **Contenido:** el dueño genera capturas 9:16 de cada oferta (hoy en `studio.html`) y las publica como carruseles de TikTok; el comprador llega de ahí al catálogo.
- **Hardware:** el catálogo y el Centro de Mando se programan en la laptop principal (8 GB). El Radar corre 24/7 en una laptop secundaria de 4 GB (ver CLAUDE.md).
- **Mercado:** México, español (`es-MX`), precios en MXN sin centavos.

## Capabilities and Constraints

Superficies:

- **Catálogo "H | Ofertas"** (`index.html`, landing rediseñada el 2026-10-28): héroe dividido con el teclado en oferta y métricas reales, carrusel horizontal de ofertas (imagen, píldoras técnicas sacadas del título, precio actual, tachado, % de descuento, botón "Aprovechar oferta") ordenado por descuento, sección del radar con el historial real de las bajas (`historial.json` + `alertas`), menú lateral y estados de carga/vacío/error.
- **Estudio** (`studio.html`): genera marcos 9:16 por oferta para capturar, con accesos a "Ver Link" y a búsqueda de fondos en Pinterest. Se integrará al Centro de Mando.
- **Centro de Mando:** aún no existe. Panel privado del dueño para gestionar enlaces/ofertas, revisar lo que detectó el Radar, ver historial de precios y estadísticas, y generar piezas para TikTok (absorbe el Estudio).
- `heleos_prototipo.html` es un prototipo anterior con datos ficticios; no es fuente de verdad.

Restricciones técnicas:

- Sitio estático: HTML + Tailwind por CDN + JS inline, sin paso de build; los datos son archivos JSON locales.
- Radar: solo `requests` + `BeautifulSoup` y librería estándar. Prohibido Selenium, Playwright o navegadores headless dentro del Radar.
- Los enlaces salientes son de afiliado: `rel="sponsored"`, abren en pestaña nueva.
- Datos por producto: `id`, `t` (título de ML), `o` (precio original), `n` (precio actual), `i` (imagen de mlstatic), `link`. No hay datos de envío, vendedor, reseñas ni stock.

Decisiones abiertas:

- Hosting/despliegue del catálogo y cómo llega `ofertas.json` de la laptop del Radar al sitio publicado.
- Categorías reales: hoy son 5 fijas en código (Audífonos, Monitores, Teclados, Smartwatch, Bocinas) y el menú aún no filtra.
- Qué estadísticas mostrará el Centro de Mando y de dónde saldrán (clics, conversiones de afiliado).
- Si las "píldoras" de envío del catálogo estilo Voltio tendrán dato real; hoy el Radar no lo extrae.

## Brand Commitments

- **Nombre público:** "H | Ofertas" (catálogo). **"Heleos"** es el nombre interno del ecosistema (Radar, Estudio, Centro de Mando).
- **Paleta oficial vinculante:** definida en CLAUDE.md; no introducir colores de marca fuera de ella sin preguntar.
- **Voz:** español de México, directa y breve ("Comprar", "Expiran pronto", "Hoy no hay ofertas nuevas. Vuelve en unas horas.").

## Evidence on Hand

- Ofertas reales en `ofertas.json` (títulos, precios e imágenes de Mercado Libre) y precios diarios en `historial.json`.
- 26 enlaces de afiliado en `enlaces.txt`.
- No hay testimonios, reseñas, cifras de ventas, logos de terceros ni estadísticas de clics. No inventarlos; tampoco afirmar envío gratis, garantías o stock que el Radar no verifica.

## Product Principles

1. **El precio es la verdad.** Todo número mostrado sale del Radar; nunca se fabrica un descuento ni un "antes".
2. **Decidir en segundos.** El comprador viene de TikTok en el celular: producto, precio, ahorro y botón, sin fricción, mobile-first.
3. **Un solo destino.** Cada superficie pública empuja al clic de afiliado hacia Mercado Libre; nada compite con él.
4. **Ligero de punta a punta.** El Radar vive en 4 GB y el sitio es estático; la sencillez es una restricción, no una etapa.
5. **El dueño opera solo.** El Centro de Mando prioriza velocidad y claridad para una persona que repite el mismo ciclo todos los días.

## Accessibility & Inclusion

Respetar `prefers-reduced-motion` (el catálogo ya lo hace) y foco visible en enlaces y botones. Uso táctil en celular como caso principal. No se estableció un estándar formal (p. ej., WCAG AA) como requisito.
