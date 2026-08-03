/* Sugestão do dia — ranking prioritário no Cockpit */
(function () {
  if (window.__sugestaoDiaLoaded) return;
  window.__sugestaoDiaLoaded = true;

  function ensureStyles() {
    if (document.getElementById('sugestao-styles')) return;
    const s = document.createElement('style');
    s.id = 'sugestao-styles';
    s.textContent = `
      .sugestao-card{margin-top:12px;border:2px solid #c4b5fd;background:linear-gradient(180deg,#faf5ff,#fff)}
      .sugestao-tier{margin-top:12px}
      .sugestao-tier h3{font:800 12px Sora,sans-serif;margin:0 0 8px;text-transform:uppercase;letter-spacing:.06em;color:#6d28d9}
      .sugestao-tier.prio h3{color:#15803d}
      .sugestao-tier.div h3{color:#b45309}
      .sugestao-tier.exp h3{color:#74658d}
      .sugestao-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}
      .sugestao-item{border:1px solid var(--line,#e9dffb);border-radius:12px;padding:12px;background:#fff}
      .sugestao-item.prio{border-color:#86efac;box-shadow:0 4px 16px rgba(21,128,61,.08)}
      .sugestao-item .top{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px;font-size:12px;font-weight:800}
      .sugestao-blocked{padding:14px;border-radius:12px;background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;font-size:13px;line-height:1.5}
    `;
    document.head.appendChild(s);
  }

  function balls(dezenas) {
    return `<div class="dezenas">${(dezenas || []).map((d) =>
      `<span class="ball">${String(d).padStart(2, '0')}</span>`
    ).join('')}</div>`;
  }

  function linha(j) {
    if (j.dezenas_texto) return j.dezenas_texto;
    return (j.dezenas || []).map((d) => String(d).padStart(2, '0')).join('-');
  }

  function ensureCard() {
    if (document.getElementById('sugestaoCard')) return document.getElementById('sugestaoCard');
    const panel = document.getElementById('panel-hoje');
    if (!panel) return null;

    const card = document.createElement('div');
    card.className = 'card sugestao-card';
    card.id = 'sugestaoCard';

    // inserir no topo do painel (após metrics / honest)
    const honest = panel.querySelector('.honest');
    if (honest && honest.nextSibling) {
      panel.insertBefore(card, honest.nextSibling);
    } else {
      panel.insertBefore(card, panel.firstChild?.nextSibling || null);
    }

    card.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
        <h2 style="margin:0">Sugestão do dia</h2>
        <div class="actions" style="margin:0">
          <button class="btn soft" type="button" id="btnSugCopyTop" style="padding:6px 10px;font-size:11px">Copiar prioritários</button>
          <button class="btn soft" type="button" id="btnSugCopyAll" style="padding:6px 10px;font-size:11px">Copiar todos</button>
          <button class="btn soft" type="button" id="btnSugReload" style="padding:6px 10px;font-size:11px">Atualizar</button>
        </div>
      </div>
      <p class="muted" id="sugestaoNote" style="margin-top:8px">Carteira ranqueada (histórico + lab). Não é previsão de prêmio.</p>
      <div id="sugestaoBody"></div>
    `;

    document.getElementById('btnSugReload')?.addEventListener('click', () => loadSugestao(true));
    document.getElementById('btnSugCopyTop')?.addEventListener('click', () => copyTier('prioritario'));
    document.getElementById('btnSugCopyAll')?.addEventListener('click', () => copyTier('all'));
    return card;
  }

  let lastData = null;

  async function copyTier(which) {
    const d = lastData;
    if (!d?.todos?.length) {
      if (typeof setStatus === 'function') setStatus('Sem jogos para copiar.', true);
      return;
    }
    let list = d.todos;
    if (which === 'prioritario') list = d.prioritarios || list.slice(0, 3);
    const text = list.map(linha).filter(Boolean).join('\n');
    try {
      if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(text);
      else {
        const ta = document.createElement('textarea');
        ta.value = text; document.body.appendChild(ta); ta.select();
        document.execCommand('copy'); document.body.removeChild(ta);
      }
      if (typeof setStatus === 'function') setStatus('Copiado: ' + list.length + ' sequência(s)');
    } catch (e) {
      if (typeof setStatus === 'function') setStatus(e.message || String(e), true);
    }
  }

  function renderItem(j, prio) {
    const hist = j.hist_media != null
      ? `hist média ${j.hist_media} · 11+ ${j.hist_taxa_11 ?? '—'}%`
      : 'sem histórico';
    return `<div class="sugestao-item ${prio ? 'prio' : ''}">
      <div class="top">
        <span>#${j.rank_pos || '—'} · ${j.metodo}</span>
        <span class="badge ${prio ? 'ok' : 'neu'}">${j.camada || ''}</span>
      </div>
      ${balls(j.dezenas)}
      <div class="muted" style="margin-top:6px;font-family:ui-monospace,Consolas,monospace">${linha(j)}</div>
      <div class="muted" style="margin-top:4px">score ${j.score ?? '—'} · ${hist}</div>
      <div class="actions" style="margin-top:8px">
        <button class="btn soft" type="button" data-copy-linha="${encodeURIComponent(linha(j))}" style="padding:4px 8px;font-size:11px">Copiar</button>
      </div>
    </div>`;
  }

  function renderSugestao(data) {
    ensureStyles();
    ensureCard();
    lastData = data;
    const body = document.getElementById('sugestaoBody');
    const note = document.getElementById('sugestaoNote');
    if (!body) return;

    if (data.blocked || data.gate_blocked) {
      body.innerHTML = `<div class="sugestao-blocked">
        <b>Sugestão indisponível</b><br>
        ${data.message || 'Cérebro bloqueado — atualize o checkpoint operacional.'}
        <div style="margin-top:8px;font-size:12px">Rode: <code>python scripts/publicar_checkpoint.py</code> → commit → deploy</div>
      </div>`;
      if (note) note.textContent = data.note || 'Checkpoint desatualizado.';
      return;
    }

    if (!data.todos?.length) {
      body.innerHTML = '<p class="muted">Sem jogos ranqueados para o concurso atual.</p>';
      return;
    }

    if (note) {
      note.textContent = `Concurso #${data.concurso || '—'} · ${data.note || ''}`
        + (data.lab_hint ? ` · Lab: ${data.lab_hint}` : '')
        + (data.checkpoint_hash ? ` · hash ${String(data.checkpoint_hash).slice(0, 10)}…` : '');
    }

    const p = data.prioritarios || [];
    const d = data.diversificacao || [];
    const e = data.exploracao || [];

    body.innerHTML = `
      <div class="sugestao-tier prio">
        <h3>Prioritários (top 3)</h3>
        <div class="sugestao-grid">${p.map((j) => renderItem(j, true)).join('') || '—'}</div>
      </div>
      <div class="sugestao-tier div">
        <h3>Diversificação</h3>
        <div class="sugestao-grid">${d.map((j) => renderItem(j, false)).join('') || '—'}</div>
      </div>
      <div class="sugestao-tier exp">
        <h3>Exploração / baseline</h3>
        <div class="sugestao-grid">${e.map((j) => renderItem(j, false)).join('') || '—'}</div>
      </div>
    `;

    body.querySelectorAll('[data-copy-linha]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const t = decodeURIComponent(btn.getAttribute('data-copy-linha') || '');
        try {
          if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(t);
          if (typeof setStatus === 'function') setStatus('Sequência copiada');
        } catch (err) {
          if (typeof setStatus === 'function') setStatus(String(err.message || err), true);
        }
      });
    });
  }

  async function loadSugestao(force) {
    try {
      ensureCard();
      const r = await fetch('/api/sistema/sugestao?t=' + Date.now(), { cache: 'no-store' });
      const data = await r.json().catch(() => ({}));
      if (!r.ok && data.ok === false && !data.blocked) {
        throw new Error(data.message || 'Falha sugestão');
      }
      renderSugestao(data);
      if (force && typeof setStatus === 'function') setStatus('Sugestão do dia atualizada');
    } catch (e) {
      ensureCard();
      const body = document.getElementById('sugestaoBody');
      if (body) body.innerHTML = `<div class="sugestao-blocked">Erro: ${e.message || e}</div>`;
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => setTimeout(loadSugestao, 400));
  } else {
    setTimeout(loadSugestao, 400);
  }

  document.getElementById('btnRefresh')?.addEventListener('click', () => setTimeout(loadSugestao, 500));
  window.loadSugestaoDia = loadSugestao;
})();
