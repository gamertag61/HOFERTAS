/* Nombres comerciales de los productos, compartidos por index.html, panel_h7x_secreto.html y app.html.
   NOMBRES va por enlace de afiliado y sobrevive a cada actualización de ofertas.json.
   Para un producto nuevo: agrega aquí su enlace; si no está, se usa p.nombre o el recorte automático. */
window.NOMBRES = {
  'https://meli.la/31Pgsbw': 'Teclado Magnético Aula Win60 HE',
  'https://meli.la/2XiVSGp': 'Teclado Inalámbrico Mecánico Attack Shark X85',
  'https://meli.la/1BTQ3gk': 'Monitor Gamer LG UltraGear 24" 144 Hz',
  'https://meli.la/2CrimQa': 'Monitor Gamer Curvo 24" Adir',
  'https://meli.la/1roJ5aB': 'Monitor Portátil Arzopa A1 15"',
  'https://meli.la/1c3APAY': 'Monitor Gamer Xiaomi G27i 27" 165 Hz',
  'https://meli.la/2wfe9sS': 'Mouse Gaming Logitech G203',
  'https://meli.la/2W8Y1Hs': 'Mouse Inalámbrico Silencioso Recargable',
  'https://meli.la/2tkpTJg': 'Escritorio Gamer en L Tielopa',
  'https://meli.la/2tHSan9': 'Escritorio de Oficina con Estantería',
  'https://meli.la/2fdwXJB': 'Escritorio Gamer en L con Luces RGB',
  'https://meli.la/1yqVWgS': 'Escritorio Gamer en L con Soporte para Monitor',
  'https://meli.la/2TgQfrM': 'Escritorio Librero Ejecutivo',
  'https://meli.la/1njdMMx': 'Escritorio Home Office Negro Mate',
  'https://meli.la/1t8NUEe': 'Silla de Oficina Ergonómica con Soporte Lumbar',
  'https://meli.la/2UL7Zk8': 'Lámpara de Escritorio Giratoria 360°',
  'https://meli.la/2Nu8c5R': 'Bocinas para PC con Subwoofer RGB',
  'https://meli.la/143CXmW': 'Procesador AMD Ryzen 7 5700X',
  'https://meli.la/2mrYvFT': 'Procesador AMD Ryzen 5 5500',
  'https://meli.la/1cJLBjz': 'Lámpara de Buró LED con USB-C',
  'https://meli.la/1C5wWyp': 'Soporte para Tablet Plegable 360°',
  'https://meli.la/2TWBd3D': 'Control GameSir Kaleid para Xbox y PC',
  'https://meli.la/2iJyZxj': 'Control GameSir G7 Pro para Xbox y PC',
  'https://meli.la/15C8wq7': 'Control GameSir Kaleid Flux para Xbox y PC',
  'https://meli.la/2pZcUyu': 'Audífonos Anker Soundcore Q11i Bluetooth'
};

/* Nombre comercial corto: primero NOMBRES, luego p.nombre si viene en ofertas.json;
   si no, toma el título de Mercado Libre hasta el modelo (máx. 6 palabras) y corta antes de
   cantidades, "con", "para", "RGB"… ("Teclado Inalámbrico Mecánico Attack Shark X85 Pro 82 Teclas…"
   → "Teclado Inalámbrico Mecánico Attack Shark X85"). */
window.nombreComercial = function (p) {
  if (window.NOMBRES[p.link]) return window.NOMBRES[p.link];
  if (p.nombre) return p.nombre;
  const pal = p.t.split(/[,|(–]| - /)[0].trim().split(/\s+/), out = [];
  for (const w of pal) {
    if (out.length >= 3 && /^(con|para|de|del|y|sin|rgb|led|\d+(\.\d+)?)$/i.test(w)) break;
    out.push(w);
    if (out.length === 6) break;
  }
  return out.join(' ').replace(/\s+(en|de|del|con|para|y|la|el)$/i, '');
};
