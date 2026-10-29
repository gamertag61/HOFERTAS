/* Carga de ofertas compartida por index.html, dashboard.html y app.html.
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

function deV2(d) {
  const hist = {};
  const productos = (d.productos || []).map(p => {
    hist[p.link] = (p.historial || []).map(([fecha, precio]) => ({ fecha, precio }));
    return { t: p.titulo, n: p.precio.actual, o: p.precio.antes, i: p.imagen, link: p.link, nombre: p.nombre,
             specs: p.specs, categoria: p.categoria, super: p.super_deal, cupon: p.cupon };
  });
  const bajas = (d.bajas || []).map(a => ({ link: a.link, t: a.nombre, i: a.imagen, antes: a.precio_antes,
                                            ahora: a.precio_ahora, fecha: a.ts }));
  return { actualizado: d.actualizado, productos, bajas, hist };
}
