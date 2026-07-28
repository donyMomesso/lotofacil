import historicalWorker from './worker_learning.js';
import { ensureJogosSistemaProvenance, inspectCerebroCheckpoint } from './worker_cerebro_games.js';

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

function assetRequest(request, url, pathname) {
  const assetUrl = new URL(request.url);
  assetUrl.pathname = pathname;
  assetUrl.search = url.search;
  return new Request(assetUrl.toString(), { method: 'GET', headers: request.headers });
}

function dezenasTexto(dezenas) {
  return (dezenas || []).map((d) => String(d).padStart(2, '0')).join('-');
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

  // Gate do Cérebro — sem fallback silencioso
  let cerebro_gate;
  try {
    cerebro_gate = await inspectCerebroCheckpoint(env, proximo);
    // não serializar games inteiros no status
    if (cerebro_gate.games) {
      const { games, ...rest } = cerebro_gate;
      cerebro_gate = { ...rest, jogos: games.length };
    }
  } catch (e) {
    cerebro_gate = { status: 'invalid', blocked: true, message: String(e.message || e) };
  }

  let jogosRows = await safeAll(env, `
    SELECT concurso, metodo, dezenas, dezenas_texto, soma, pares, impares,
           origem, cerebro_version, checkpoint_hash,
           audit_brain_version, source_of_truth, checkpoint_generated_at, criado_em
    FROM jogos_sistema WHERE concurso = ? ORDER BY metodo
  `, [proximo]);
  if (!jogosRows.length) {
    jogosRows = await safeAll(env, `
      SELECT concurso, metodo, dezenas, dezenas_texto, soma, pares, impares, criado_em
      FROM jogos_sistema WHERE concurso = ? ORDER BY metodo
    `, [proximo]);
  }
  const jogos_gerados = jogosRows.map(mapJogoSistema);

  const provenance = jogos_gerados.length ? {
    origem: jogos_gerados[0].origem,
    cerebro_version: jogos_gerados[0].cerebro_version,
    checkpoint_hash: jogos_gerados[0].checkpoint_hash,
    source_of_truth: jogos_gerados[0].source_of_truth,
    jogos: jogos_gerados.length,
    rastreavel: Boolean(jogos_gerados[0].checkpoint_hash)
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
    note: cerebro_gate?.blocked
      ? 'Cérebro BLOQUEADO: ' + (cerebro_gate.message || cerebro_gate.status)
      : 'Checkpoint Python ativo.'
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

      if (request.method === 'GET' && COCKPIT_ROUTES.has(url.pathname)) {
        try {
          return await env.ASSETS.fetch(assetRequest(request, url, '/painel_cockpit.html'));
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

      if (request.method === 'GET' && url.pathname === '/api/sistema/gate') {
        const latest = await safeFirst(env, 'SELECT concurso FROM resultados ORDER BY concurso DESC LIMIT 1');
        const proximo = latest ? Number(latest.concurso) + 1 : 1;
        const gate = await inspectCerebroCheckpoint(env, proximo);
        const { games, ...pub } = gate;
        return json({ ok: true, concurso: proximo, ...pub, jogos: games?.length || 0 });
      }

      if (request.method === 'GET' && url.pathname === '/api/health') {
        return json({ ok: true, service: 'lotofacil', bridge: true, provenance: true, gate: true });
      }

      if (request.method === 'GET' && url.pathname === '/api/jogos') {
        await ensureAppSchema(env);
        const user = await getUserFromRequest(request, env);
        if (!user) return json({ ok: false, message: 'Acesso nao autorizado.' }, 401);
        return listJogosSeguro(user, env);
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
