/* Misiones de inventario (panel y app): vista superpuesta que solo se abre con un botón [data-misiones].
   Lee misiones.json (lo genera el asesor) y lo dibuja como lista de tareas; lo marcado se guarda en este navegador. */
(() => {
  const CLAVE = 'heleos.misiones';
  const esc = t => String(t ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const leer = () => { try { return JSON.parse(localStorage.getItem(CLAVE)) || {}; } catch { return {}; } };
  const guardar = v => { try { localStorage.setItem(CLAVE, JSON.stringify(v)); } catch {} };
  const ml = q => 'https://listado.mercadolibre.com.mx/' + encodeURIComponent(q.toLowerCase().trim().replace(/\s+/g, '-'));

  document.head.insertAdjacentHTML('beforeend', `<style>
    #misiones { opacity: 0; visibility: hidden; transition: opacity .22s ease, visibility 0s linear .22s; }
    #misiones.abierto { opacity: 1; visibility: visible; transition: opacity .22s ease; }
    #misiones .hoja-m { translate: 100% 0; transition: translate .38s cubic-bezier(.16,1,.3,1); }
    #misiones.abierto .hoja-m { translate: 0 0; }
    #misiones .tarea { transition: border-color .2s ease, opacity .2s ease; }
    #misiones .tarea.hecha { opacity: .55; }
    #misiones .tarea.hecha .t-sug { text-decoration: line-through; text-decoration-color: rgba(198,241,53,.7); }
    #misiones .marca { transition: background-color .18s ease, border-color .18s ease, transform .16s cubic-bezier(.16,1,.3,1); }
    #misiones .marca:active { transform: scale(.9); }
    #misiones .marca svg { opacity: 0; scale: .6; transition: opacity .16s ease, scale .2s cubic-bezier(.16,1,.3,1); }
    #misiones .hecha .marca { background: #c6f135; border-color: #c6f135; color: #0a0b0d; }
    #misiones .hecha .marca svg { opacity: 1; scale: 1; }
    #m-lista { scrollbar-width: thin; scrollbar-color: #2c3037 transparent; }
    #m-barra { transition: width .4s cubic-bezier(.16,1,.3,1); }
    @media (prefers-reduced-motion: reduce) { #misiones, #misiones .hoja-m, #misiones .tarea, #misiones .marca, #misiones .marca svg, #m-barra { transition: none; } }
  </style>`);

  document.body.insertAdjacentHTML('beforeend', `
  <div id="misiones" role="dialog" aria-modal="true" aria-labelledby="m-titulo" class="fixed inset-0 z-40 flex justify-end bg-black/60 backdrop-blur-[2px]">
    <section class="hoja-m flex h-[100dvh] w-full max-w-md flex-col border-l border-linea bg-grafito">
      <header class="flex shrink-0 items-start gap-3 border-b border-linea px-5 pb-4 pt-[max(20px,env(safe-area-inset-top))]">
        <div class="min-w-0 flex-1">
          <h2 id="m-titulo" class="text-xl font-bold tracking-tight">Misiones de inventario</h2>
          <p id="m-origen" class="num mt-1 font-mono text-xs text-humo">Cargando…</p>
        </div>
        <button id="m-cerrar" type="button" aria-label="Cerrar misiones" class="press -mr-1 grid h-11 w-11 shrink-0 place-items-center rounded-full border border-linea text-zinc-200 hover:bg-white/5">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
        </button>
      </header>
      <div id="m-progreso" class="hidden shrink-0 px-5 pt-4">
        <div class="flex items-baseline justify-between text-xs"><span class="text-humo">Progreso</span><span id="m-cuenta" class="num font-mono text-lima"></span></div>
        <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-alto"><div id="m-barra" class="h-full w-0 rounded-full bg-lima"></div></div>
      </div>
      <ol id="m-lista" class="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto px-4 py-4 sm:px-5" aria-live="polite"></ol>
      <footer id="m-catalogo" class="hidden shrink-0 border-t border-linea px-5 pb-[max(16px,env(safe-area-inset-bottom))] pt-3">
        <p class="text-[11px] font-medium uppercase tracking-[.08em] text-ceniza">Catálogo analizado</p>
        <div id="m-chips" class="-mx-5 mt-2 flex gap-1.5 overflow-x-auto px-5 pb-1 [scrollbar-width:none]"></div>
      </footer>
    </section>
  </div>`);

  const $ = id => document.getElementById(id);
  const capa = $('misiones'), lista = $('m-lista');
  let datos = null, origen = null;

  const idDe = m => (datos?.generado || '') + '|' + m.sugerencia;

  function progreso() {
    const hechas = leer(), ms = datos?.misiones || [];
    const n = ms.filter(m => hechas[idDe(m)]).length;
    $('m-progreso').classList.toggle('hidden', !ms.length);
    $('m-cuenta').textContent = `${n}/${ms.length} completadas`;
    $('m-barra').style.width = ms.length ? `${(n / ms.length) * 100}%` : '0';
  }

  function vacio(titulo, texto) {
    lista.innerHTML = `<li class="rounded-2xl border border-dashed border-linea px-5 py-8 text-center">
      <p class="text-sm font-semibold text-zinc-200">${esc(titulo)}</p><p class="mt-1 text-xs text-humo">${esc(texto)}</p></li>`;
  }

  function dibujar() {
    const ms = datos?.misiones || [];
    const fecha = datos?.generado ? new Date(datos.generado) : null;
    $('m-origen').textContent = fecha && !isNaN(fecha)
      ? `Generadas el ${fecha.toLocaleDateString('es-MX', { day: 'numeric', month: 'short' })}, ${fecha.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })}${datos.nicho ? ' · ' + datos.nicho : ''}`
      : 'Sugerencias para equilibrar el catálogo';
    if (!ms.length) { vacio('Aún no hay misiones', 'Cuando se generen aparecerán aquí como lista de tareas.'); progreso(); return; }
    const hechas = leer();
    lista.innerHTML = ms.map((m, i) => `
      <li class="tarea ${hechas[idDe(m)] ? 'hecha' : ''} flex gap-3.5 rounded-2xl border border-linea bg-mate p-4" data-i="${i}">
        <button type="button" class="marca mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full border-2 border-[#3a3f47]" role="checkbox" aria-checked="${!!hechas[idDe(m)]}" aria-label="Marcar «${esc(m.sugerencia)}» como conseguida">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>
        </button>
        <div class="min-w-0 flex-1">
          <p class="num font-mono text-[11px] text-ceniza">Misión ${String(i + 1).padStart(2, '0')}</p>
          <h3 class="t-sug mt-0.5 text-base font-bold leading-snug tracking-tight text-zinc-50">${esc(m.sugerencia)}</h3>
          <p class="mt-1 text-[13px] leading-relaxed text-humo">${esc(m.motivo)}</p>
          <a href="${ml(m.sugerencia)}" target="_blank" rel="noopener" class="press mt-3 inline-flex items-center gap-1.5 rounded-full border border-linea px-3.5 py-2 text-xs font-semibold text-lima hover:border-lima/50">
            Buscar en Mercado Libre
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17L17 7M9 7h8v8"/></svg>
          </a>
        </div>
      </li>`).join('');
    const cats = datos.catalogo || [];
    $('m-catalogo').classList.toggle('hidden', !cats.length);
    $('m-chips').innerHTML = cats.map(c => `<span class="num shrink-0 whitespace-nowrap rounded-full border border-linea px-2.5 py-1 font-mono text-[11px] text-humo">${esc(c.categoria)} <span class="text-zinc-200">${c.total}</span></span>`).join('');
    progreso();
  }

  async function cargar() {
    lista.innerHTML = [0, 1, 2].map(() => '<li class="esq h-32 rounded-2xl" aria-hidden="true"></li>').join('');
    try {
      const r = await fetch('misiones.json', { cache: 'no-store' });
      if (r.status === 404) { datos = { misiones: [] }; return dibujar(); }
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const j = await r.json();
      datos = Array.isArray(j) ? { misiones: j } : j;  // también acepta la lista sola
      dibujar();
    } catch (e) {
      $('m-origen').textContent = 'Sin conexión';
      vacio('No se pudieron cargar las misiones', 'Revisa tu conexión y vuelve a abrir esta vista.');
    }
  }

  function abrir(boton) {
    origen = boton;
    capa.classList.add('abierto');
    document.querySelectorAll('[data-misiones]').forEach(b => b.setAttribute('aria-expanded', 'true'));
    setTimeout(() => $('m-cerrar').focus(), 60);
    cargar();
  }

  function cerrar() {
    capa.classList.remove('abierto');
    document.querySelectorAll('[data-misiones]').forEach(b => b.setAttribute('aria-expanded', 'false'));
    origen?.focus();
  }

  document.querySelectorAll('[data-misiones]').forEach(b => {
    b.setAttribute('aria-controls', 'misiones');
    b.setAttribute('aria-expanded', 'false');
    b.addEventListener('click', () => abrir(b));
  });
  $('m-cerrar').addEventListener('click', cerrar);
  capa.addEventListener('click', e => { if (e.target === capa) cerrar(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && capa.classList.contains('abierto')) cerrar(); });
  lista.addEventListener('click', e => {
    const marca = e.target.closest('.marca');
    if (!marca || !datos) return;
    const li = marca.closest('.tarea'), m = datos.misiones[+li.dataset.i], hechas = leer(), id = idDe(m);
    if (hechas[id]) delete hechas[id]; else hechas[id] = Date.now();
    guardar(hechas);
    li.classList.toggle('hecha', !!hechas[id]);
    marca.setAttribute('aria-checked', String(!!hechas[id]));
    progreso();
  });
})();
