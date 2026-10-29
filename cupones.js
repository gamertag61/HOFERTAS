/* Cupones de Mercado Libre, compartido por index.html, panel_h7x_secreto.html y app.html.
   Mercado Libre no tiene API pública de cupones: se escriben a mano en cupones.json y aquí se cruzan con la
   "categoria" que la IA asignó a cada producto.
     await window.cargarCupones()            → cupones activos y vigentes (nunca falla: sin archivo devuelve [])
     window.cuponPara(categoria, cupones)    → el de mayor descuento que aplica a esa categoría, o null
     window.etiquetaCupon(cupon, tamaño)     → badge "🎟️ CODIGO (-15%)" para las tarjetas
     window.pintarCupones(el, cupones, nombresCategoria, categoriasConOferta) → lista compacta (panel y app) */
(() => {
  const esc = t => String(t ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const hoy = new Date().toISOString().slice(0, 10);
  const fecha = f => new Date(f + 'T12:00:00').toLocaleDateString('es-MX', { day: 'numeric', month: 'short' });
  const pctDe = c => Number(c.pct) || parseFloat(String(c.descuento || '').replace(',', '.')) || 0;
  let pedido = null;

  window.cargarCupones = function () {
    return pedido || (pedido = fetch('cupones.json?t=' + Date.now(), { cache: 'no-store' })
      .then(r => r.ok ? r.json() : {})
      .catch(() => ({}))
      .then(cfg => (cfg.cupones || [])
        .filter(c => c.activo && c.codigo && !(c.vence && c.vence < hoy))
        .map(c => ({ ...c, codigo: String(c.codigo).trim().toUpperCase(), pct: pctDe(c), categorias: c.categorias || [] }))
        .sort((a, b) => b.pct - a.pct)));
  };

  window.cuponPara = (categoria, cupones) =>
    (cupones || []).find(c => c.categorias.includes('*') || (categoria && c.categorias.includes(categoria))) || null;

  window.etiquetaCupon = (c, tam = 'sm') => !c ? '' :
    `<span class="cupon-badge num inline-flex max-w-full items-center gap-1 whitespace-nowrap rounded-full border border-dashed border-lima/60 bg-lima/[.08] font-mono font-semibold text-lima ${tam === 'lg' ? 'px-3 py-1 text-xs' : 'px-2 py-0.5 text-[10.5px]'}" title="Cupón ${esc(c.codigo)}${c.pct ? ` · ${c.pct}% de descuento` : ''}${c.detalle ? ' · ' + esc(c.detalle) : ''}">`
    + `<span aria-hidden="true">🎟️</span><span class="truncate">${esc(c.codigo)}</span>${c.pct ? `<span class="text-lima/75">(-${c.pct}%)</span>` : ''}</span>`;

  // Nombres de las categorías de la IA (radar/ia.py), por si la página no tiene datos.json a mano
  const CATEGORIAS = { teclados: 'Teclados', mouse: 'Mouse', monitores: 'Monitores', audio: 'Audio', escritorios: 'Escritorios',
                       sillas: 'Sillas', iluminacion: 'Iluminación', controles: 'Controles', componentes: 'Componentes', accesorios: 'Accesorios' };

  // "Monitores, Teclados" o "Todo el catálogo"
  window.dondeAplica = (c, nombres) => c.categorias.includes('*') ? 'Todo el catálogo'
    : c.categorias.map(id => (nombres && nombres.get(id)) || CATEGORIAS[id] || id.replace(/-/g, ' ').replace(/^./, l => l.toUpperCase())).join(', ');

  window.pintarCupones = function (el, cupones, nombres, conOferta) {
    if (!el) return;
    const lista = cupones.map(c => {
      const enOferta = c.categorias.includes('*') || c.categorias.some(id => conOferta && conOferta.has(id));
      return `<li class="flex items-center gap-2.5 py-2">
        <button type="button" data-copiar="${esc(c.codigo)}" class="press shrink-0 rounded-md border border-dashed border-lima/60 bg-lima/[.08] px-2 py-1 font-mono text-[13px] font-bold text-lima" aria-label="Copiar el código ${esc(c.codigo)}">${esc(c.codigo)}</button>
        <p class="min-w-0 flex-1 truncate text-xs text-humo">
          ${c.pct ? `<span class="num font-mono font-semibold text-zinc-100">-${c.pct}%</span> · ` : ''}${esc(window.dondeAplica(c, nombres))}${c.vence ? ` <span class="text-ceniza">· vence ${esc(fecha(c.vence))}</span>` : ''}
        </p>
        ${enOferta ? '<span class="h-1.5 w-1.5 shrink-0 rounded-full bg-lima" title="Aplica a una caída de precio de hoy"></span>' : ''}
      </li>`;
    }).join('');
    el.innerHTML = `
      <div class="flex items-baseline justify-between gap-3">
        <h2 class="whitespace-nowrap text-sm font-bold tracking-tight">Cupones de Mercado Libre</h2>
        <span class="num whitespace-nowrap font-mono text-[11px] text-humo">${cupones.length} ${cupones.length === 1 ? 'vigente' : 'vigentes'}</span>
      </div>
      ${cupones.length
        ? `<ul class="mt-1 divide-y divide-linea">${lista}</ul><p class="mt-1 text-[11px] text-ceniza">Toca un código para copiarlo. <span class="inline-block h-1.5 w-1.5 rounded-full bg-lima align-middle"></span> aplica a una caída de hoy.</p>`
        : '<p class="mt-1.5 text-xs text-humo">Sin cupones vigentes. Agrégalos en cupones.json con "activo": true.</p>'}`;
    el.hidden = false;
  };

  document.addEventListener('click', async e => {
    const b = e.target.closest('[data-copiar]');
    if (!b) return;
    const codigo = b.dataset.copiar;
    try { await navigator.clipboard.writeText(codigo); b.textContent = '¡Copiado!'; }
    catch (err) { b.textContent = codigo; return; }
    setTimeout(() => { b.textContent = codigo; }, 1400);
  });
})();
