import historicalWorker from './worker_learning.js';
import { ensureJogosSistemaProvenance, inspectCerebroCheckpoint, applyCerebroOrBlock } from './worker_cerebro_games.js';
import {
  ensureSugestaoSchema,
  computeMethodScores,
  buildSugestaoDoDia,
  saveSugestaoSnapshot,
  extractLabHint
} from './worker_sugestao_dia.js';

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      'access-control-allow-origin': '*'
    }
  });
}

const COCKPIT_ROUTES = new Set([
  '/painel', '/painel.html', '/cockpit',
  '/painel_cockpit', '/painel_cockpit.html',
  '/painel_avancado', '/painel_avancado.html',
  '/painel_mobile', '/painel_mobile.html'
]);

const APRENDIZADO_ROUTES = new Set([
  '/aprend', '/aprendizado', '/aprendizado.html'
]);

function assetRequest(request, url, pathname) {
  const assetUrl = new URL(request.url);
  assetUrl.pathname = pathname;
  assetUrl.search = url.search;
  return new Request(assetUrl.toString(), { method: 'GET', headers: request.headers });
}

function dezenasTexto(dezenas) {
  return (dezenas || []).map((d) => String(d).padStart(2, '0')).join('-');
}

function scoreSet(dezenas) {
  const soma = (dezenas || []).reduce((t, d) => t + Number(d), 0);
  const pares = (dezenas || []).filter((d) => Number(d) % 2 === 0).length;
  return { soma, pares, impares: (dezenas || []).length - pares };
}

function countHits(jogoDezenas, sorteadas) {
  const set = new Set((sorteadas || []).map(Number));
  return (jogoDezenas || []).filter((d) => set.has(Number(d))).length;
}

async function safeFirst(env, sql, binds = []) {
  try {
    const stmt = env.DB.prepare(sql);
    return binds.length ? await stmt.bind(...binds).first() : await stmt.first();
  } catch (err) {
    console.error('safeFirst', err?.message || err);
    return null;
  }
}

async function safeAll(env, sql, binds = []) {
  try {
    const stmt = env.DB.prepare(sql);
    const rows = binds.length ? await stmt.bind(...binds).all() : await stmt.all();
    return rows?.results || [];
  } catch (err) {
    console.error('safeAll', err?.message || err);
    return [];
  }
}

async function ensureAppSchema(env) {
  if (!env?.DB) return;
  const alters = [
    'ALTER TABLE jogos ADD COLUMN manter_salvo INTEGER NOT NULL DEFAULT 0',
    'ALTER TABLE jogos ADD COLUMN descartar_apos_rodadas INTEGER NOT NULL DEFAULT 2',
    'ALTER TABLE conferencias ADD COLUMN dezenas_jogadas TEXT',
    'ALTER TABLE conferencias ADD COLUMN dezenas_acertadas TEXT',
    'ALTER TABLE conferencias ADD COLUMN metodo TEXT',
    'ALTER TABLE jogos_sistema ADD COLUMN origem TEXT',
    'ALTER TABLE jogos_sistema ADD COLUMN cerebro_version TEXT',
    'ALTER TABLE jogos_sistema ADD COLUMN checkpoint_hash TEXT',
    'ALTER TABLE jogos_sistema ADD COLUMN audit_brain_version TEXT',
    'ALTER TABLE jogos_sistema ADD COLUMN source_of_truth TEXT',
    'ALTER TABLE jogos_sistema ADD COLUMN checkpoint_generated_at TEXT'
  ];
  for (const sql of alters) {
    try { await env.DB.prepare(sql).run(); } catch { /* ok */ }
  }
  try { await ensureJogosSistemaProvenance(env); } catch (e) { console.error(e); }
  try { await ensureSugestaoSchema(env); } catch (e) { console.error(e); }
}

async function getUserFromRequest(request, env) {
  const header = request.headers.get('authorization') || '';
  const match = header.match(/^Bearer\s+(.+)$/i);
  if (!match) return null;
  return safeFirst(env, `
    SELECT usuarios.id, usuarios.nome, usuarios.email, usuarios.criado_em
    FROM sessoes JOIN usuarios ON usuarios.id = sessoes.usuario_id
    WHERE sessoes.token = ? AND datetime(sessoes.expira_em) > datetime('now')
  `, [match[1].trim()]);
}

async function listJogosSeguro(user, env) {
  await ensureAppSchema(env);
  let rows = await safeAll(env, `
    SELECT id, concurso, metodo, dezenas, dezenas_texto, status, observacao,
           manter_salvo, descartar_apos_rodadas, criado_em, atualizado_em
    FROM jogos WHERE usuario_id = ? ORDER BY datetime(criado_em) DESC LIMIT 1000
  `, [user.id]);
  if (!rows.length) {
    rows = await safeAll(env, `
      SELECT id, concurso, metodo, dezenas, dezenas_texto, status, observacao, criado_em, atualizado_em
      FROM jogos WHERE usuario_id = ? ORDER BY id DESC LIMIT 1000
    `, [user.id]);
  }
  const jogos = rows.map((jogo) => {
    let dezenas = [];
    try { dezenas = JSON.parse(jogo.dezenas || '[]'); } catch { dezenas = []; }
    return {
      id: jogo.id, concurso: jogo.concurso, metodo: jogo.metodo, dezenas,
      dezenas_texto: jogo.dezenas_texto || dezenasTexto(dezenas),
      status: jogo.status || 'salvo', observacao: jogo.observacao || null,
      manter_salvo: Boolean(jogo.manter_salvo),
      descartar_apos_rodadas: Number(jogo.descartar_apos_rodadas || 2),
      criado_em: jogo.criado_em, atualizado_em: jogo.atualizado_em, conferencias: []
    };
  });
  return json({ ok: true, jogos, source: 'bridge_seguro' });
}

async function deleteAllJogosUsuario(user, env) {
  await ensureAppSchema(env);
  const countRow = await safeFirst(env, 'SELECT COUNT(*) AS total FROM jogos WHERE usuario_id = ?', [user.id]);
  const total = Number(countRow?.total || 0);
  if (!total) {
    return json({ ok: true, deleted: 0, message: 'Nenhum jogo para limpar.' });
  }
  try {
    await env.DB.prepare('DELETE FROM conferencias WHERE jogo_id IN (SELECT id FROM jogos WHERE usuario_id = ?)').bind(user.id).run();
  } catch (e) {
    console.error('delete conferencias', e);
  }
  const result = await env.DB.prepare('DELETE FROM jogos WHERE usuario_id = ?').bind(user.id).run();
  const deleted = Number(result?.meta?.changes ?? total);
  return json({ ok: true, deleted, message: 'Área Meus jogos limpa.' });
}

function parseLabRow(row) {
  if (!row) return null;
  const parse = (v, fb) => { try { return v ? JSON.parse(v) : fb; } catch { return fb; } };
  return {
    id: row.id, concurso: row.concurso, quantidade: row.quantidade, seed: row.seed,
    status: row.status, criado_em: row.criado_em, conferido_em: row.conferido_em,
    resumo: parse(row.resumo_json, null), estrategias: parse(row.estrategias_json, []),
    melhor: parse(row.melhor_json, null)
  };
}

function mapJogoSistema(row) {
  let dezenas = [];
  try { dezenas = JSON.parse(row.dezenas || '[]'); } catch { dezenas = []; }
  return {
    concurso: row.concurso, metodo: row.metodo, dezenas, dezenas_texto: row.dezenas_texto,
    soma: row.soma, pares: row.pares, impares: row.impares,
    origem: row.origem || null, cerebro_version: row.cerebro_version || null,
    checkpoint_hash: row.checkpoint_hash || null, audit_brain_version: row.audit_brain_version || null,
    source_of_truth: row.source_of_truth || null, checkpoint_generated_at: row.checkpoint_generated_at || null,
    criado_em: row.criado_em || null
  };
}

function mapGamesFromCheckpoint(games, concurso) {
  return (games || []).map((g) => {
    const stats = scoreSet(g.dezenas);
    return {
      concurso,
      metodo: g.metodo,
      dezenas: g.dezenas,
      dezenas_texto: dezenasTexto(g.dezenas),
      soma: stats.soma,
      pares: stats.pares,
      impares: stats.impares,
      origem: g.origem || 'cerebro_python',
      cerebro_version: g.cerebro_version || null,
      checkpoint_hash: g.checkpoint_hash || null,
      audit_brain_version: g.audit_brain_version || null,
      source_of_truth: g.source_of_truth || 'python',
      checkpoint_generated_at: g.checkpoint_generated_at || null,
      criado_em: null,
      source: 'checkpoint_fallback'
    };
  });
}

async function purgeNonCerebroSistema(env, concurso) {
  try {
    await env.DB.prepare(`
      DELETE FROM jogos_sistema
      WHERE concurso = ?
        AND (origem IS NULL OR origem = '' OR origem != 'cerebro_python')
    `).bind(concurso).run();
  } catch (e) {
    console.error('purgeNonCerebroSistema', e);
  }
}

/** Carrega jogos atuais (D1 cerebro ou checkpoint) e monta sugestão ranqueada. */
async function sugestaoDoDiaApi(env) {
  await ensureAppSchema(env);
  const latest = await safeFirst(env, 'SELECT concurso FROM resultados ORDER BY concurso DESC LIMIT 1');
  const proximo = latest ? Number(latest.concurso) + 1 : 1;

  let gateFull;
  try {
    gateFull = await inspectCerebroCheckpoint(env, proximo);
  } catch (e) {
    gateFull = { status: 'invalid', blocked: true, message: String(e.message || e) };
  }

  if (gateFull.blocked) {
    return json({
      ok: false,
      blocked: true,
      gate_blocked: true,
      concurso: proximo,
      status: gateFull.status,
      message: gateFull.message || 'Cérebro bloqueado',
      prioritarios: [],
      diversificacao: [],
      exploracao: [],
      todos: [],
      note: 'Atualize o checkpoint: python scripts/publicar_checkpoint.py'
    });
  }

  await purgeNonCerebroSistema(env, proximo);

  let jogosRows = await safeAll(env, `
    SELECT concurso, metodo, dezenas, dezenas_texto, soma, pares, impares,
           origem, cerebro_version, checkpoint_hash,
           audit_brain_version, source_of_truth, checkpoint_generated_at, criado_em
    FROM jogos_sistema
    WHERE concurso = ? AND origem = 'cerebro_python'
    ORDER BY metodo
  `, [proximo]);

  let games = jogosRows.map(mapJogoSistema);

  if (!games.length && gateFull.games?.length) {
    games = mapGamesFromCheckpoint(gateFull.games, proximo);
    try {
      await applyCerebroOrBlock(env, proximo);
    } catch (e) {
      console.error(e);
    }
  }

  if (!games.length) {
    return json({
      ok: false,
      blocked: true,
      concurso: proximo,
      message: 'Sem jogos do Cérebro para o concurso atual.',
      prioritarios: [],
      diversificacao: [],
      exploracao: [],
      todos: []
    });
  }

  const stats = await computeMethodScores(env, 30);
  const labHint = await extractLabHint(env);
  const sugestao = buildSugestaoDoDia(games, stats, labHint);

  // snapshot imutável (não sobrescreve)
  try {
    await saveSugestaoSnapshot(env, proximo, sugestao.todos);
  } catch (e) {
    console.error('snapshot sugestao', e);
  }

  return json({
    ok: true,
    blocked: false,
    concurso: proximo,
    cerebro_version: gateFull.cerebro_version || games[0]?.cerebro_version,
    checkpoint_hash: gateFull.checkpoint_hash || games[0]?.checkpoint_hash,
    lab_hint: labHint,
    prioritarios: sugestao.prioritarios,
    diversificacao: sugestao.diversificacao,
    exploracao: sugestao.exploracao,
    todos: sugestao.todos,
    ranking_metodos: sugestao.ranking_metodos,
    note: sugestao.note
  });
}

async function desempenhoSistema(env, limit = 30) {
  await ensureAppSchema(env);
  const lim = Math.min(Math.max(Number(limit) || 30, 5), 80);

  const resultados = await safeAll(env, `
    SELECT concurso, data_sorteio, dezenas, dezenas_texto
    FROM resultados
    ORDER BY concurso DESC
    LIMIT ?
  `, [lim]);

  if (!resultados.length) {
    return json({
      ok: true,
      concursos: [],
      por_metodo: [],
      resumo: null,
      message: 'Sem resultados no D1.'
    });
  }

  const concursosIds = resultados.map((r) => Number(r.concurso));
  const minC = Math.min(...concursosIds);
  const maxC = Math.max(...concursosIds);

  // Preferir snapshot imutável
  let jogosRows = await safeAll(env, `
    SELECT concurso, metodo, dezenas, dezenas_texto, origem, NULL as cerebro_version, checkpoint_hash
    FROM sugestao_dia_snapshot
    WHERE concurso >= ? AND concurso <= ?
    ORDER BY concurso DESC, rank_pos ASC
  `, [minC, maxC]);

  if (!jogosRows.length) {
    jogosRows = await safeAll(env, `
      SELECT concurso, metodo, dezenas, dezenas_texto, origem, cerebro_version, checkpoint_hash
      FROM jogos_sistema
      WHERE concurso >= ? AND concurso <= ?
      ORDER BY concurso DESC, metodo
    `, [minC, maxC]);
  }

  const byConcurso = new Map();
  for (const row of jogosRows) {
    const c = Number(row.concurso);
    if (!byConcurso.has(c)) byConcurso.set(c, []);
    byConcurso.get(c).push(row);
  }

  for (const [c, rows] of byConcurso) {
    const py = rows.filter((r) => r.origem === 'cerebro_python');
    if (py.length) byConcurso.set(c, py);
  }

  const serie = [];
  const metodoAgg = new Map();

  for (const res of resultados) {
    const concurso = Number(res.concurso);
    let sorteadas = [];
    try { sorteadas = JSON.parse(res.dezenas || '[]'); } catch { sorteadas = []; }
    const jogos = byConcurso.get(concurso) || [];

    if (!jogos.length) {
      serie.push({
        concurso,
        data: res.data_sorteio,
        sorteadas_texto: res.dezenas_texto || dezenasTexto(sorteadas),
        jogos: 0,
        melhor: null,
        media: null,
        acertos_11_mais: 0,
        metodos: []
      });
      continue;
    }

    const detalhe = [];
    let somaAcertos = 0;
    let melhor = 0;
    let acertos11 = 0;

    for (const j of jogos) {
      let dez = [];
      try { dez = JSON.parse(j.dezenas || '[]'); } catch { dez = []; }
      const acertos = countHits(dez, sorteadas);
      somaAcertos += acertos;
      if (acertos > melhor) melhor = acertos;
      if (acertos >= 11) acertos11 += 1;

      detalhe.push({
        metodo: j.metodo,
        acertos,
        dezenas_texto: j.dezenas_texto || dezenasTexto(dez),
        origem: j.origem || null
      });

      const key = j.metodo || 'desconhecido';
      const agg = metodoAgg.get(key) || {
        metodo: key,
        jogos: 0,
        soma: 0,
        melhor: 0,
        acertos_11: 0,
        acertos_12: 0,
        acertos_13: 0,
        acertos_14: 0,
        acertos_15: 0
      };
      agg.jogos += 1;
      agg.soma += acertos;
      if (acertos > agg.melhor) agg.melhor = acertos;
      if (acertos === 11) agg.acertos_11 += 1;
      if (acertos === 12) agg.acertos_12 += 1;
      if (acertos === 13) agg.acertos_13 += 1;
      if (acertos === 14) agg.acertos_14 += 1;
      if (acertos === 15) agg.acertos_15 += 1;
      metodoAgg.set(key, agg);
    }

    detalhe.sort((a, b) => b.acertos - a.acertos || String(a.metodo).localeCompare(String(b.metodo)));

    serie.push({
      concurso,
      data: res.data_sorteio,
      sorteadas_texto: res.dezenas_texto || dezenasTexto(sorteadas),
      jogos: jogos.length,
      melhor,
      media: Number((somaAcertos / jogos.length).toFixed(2)),
      acertos_11_mais: acertos11,
      metodos: detalhe
    });
  }

  const serieAsc = serie.slice().reverse();

  const por_metodo = Array.from(metodoAgg.values()).map((m) => ({
    ...m,
    media: m.jogos ? Number((m.soma / m.jogos).toFixed(2)) : 0,
    taxa_11_mais: m.jogos
      ? Number((((m.acertos_11 + m.acertos_12 + m.acertos_13 + m.acertos_14 + m.acertos_15) * 100) / m.jogos).toFixed(1))
      : 0
  })).sort((a, b) => b.media - a.media || b.melhor - a.melhor);

  const comDados = serie.filter((s) => s.jogos > 0);
  const resumo = comDados.length ? {
    concursos_com_jogos: comDados.length,
    concursos_analisados: serie.length,
    media_melhor: Number((comDados.reduce((a, s) => a + s.melhor, 0) / comDados.length).toFixed(2)),
    media_media: Number((comDados.reduce((a, s) => a + s.media, 0) / comDados.length).toFixed(2)),
    vezes_11_mais: comDados.reduce((a, s) => a + s.acertos_11_mais, 0),
    melhor_absoluto: Math.max(...comDados.map((s) => s.melhor)),
    baseline_aleatorio_aprox: 9
  } : null;

  return json({
    ok: true,
    limit: lim,
    serie: serieAsc,
    serie_recente: serie,
    por_metodo,
    resumo,
    note: comDados.length
      ? 'Acertos = snapshot/sugestão × resultado oficial. Média aleatória teórica ≈ 9.'
      : 'Ainda sem histórico. Após cada sorteio com snapshot gravado, o gráfico enriquece.'
  });
}

async function serveCockpit(request, env, url) {
  const asset = await env.ASSETS.fetch(assetRequest(request, url, '/painel_cockpit.html'));
  if (!asset.ok) return asset;
  let html = await asset.text();
  const scripts = [];
  if (!html.includes('sugestao_dia.js')) {
    scripts.push('<script src="/sugestao_dia.js" defer></script>');
  }
  if (!html.includes('desempenho_cockpit.js')) {
    scripts.push('<script src="/desempenho_cockpit.js" defer></script>');
  }
  if (scripts.length) {
    html = html.replace('</body>', scripts.join('\n') + '\n</body>');
  }
  return new Response(html, {
    status: 200,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store'
    }
  });
}

async function sistemaStatusSeguro(env) {
  if (!env?.DB) return json({ ok: false, message: 'Binding D1 ausente.' }, 500);
  await ensureAppSchema(env);

  const totalRow = await safeFirst(env, 'SELECT COUNT(*) AS total FROM resultados');
  const latest = await safeFirst(env, `
    SELECT concurso, data_sorteio, dezenas, dezenas_texto FROM resultados ORDER BY concurso DESC LIMIT 1
  `);

  let ultimo = null;
  let proximo = 1;
  if (latest) {
    let dezenas = [];
    try { dezenas = JSON.parse(latest.dezenas || '[]'); } catch { dezenas = []; }
    ultimo = {
      concurso: latest.concurso, data: latest.data_sorteio, dezenas,
      dezenas_texto: latest.dezenas_texto || dezenasTexto(dezenas)
    };
    proximo = Number(latest.concurso) + 1;
  }

  let gateFull;
  try {
    gateFull = await inspectCerebroCheckpoint(env, proximo);
  } catch (e) {
    gateFull = { status: 'invalid', blocked: true, message: String(e.message || e) };
  }

  let cerebro_gate = gateFull;
  if (cerebro_gate?.games) {
    const { games, ...rest } = cerebro_gate;
    cerebro_gate = { ...rest, jogos: games.length };
  }

  await purgeNonCerebroSistema(env, proximo);

  let jogosRows = await safeAll(env, `
    SELECT concurso, metodo, dezenas, dezenas_texto, soma, pares, impares,
           origem, cerebro_version, checkpoint_hash,
           audit_brain_version, source_of_truth, checkpoint_generated_at, criado_em
    FROM jogos_sistema
    WHERE concurso = ? AND origem = 'cerebro_python'
    ORDER BY metodo
  `, [proximo]);

  let jogos_gerados = jogosRows.map(mapJogoSistema);
  let source_jogos = 'd1_cerebro';

  if (!jogos_gerados.length && gateFull && !gateFull.blocked && gateFull.games?.length) {
    jogos_gerados = mapGamesFromCheckpoint(gateFull.games, proximo);
    source_jogos = 'checkpoint_fallback';
    try {
      await applyCerebroOrBlock(env, proximo);
      await purgeNonCerebroSistema(env, proximo);
      const after = await safeAll(env, `
        SELECT concurso, metodo, dezenas, dezenas_texto, soma, pares, impares,
               origem, cerebro_version, checkpoint_hash,
               audit_brain_version, source_of_truth, checkpoint_generated_at, criado_em
        FROM jogos_sistema
        WHERE concurso = ? AND origem = 'cerebro_python'
        ORDER BY metodo
      `, [proximo]);
      if (after.length) {
        jogos_gerados = after.map(mapJogoSistema);
        source_jogos = 'd1_cerebro';
      }
    } catch (e) {
      console.error('auto-apply cerebro', e);
    }
  }

  const pyOnly = jogos_gerados.filter((j) => j.origem === 'cerebro_python' || j.source === 'checkpoint_fallback');
  if (pyOnly.length) jogos_gerados = pyOnly;

  const provenance = jogos_gerados.length ? {
    origem: jogos_gerados[0].origem,
    cerebro_version: jogos_gerados[0].cerebro_version,
    checkpoint_hash: jogos_gerados[0].checkpoint_hash,
    source_of_truth: jogos_gerados[0].source_of_truth,
    jogos: jogos_gerados.length,
    rastreavel: Boolean(jogos_gerados[0].checkpoint_hash),
    source_jogos
  } : null;

  const ultimo_ingest = await safeFirst(env, `
    SELECT id, concurso, origem, cerebro_version, checkpoint_hash, jogos_count, ingestido_em
    FROM checkpoint_ingest ORDER BY id DESC LIMIT 1
  `);

  const ciclo = await safeFirst(env, `
    SELECT id, iniciado_em, finalizado_em, status, novos_concursos, conferencias,
           jogos_gerados, erro FROM execucoes_ciclo
    ORDER BY datetime(iniciado_em) DESC LIMIT 1
  `);
  let ultimo_ciclo = null;
  if (ciclo) {
    let novos = [];
    try { novos = JSON.parse(ciclo.novos_concursos || '[]'); } catch { novos = []; }
    ultimo_ciclo = { ...ciclo, novos_concursos: novos };
  }

  const recentFreq = await safeAll(env, `SELECT dezenas FROM resultados ORDER BY concurso DESC LIMIT 120`);
  const freq = new Map(Array.from({ length: 25 }, (_, i) => [i + 1, 0]));
  recentFreq.forEach((row) => {
    let dezenas = [];
    try { dezenas = JSON.parse(row.dezenas || '[]'); } catch { dezenas = []; }
    for (const d of dezenas) freq.set(d, (freq.get(d) || 0) + 1);
  });
  const n = recentFreq.length || 1;
  const frequencia_dezenas = Array.from({ length: 25 }, (_, i) => {
    const dezena = i + 1;
    return {
      dezena, dezena_texto: String(dezena).padStart(2, '0'),
      frequencia: freq.get(dezena) || 0,
      frequencia_pct: Number((((freq.get(dezena) || 0) * 100) / n).toFixed(2))
    };
  });

  const labConferido = parseLabRow(await safeFirst(env, `
    SELECT * FROM laboratorio_execucoes WHERE status = 'conferido'
    ORDER BY concurso DESC, id DESC LIMIT 1
  `));

  return json({
    ok: true,
    mode: 'seguro',
    total_concursos: totalRow?.total || 0,
    ultimo_resultado: ultimo,
    proximo_concurso: proximo,
    frequencia_dezenas,
    ultimo_ciclo,
    laboratorio_ultimo_conferido: labConferido,
    jogos_gerados,
    provenance,
    ultimo_ingest,
    cerebro_gate,
    source_jogos,
    note: cerebro_gate?.blocked
      ? 'Cérebro BLOQUEADO: ' + (cerebro_gate.message || cerebro_gate.status)
      : (source_jogos === 'checkpoint_fallback'
        ? 'Lista montada do checkpoint (D1 ainda sem ingest).'
        : 'Checkpoint Python ativo.')
  });
}

async function exportHistoricalResults(env) {
  const rows = await safeAll(env, `SELECT concurso, data_sorteio, dezenas FROM resultados ORDER BY concurso ASC`);
  const resultados = rows.map((row) => {
    let dezenas = [];
    try { dezenas = JSON.parse(row.dezenas || '[]'); } catch { dezenas = []; }
    return { concurso: Number(row.concurso), data: String(row.data_sorteio || ''), dezenas };
  }).filter((row) => row.concurso > 0 && Array.isArray(row.dezenas) && row.dezenas.length === 15);
  return json({ ok: true, purpose: 'historical_education_only', source: 'd1_resultados', total: resultados.length, resultados });
}

async function fetchAssetJson(request, env, assetPath) {
  const assetUrl = new URL(assetPath, request.url);
  const response = await env.ASSETS.fetch(new Request(assetUrl, { headers: request.headers }));
  if (!response.ok) return { ok: false, status: response.status };
  try { return { ok: true, payload: await response.json() }; }
  catch { return { ok: false, status: 500, invalid: true }; }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    try {
      if (request.method === 'OPTIONS') {
        return new Response(null, {
          status: 204,
          headers: {
            'access-control-allow-origin': '*',
            'access-control-allow-methods': 'GET,POST,PATCH,DELETE,OPTIONS',
            'access-control-allow-headers': 'content-type,authorization'
          }
        });
      }

      if (request.method === 'GET' && APRENDIZADO_ROUTES.has(url.pathname)) {
        try {
          return await env.ASSETS.fetch(assetRequest(request, url, '/aprendizado.html'));
        } catch (err) {
          return json({ ok: false, message: String(err.message || err) }, 500);
        }
      }

      if (request.method === 'GET' && COCKPIT_ROUTES.has(url.pathname)) {
        try {
          return await serveCockpit(request, env, url);
        } catch (err) {
          return json({ ok: false, message: String(err.message || err) }, 500);
        }
      }

      if (request.method === 'GET' && (url.pathname === '/api/sistema/status' || url.pathname === '/api/sistema/rapido')) {
        try { return await sistemaStatusSeguro(env); }
        catch (error) {
          return json({ ok: true, mode: 'degraded', message: String(error.message || error) });
        }
      }

      if (request.method === 'GET' && url.pathname === '/api/sistema/desempenho') {
        const lim = Number(url.searchParams.get('limit') || 30);
        try { return await desempenhoSistema(env, lim); }
        catch (error) {
          return json({ ok: false, message: String(error.message || error) }, 500);
        }
      }

      if (request.method === 'GET' && url.pathname === '/api/sistema/sugestao') {
        try { return await sugestaoDoDiaApi(env); }
        catch (error) {
          return json({ ok: false, message: String(error.message || error) }, 500);
        }
      }

      if (request.method === 'GET' && url.pathname === '/api/sistema/gate') {
        const latest = await safeFirst(env, 'SELECT concurso FROM resultados ORDER BY concurso DESC LIMIT 1');
        const proximo = latest ? Number(latest.concurso) + 1 : 1;
        const gate = await inspectCerebroCheckpoint(env, proximo);
        const { games, ...pub } = gate;
        return json({ ok: true, concurso: proximo, ...pub, jogos: games?.length || 0 });
      }

      if (request.method === 'GET' && url.pathname === '/api/health') {
        return json({
          ok: true, service: 'lotofacil', bridge: true, provenance: true,
          gate: true, cerebro_only: true, desempenho: true, sugestao_dia: true
        });
      }

      if (request.method === 'GET' && url.pathname === '/api/jogos') {
        await ensureAppSchema(env);
        const user = await getUserFromRequest(request, env);
        if (!user) return json({ ok: false, message: 'Acesso nao autorizado.' }, 401);
        return listJogosSeguro(user, env);
      }

      if (request.method === 'DELETE' && url.pathname === '/api/jogos') {
        await ensureAppSchema(env);
        const user = await getUserFromRequest(request, env);
        if (!user) return json({ ok: false, message: 'Acesso nao autorizado.' }, 401);
        return deleteAllJogosUsuario(user, env);
      }

      if (url.pathname.startsWith('/api/jogos') || url.pathname === '/api/ciclo/rodar') {
        try { await ensureAppSchema(env); } catch (e) { console.error(e); }
      }

      if (request.method === 'GET' && url.pathname === '/api/aprendizado/exportar-resultados') {
        return exportHistoricalResults(env);
      }
      if (request.method === 'GET' && url.pathname === '/api/aprendizado/checkpoint-operacional') {
        const result = await fetchAssetJson(request, env, '/motor_python_v4/checkpoints/operacional.json');
        if (!result.ok) {
          return json({
            ok: false, blocked: true, status: 'aguardando_checkpoint_operacional',
            message: 'Checkpoint ausente. Rode validar_historico + exportar_checkpoint_cerebro.'
          }, 503);
        }
        return json(result.payload);
      }

      return await historicalWorker.fetch(request, env, ctx);
    } catch (err) {
      return json({ ok: false, message: 'Erro interno: ' + String(err.message || err) }, 500);
    }
  },

  async scheduled(event, env, ctx) {
    return historicalWorker.scheduled(event, env, ctx);
  }
};
