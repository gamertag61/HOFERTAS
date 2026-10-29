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
