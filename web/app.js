/* Adivina el Bloque - cliente v2 */
(() => {
  const $ = (s) => document.querySelector(s);

  const contenido    = $('#contenido');
  const sidebarGrid  = $('#sidebar-grid');
  const sidebarCount = $('#sidebar-count');
  const meterFill    = $('#meter-fill');
  const statCand     = $('#stat-candidatos');
  const statPreg     = $('#stat-pregunta');
  const statusText   = $('#status-text');

  let session = null;
  let totalInicial = null;
  let preguntaActualIdx = null;
  let pregNum = 0;
  let ultimaPreview = []; // ids de candidatos visibles en el sidebar

  // ---------- helpers ----------
  const escape = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));

  const setStatus = (txt) => { statusText.textContent = txt; };

  async function api(ruta, datos = {}) {
    const r = await fetch(ruta, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    });
    if (!r.ok) throw new Error(`API ${r.status}`);
    return r.json();
  }

  /** Crea un <img> que recorre `urls` hasta encontrar una que cargue.
   *  Si todas fallan, marca el contenedor como `.empty`. */
  function imgConFallback(urls, alt = '') {
    const img = document.createElement('img');
    img.alt = alt;
    img.loading = 'lazy';
    img.decoding = 'async';
    let i = 0;
    const intentar = () => {
      if (i >= urls.length) {
        img.parentElement?.classList.add('empty');
        img.remove();
        return;
      }
      img.src = urls[i++];
    };
    img.addEventListener('error', intentar);
    intentar();
    return img;
  }

  /** Construye un <div class="block-art"> con la textura del bloque. */
  function arteBloque(bloque, { big = false } = {}) {
    const div = document.createElement('div');
    div.className = 'block-art' + (big ? ' big' : '');
    const urls = bloque.textures || [];
    if (urls.length) {
      div.appendChild(imgConFallback(urls, bloque.displayName));
    } else {
      div.classList.add('empty');
    }
    return div;
  }

  // ---------- header / metricas ----------
  function actualizarMetricas(data) {
    if (data.candidatos != null) {
      statCand.textContent = data.candidatos;
      const ratio = totalInicial ? (data.candidatos / totalInicial) : 1;
      meterFill.style.width = `${Math.max(2, ratio * 100)}%`;
    }
  }

  // ---------- sidebar (mosaico de candidatos) ----------
  function renderSidebar(preview) {
    const ids = preview.map((b) => b.id);
    sidebarCount.textContent = preview.length || '—';

    if (!preview.length) {
      sidebarGrid.innerHTML = `
        <p class="sidebar-empty">aparecen cuando queden ≤ 24</p>
      `;
      ultimaPreview = [];
      return;
    }

    // Si la lista anterior y la nueva son el mismo conjunto (orden distinto), no rehacer
    const mismosIds = ids.length === ultimaPreview.length &&
                      ids.every((id, i) => id === ultimaPreview[i]);
    if (mismosIds) return;

    // Animar salida de los descartados, luego rebuild
    const previas = sidebarGrid.querySelectorAll('.tile');
    let demoraSalida = 0;
    previas.forEach((tile) => {
      const tileId = Number(tile.dataset.id);
      if (!ids.includes(tileId)) {
        tile.classList.add('removed');
        demoraSalida = 320;
      }
    });

    setTimeout(() => {
      sidebarGrid.innerHTML = '';
      preview.forEach((b, i) => {
        const tile = document.createElement('div');
        tile.className = 'tile';
        tile.dataset.id = b.id;
        tile.style.animationDelay = `${i * 18}ms`;
        const tooltip = document.createElement('span');
        tooltip.className = 'tooltip';
        tooltip.textContent = b.displayName;
        tile.appendChild(tooltip);
        const urls = b.textures || [];
        if (urls.length) tile.appendChild(imgConFallback(urls, b.displayName));
        else tile.classList.add('empty');
        sidebarGrid.appendChild(tile);
      });
      ultimaPreview = ids;
    }, demoraSalida);
  }

  // ---------- render principal ----------
  function render(html) {
    contenido.innerHTML = html;
    contenido.style.animation = 'none';
    void contenido.offsetHeight;
    contenido.style.animation = 'aparecer 350ms cubic-bezier(.2,.8,.2,1)';
  }

  function tagsBloque(b) {
    const tags = [];
    tags.push(`<span class="tag">${escape(b.material) || 'sin material'}</span>`);
    tags.push(`<span class="tag">dureza ${b.hardness}</span>`);
    if (b.transparent)         tags.push('<span class="tag sky">transparente</span>');
    if (b.emitLight > 0)       tags.push(`<span class="tag amber">luz ${b.emitLight}</span>`);
    if (b.is_family)           tags.push('<span class="tag moss">familia</span>');
    return tags.join('');
  }

  // ---------- pantallas ----------
  function pantallaPregunta(data) {
    pregNum += 1;
    preguntaActualIdx = data.idx;
    statPreg.textContent = pregNum;
    setStatus(`pregunta ${pregNum}`);

    render(`
      <div class="pregunta-num">PREGUNTA #${String(pregNum).padStart(2, '0')}</div>
      <p class="pregunta-texto">${escape(data.texto)}</p>
      <div class="acciones">
        <button class="btn primario" data-respuesta="si">Sí</button>
        <button class="btn peligro" data-respuesta="no">No</button>
        <button class="btn fantasma" data-respuesta="ns">No sé</button>
      </div>
    `);

    contenido.querySelectorAll('[data-respuesta]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const r = btn.dataset.respuesta;
        const respuesta = r === 'si' ? true : r === 'no' ? false : null;
        responder(respuesta);
        contenido.classList.add(respuesta === false ? 'flash-error' : 'flash-ok');
        setTimeout(() => contenido.classList.remove('flash-error', 'flash-ok'), 600);
      });
    });
  }

  function pantallaAdivinanza(data) {
    setStatus('adivinando…');
    const b = data.bloque;
    const card = document.createElement('div');
    card.className = 'block-card big';
    card.appendChild(arteBloque(b, { big: true }));
    const info = document.createElement('div');
    info.innerHTML = `
      <p class="block-name">${escape(b.displayName)}</p>
      <div class="block-meta">${tagsBloque(b)}</div>
    `;
    card.appendChild(info);

    render(`
      <div class="pregunta-num">¿ES ÉSTE?</div>
      <div id="card-mount"></div>
      <div class="acciones">
        <button class="btn primario" data-acerto="si">¡Sí, es ése!</button>
        <button class="btn peligro" data-acerto="no">No</button>
        <button class="btn fantasma" data-acerto="ns">No sé</button>
      </div>
    `);
    $('#card-mount').replaceWith(card);

    contenido.querySelectorAll('[data-acerto]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const r = btn.dataset.acerto;
        const acerto = r === 'si' ? true : r === 'no' ? false : null;
        const data = await api('/api/confirm', { session_id: session, acerto });
        manejar(data);
      });
    });
  }

  function pantallaGanado(data) {
    setStatus('te gané');
    const b = data.bloque;
    const variantes = data.variantes || [];

    render(`
      <div class="resultado win">
        <h2>¡Te gané!</h2>
        <p style="color: var(--bone-dim); margin-bottom: 18px;">
          Tu bloque era…
        </p>
        <div id="card-mount"></div>
        ${variantes.length ? `
          <div class="variantes-block">
            <h3>¿Cuál variante era?</h3>
            <div class="variantes-grid" id="lista-variantes"></div>
          </div>
        ` : ''}
        <div class="acciones" style="margin-top: 28px;">
          <button class="btn primario" id="btn-otra">Otra partida</button>
        </div>
      </div>
    `);

    const card = document.createElement('div');
    card.className = 'block-card big';
    card.appendChild(arteBloque(b, { big: true }));
    const info = document.createElement('div');
    info.innerHTML = `
      <p class="block-name">${escape(b.displayName)}</p>
      <div class="block-meta">${tagsBloque(b)}</div>
    `;
    card.appendChild(info);
    $('#card-mount').replaceWith(card);

    if (variantes.length) {
      const lista = $('#lista-variantes');
      variantes.forEach((v) => {
        const btn = document.createElement('button');
        btn.className = 'variante';
        btn.dataset.id = v.id;
        const sw = document.createElement('span');
        sw.className = 'swatch';
        const urls = v.textures || [];
        if (urls.length) sw.appendChild(imgConFallback(urls, v.displayName));
        btn.appendChild(sw);
        const label = document.createElement('span');
        label.textContent = v.displayName.replace(/^.+? /, ''); // "White Wool" -> "White"
        btn.appendChild(label);
        btn.addEventListener('click', async () => {
          lista.querySelectorAll('.variante').forEach((b) => b.classList.remove('seleccionada'));
          btn.classList.add('seleccionada');
          api('/api/variant', { session_id: session, variant_id: v.id }).catch(() => {});
        });
        lista.appendChild(btn);
      });
    }

    $('#btn-otra').addEventListener('click', iniciar);
  }

  function pantallaPerdido() {
    setStatus('me rendí');
    render(`
      <div class="resultado loss">
        <h2>Me rindo.</h2>
        <p style="color: var(--bone-dim); margin-bottom: 24px;">
          No logré adivinar tu bloque. ¡Bien jugado!
        </p>
        <div class="acciones">
          <button class="btn primario" id="btn-otra">Otra partida</button>
        </div>
      </div>
    `);
    $('#btn-otra').addEventListener('click', iniciar);
  }

  // ---------- flujo ----------
  function manejar(data) {
    actualizarMetricas(data);
    renderSidebar(data.preview || []);
    if (data.fase === 'pregunta')      pantallaPregunta(data);
    else if (data.fase === 'adivinanza') pantallaAdivinanza(data);
    else if (data.fase === 'ganado')   pantallaGanado(data);
    else if (data.fase === 'perdido')  pantallaPerdido();
  }

  async function iniciar() {
    setStatus('iniciando…');
    pregNum = 0;
    statPreg.textContent = 0;
    ultimaPreview = [];
    sidebarGrid.innerHTML = '<p class="sidebar-empty">aparecen cuando queden ≤ 24</p>';
    try {
      const data = await api('/api/start');
      session = data.session_id;
      totalInicial = data.total;
      manejar(data);
    } catch (e) {
      setStatus('error de conexión');
      console.error(e);
    }
  }

  async function responder(respuesta) {
    try {
      const data = await api('/api/answer', {
        session_id: session,
        idx: preguntaActualIdx,
        respuesta,
      });
      manejar(data);
    } catch (e) {
      setStatus('error');
      console.error(e);
    }
  }

  // ---------- atajos de teclado ----------
  document.addEventListener('keydown', (e) => {
    if (e.target.matches('input, textarea')) return;

    if (e.key === 'Enter') {
      const inicio = contenido.querySelector('#btn-iniciar') ||
                     contenido.querySelector('#btn-otra');
      if (inicio) { inicio.click(); return; }
    }
    const map = { s: 'si', n: 'no', x: 'ns' };
    const k = map[e.key.toLowerCase()];
    if (!k) return;
    const btn = contenido.querySelector(
      `[data-respuesta="${k}"], [data-acerto="${k}"]`
    );
    if (btn) btn.click();
  });

  // listener inicial
  $('#btn-iniciar')?.addEventListener('click', iniciar);
})();
