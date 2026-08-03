/* Desempenho dos jogos do sistema — injetado no Cockpit */
(function () {
  if (window.__desempCockpitLoaded) return;
  window.__desempCockpitLoaded = true;

  function ensureStyles() {
    if (document.getElementById('desemp-styles')) return;
    const s = document.createElement('style');
    s.id = 'desemp-styles';
    s.textContent = `
      .desemp-wrap{margin-top:12px}
      .desemp-chart{display:flex;align-items:flex-end;gap:4px;height:140px;padding:8px 4px 0;border-bottom:1px solid var(--line,#e9dffb);overflow-x:auto}
      .desemp-col{flex:0 0 28px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%;min-width:26px}
      .desemp-bar{width:100%;border-radius:6px 6px 2px 2px;background:linear-gradient(180deg,#a78bfa,#6d28d9);min-height:2px;transition:height .2s}
      .desemp-bar.hi{background:linear-gradient(180deg,#86efac,#15803d)}
      .desemp-bar.mid{background:linear-gradient(180deg,#fde68a,#b45309)}
      .desemp-bar.lo{background:linear-gradient(180deg,#fecaca,#be123c)}
      .desemp-bar.empty{background:#e9dffb}
      .desemp-lab{font-size:9px;color:var(--muted,#74658d);margin-top:4px;font-weight:700}
      .desemp-val{font-size:9px;font-weight:800;color:var(--ink,#21153a);margin-bottom:2px}
      .desemp-legend{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;font-size:11px;color:var(--muted,#74658d)}
      .desemp-legend span{display:inline-flex;align-items:center;gap:4px}
      .desemp-dot{width:10px;height:10px;border-radius:3px;display:inline-block}
    `;
    document.head.appendChild(s);
  }

  function ensureCard() {
    if (document.getElementById('desempCard')) return document.getElementById('desempCard');
    const panel = document.getElementById('panel-hoje');
    if (!panel) return null;
    const card = document.createElement('div');
    card.className = 'card desemp-wrap';
    card.id = 'desempCard';
    card.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
        <h2 style="margin:0">Desempenho M1–M9</h2>
        <button class="btn soft" type="button" id="btnDesempReload" style="padding:6px 10px;font-size:11px">Atualizar gráfico</button>
      </div>
      <p class="muted" id="desempNote">Sugestão do sistema × resultado oficial (pontos = dezenas em comum). Baseline aleatório ≈ 9.</p>
      <div class="grid" id="desempMetrics" style="margin-top:8px"></div>
      <div id="desempChart" class="desemp-chart" aria-label="Gráfico melhor acerto por concurso"></div>
      <div class="desemp-legend">
        <span><i class="desemp-dot" style="background:#15803d"></i> melhor ≥ 11</span>
        <span><i class="desemp-dot" style="background:#b45309"></i> 9–10</span>
        <span><i class="desemp-dot" style="background:#be123c"></i> &lt; 9</span>
        <span><i class="desemp-dot" style="background:#e9dffb"></i> sem jogo gravado</span>
      </div>
      <h2 style="margin-top:16px">Ranking dos métodos</h2>
      <div id="desempMetodos" class="muted">—</div>
      <h2 style="margin-top:16px">Últimos concursos</h2>
      <div class="table-wrap" style="max-height:280px">
        <table class="table">
          <thead><tr><th>Concurso</th><th>Melhor</th><th>Média</th><th>11+</th><th>Top método</th></tr></thead>
          <tbody id="desempBody"></tbody>
        </table>
      </div>
    `;
    panel.appendChild(card);
    document.getElementById('btnDesempReload')?.addEventListener('click', () => loadDesempenho(true));
    return card;
  }

  function barClass(melhor, jogos) {
    if (!jogos) return 'empty';
    if (melhor >= 11) return 'hi';
    if (melhor >= 9) return 'mid';
    return 'lo';
  }

  function renderDesempenho(data) {
    ensureStyles();
    ensureCard();
    const note = document.getElementById('desempNote');
    const metrics = document.getElementById('desempMetrics');
    const chart = document.getElementById('desempChart');
    const metodos = document.getElementById('desempMetodos');
    const body = document.getElementById('desempBody');
    if (!chart) return;

    if (note) note.textContent = data.note || 'Sugestão × resultado oficial.';

    const r = data.resumo;
    if (metrics) {
      if (!r) {
        metrics.innerHTML = '<div class="metric"><div class="label">Histórico</div><div class="value">—</div><div class="detail">Ainda sem jogos_sistema nos concursos passados</div></div>';
      } else {
        metrics.innerHTML = [
          ['Concursos', r.concursos_com_jogos, 'com jogos gravados'],
          ['Média melhor', r.media_melhor, 'por concurso'],
          ['Média geral', r.media_media, 'todos os métodos'],
          ['Melhor abs.', r.melhor_absoluto, 'pontos'],
          ['Vezes 11+', r.vezes_11_mais, 'jogos ≥ 11'],
          ['Baseline', r.baseline_aleatorio_aprox, 'aleatório ≈']
        ].map(([l, v, d]) =>
          `<div class="metric"><div class="label">${l}</div><div class="value">${v ?? '—'}</div><div class="detail">${d || ''}</div></div>`
        ).join('');
      }
    }

    const serie = data.serie || [];
    const maxH = 15;
    chart.innerHTML = serie.map((s) => {
      const h = s.jogos ? Math.max(4, Math.round((Number(s.melhor || 0) / maxH) * 120)) : 4;
      const cls = barClass(s.melhor, s.jogos);
      const title = s.jogos
        ? `#${s.concurso}: melhor ${s.melhor} · média ${s.media} · ${s.jogos} jogos`
        : `#${s.concurso}: sem jogos do sistema`;
      return `<div class="desemp-col" title="${title}">
        <div class="desemp-val">${s.jogos ? s.melhor : '·'}</div>
        <div class="desemp-bar ${cls}" style="height:${h}px"></div>
        <div class="desemp-lab">${String(s.concurso).slice(-3)}</div>
      </div>`;
    }).join('') || '<p class="muted">Sem série.</p>';

    if (metodos) {
      const pm = data.por_metodo || [];
      if (!pm.length) {
        metodos.innerHTML = '<p class="muted">Sem ranking ainda — precisa de jogos_sistema em concursos já sorteados.</p>';
      } else {
        metodos.innerHTML = pm.map((m) => {
          const short = String(m.metodo || '').replace(/^M\d+_/, (x) => x);
          return `<div style="margin:6px 0;display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap">
            <span><b>${short}</b> · ${m.jogos} jogos</span>
            <span>média <b>${m.media}</b> · melhor ${m.melhor} · 11+ ${m.taxa_11_mais}%</span>
          </div>`;
        }).join('');
      }
    }

    if (body) {
      const recent = (data.serie_recente || []).filter((s) => s.jogos > 0).slice(0, 20);
      body.innerHTML = recent.length
        ? recent.map((s) => {
            const top = (s.metodos || [])[0];
            return `<tr>
              <td>#${s.concurso}</td>
              <td><span class="badge ${s.melhor >= 11 ? 'ok' : s.melhor >= 9 ? 'warn' : 'neu'}">${s.melhor}</span></td>
              <td>${s.media ?? '—'}</td>
              <td>${s.acertos_11_mais || 0}</td>
              <td>${top ? top.metodo + ' (' + top.acertos + ')' : '—'}</td>
            </tr>`;
          }).join('')
        : '<tr><td colspan="5">Ainda sem histórico de jogos do sistema conferidos. Após cada sorteio + ciclo, a linha entra aqui.</td></tr>';
    }
  }

  async function loadDesempenho(force) {
    try {
      ensureCard();
      const r = await fetch('/api/sistema/desempenho?limit=30&t=' + Date.now(), { cache: 'no-store' });
      const data = await r.json().catch(() => ({}));
      if (!r.ok || data.ok === false) throw new Error(data.message || 'Falha desempenho');
      renderDesempenho(data);
      if (force && typeof setStatus === 'function') setStatus('Gráfico desempenho atualizado');
    } catch (e) {
      ensureCard();
      const note = document.getElementById('desempNote');
      if (note) note.textContent = 'Erro ao carregar desempenho: ' + (e.message || e);
    }
  }

  // carrega após o painel subir
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => setTimeout(loadDesempenho, 600));
  } else {
    setTimeout(loadDesempenho, 600);
  }

  // re-carrega quando o usuário clica em Atualizar rápido
  document.getElementById('btnRefresh')?.addEventListener('click', () => setTimeout(loadDesempenho, 400));

  window.loadDesempenhoSistema = loadDesempenho;
})();
