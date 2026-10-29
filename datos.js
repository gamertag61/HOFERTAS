/* Carga de ofertas compartida por index.html, panel_h7x_secreto.html y app.html.
   Lee datos.json (radar v2) y, si todavía no existe, el formato anterior (ofertas.json + historial.json).
   Siempre devuelve la misma forma:
   { actualizado, productos: [{ t, o, n, i, link, nombre?, specs?, categoria?, super?, cupon? }],
     bajas: [{ link, t, i, antes, ahora, fecha }], hist: { link: [{ fecha, precio }] } } */
window.cargarOfertas = async function () {
  const leer = url => fetch(url + '?t=' + Date.now(), { cache: 'no-store' })
    .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); });
  try {
    const d = await leer('datos.json');
    if (d && d.version === 2) return deV2(d);
  } catch (e) { /* aún no hay datos.json: se usa el formato anterior */ }
  const [d, hist] = await Promise.all([leer('ofertas.json'), leer('historial.json').catch(() => ({}))]);
  return { actualizado: d.actualizado, productos: d.productos || [], bajas: d.alertas || [], hist: hist || {} };
};

/* Panel y app: lee SOLO alertas.json (caídas reales vigentes que filtró el radar, con la categoría y specs de la IA).
   "o" es el precio anterior medido por el radar, nunca el tachado del vendedor.
   Devuelve { actualizado, alertas: [{ t, o, n, i, link, nombre, specs, categoria, categoriaNombre, super, cupon, caida }] } */
window.cargarAlertas = async function () {
  const r = await fetch('alertas.json?t=' + Date.now(), { cache: 'no-store' });
  if (!r.ok) throw new Error(r.status);
  const d = await r.json();
  const alertas = (d.alertas || []).map(a => {
    const tipo = a.tipo || 'super';  // alertas.json anterior: solo traía súper ofertas
    return { t: a.titulo || a.nombre, o: a.precio_antes, n: a.precio_actual ?? a.precio_ahora, i: a.imagen, link: a.link,
             nombre: a.nombre, specs: a.specs, categoria: a.categoria, categoriaNombre: a.categoria_nombre || a.categoria,
             super: tipo === 'super', cupon: a.cupon, caida: { tipo, fecha: a.ts } };
  }).filter(a => a.o > a.n);
  return { actualizado: d.actualizado, alertas };
};

/* Relleno para que el feed nunca se quede vacío (5 videos diarios): con 5 o más caídas reales se usan tal cual;
   con menos, se completa hasta exactamente `minimo` con productos del catálogo (datos.json) marcados como destacados.
   Los destacados NO llevan precio anterior ni descuento (o = null, relleno = true): no se inventa ninguna baja.
   Se eligen de categorías distintas y rotan cada día para no repetir siempre los mismos. */
window.completarConDestacados = function (caidas, productos, minimo = 5) {
  if (caidas.length >= minimo) return caidas;
  const usados = new Set(caidas.map(p => p.link));
  const pool = (productos || [])
    .filter(p => p && !usados.has(p.link) && p.n > 0 && /^https:\/\//.test(p.link) && p.i)
    .sort((a, b) => (b.specs?.length || 0) - (a.specs?.length || 0) || String(a.link).localeCompare(String(b.link)));
  if (!pool.length) return caidas;
  const dia = Math.floor(Date.now() / 864e5), inicio = dia % pool.length;
  const rotado = pool.slice(inicio).concat(pool.slice(0, inicio));
  const elegidos = [], cats = new Set(caidas.map(p => p.categoria));
  for (const p of rotado) if (elegidos.length + caidas.length < minimo && !cats.has(p.categoria)) { elegidos.push(p); cats.add(p.categoria); }
  for (const p of rotado) if (elegidos.length + caidas.length < minimo && !elegidos.includes(p)) elegidos.push(p);
  return caidas.concat(elegidos.map(p => ({ ...p, o: null, super: false, caida: null, relleno: true })));
};

function deV2(d) {
  const hist = {};
  const productos = (d.productos || []).map(p => {
    hist[p.link] = (p.historial || []).map(([fecha, precio]) => ({ fecha, precio }));
    return { t: p.titulo, n: p.precio.actual, o: p.precio.antes, i: p.imagen, link: p.link, nombre: p.nombre,
             specs: p.specs, categoria: p.categoria, super: p.super_deal, cupon: p.cupon };
  });
  const bajas = (d.bajas || []).map(a => ({ link: a.link, t: a.nombre, i: a.imagen, antes: a.precio_antes,
                                            ahora: a.precio_ahora, fecha: a.ts }));
  return { actualizado: d.actualizado, productos, bajas, hist, categorias: d.categorias || [] };
}
