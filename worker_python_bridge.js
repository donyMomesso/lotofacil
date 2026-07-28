import historicalWorker from './worker_learning.js';

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
  '/painel',
  '/painel.html',
  '/cockpit',
  '/painel_cockpit',
  '/painel_cockpit.html',
  '/painel_avancado',
  '/painel_avancado.html',
  '/painel_mobile',
  '/painel_mobile.html'
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

function parseLabRow(row) {
  if (!row) return null;
  const parse = (v, fb) => {
    try { return v ? JSON.parse(v) : fb; } catch { return fb; }
  };
  return {
    id: row.id,
    concurso: row.concurso,
    quantidade: row.quantidade,
    seed: row.seed,
    status: row.status,
    criado_em: row.criado_em,
    conferido_em: row.conferido_em,
    resumo: parse(row.resumo_json, null),
    estrategias: parse(row.estrategias_json, []),
    melhor: parse(row.melhor_json, null)
  };
}

/**
 * Status completo mas SEGURO: só leitura no D1.
 * NÃO chama generateNextContestGames nem sincronizarLaboratorios
 * (isso causava "Erro interno do servidor" por CPU/timeout no Worker).
 */
async function sistemaStatusSeguro(env) {
  if (!env?.DB) {
    return json({ ok: false, message: 'Binding D1 (DB) ausente no deploy.' }, 500);
  }

  const totalRow = await safeFirst(env, 'SELECT COUNT(*) AS total FROM resultados');
  const latest = await safeFirst(env, `
    SELECT concurso, data_sorteio, dezenas, dezenas_texto
    FROM resultados ORDER BY concurso DESC LIMIT 1
  `);

  let ultimo = null;
  let proximo = 1;
  if (latest) {
    let dezenas = [];
    try { dezenas = JSON.parse(latest.dezenas || '[]'); } catch { dezenas = []; }
    ultimo = {
      concurso: latest.concurso,
      data: latest.data_sorteio,
      dezenas,
      dezenas_texto: latest.dezenas_texto || dezenasTexto(dezenas)
    };
    proximo = Number(latest.concurso) + 1;
  }

  const recentesRows = await safeAll(env, `
    SELECT concurso, data_sorteio, dezenas, dezenas_texto
    FROM resultados ORDER BY concurso DESC LIMIT 50
  `);
  const resultados_recentes = recentesRows.map((row) => {
    let dezenas = [];
    try { dezenas = JSON.parse(row.dezenas || '[]'); } catch { dezenas = []; }
    return {
      concurso: row.concurso,
      data: row.data_sorteio,
      dezenas,
      dezenas_texto: row.dezenas_texto || dezenasTexto(dezenas)
    };
  });

  const jogosRows = await safeAll(env, `
    SELECT concurso, metodo, dezenas, dezenas_texto, soma, pares, impares
    FROM jogos_sistema WHERE concurso = ? ORDER BY metodo
  `, [proximo]);
  const jogos_gerados = jogosRows.map((row) => {
    let dezenas = [];
    try { dezenas = JSON.parse(row.dezenas || '[]'); } catch { dezenas = []; }
    return {
      concurso: row.concurso,
      metodo: row.metodo,
      dezenas,
      dezenas_texto: row.dezenas_texto,
      soma: row.soma,
      pares: row.pares,
      impares: row.impares
    };
  });

  const ciclo = await safeFirst(env, `
    SELECT id, iniciado_em, finalizado_em, status, novos_concursos, conferencias,
           jogos_descartados, sessoes_expiradas, proximo_concurso, jogos_gerados, erro
    FROM execucoes_ciclo ORDER BY datetime(iniciado_em) DESC LIMIT 1
  `);
  let ultimo_ciclo = null;
  if (ciclo) {
    let novos = [];
    try { novos = JSON.parse(ciclo.novos_concursos || '[]'); } catch { novos = []; }
    ultimo_ciclo = { ...ciclo, novos_concursos: novos };
  }

  // Frequência nos últimos 120 (barato)
  const recentFreq = await safeAll(env, `
    SELECT dezenas FROM resultados ORDER BY concurso DESC LIMIT 120
  `);
  const freq = new Map(Array.from({ length: 25 }, (_, i) => [i + 1, 0]));
  const atraso = new Map(Array.from({ length: 25 }, (_, i) => [i + 1, recentFreq.length]));
  const seen = new Set();
  recentFreq.forEach((row, idx) => {
    let dezenas = [];
    try { dezenas = JSON.parse(row.dezenas || '[]'); } catch { dezenas = []; }
    for (const d of dezenas) {
      freq.set(d, (freq.get(d) || 0) + 1);
      if (!seen.has(d)) {
        atraso.set(d, idx);
        seen.add(d);
      }
    }
  });
  const n = recentFreq.length || 1;
  const frequencia_dezenas = Array.from({ length: 25 }, (_, i) => {
    const dezena = i + 1;
    return {
      dezena,
      dezena_texto: String(dezena).padStart(2, '0'),
      frequencia: freq.get(dezena) || 0,
      frequencia_pct: Number((((freq.get(dezena) || 0) * 100) / n).toFixed(2)),
      atraso: atraso.get(dezena) || 0
    };
  });

  // Lab: só lê o que já existe (não prepara / não confere 20k aqui)
  const labProximo = parseLabRow(await safeFirst(env, `
    SELECT * FROM laboratorio_execucoes WHERE concurso = ? LIMIT 1
  `, [proximo]));
  const labConferido = parseLabRow(await safeFirst(env, `
    SELECT * FROM laboratorio_execucoes
    WHERE status = 'conferido'
    ORDER BY concurso DESC, id DESC LIMIT 1
  `));
  const labsRecentes = (await safeAll(env, `
    SELECT * FROM laboratorio_execucoes
    WHERE status = 'conferido'
    ORDER BY concurso DESC LIMIT 12
  `)).map(parseLabRow).filter(Boolean);

  // Agregado simples
  let laboratorio_acumulado = null;
  if (labsRecentes.length) {
    const resumo = {
      quantidade: 0,
      acertos_11: 0, acertos_12: 0, acertos_13: 0, acertos_14: 0, acertos_15: 0,
      acertos_11_mais: 0, melhor_acerto: 0, media_acertos: 0
    };
    const estratMap = new Map();
    for (const lab of labsRecentes) {
      const r = lab.resumo || {};
      const qtd = Number(r.quantidade || lab.quantidade || 0);
      resumo.quantidade += qtd;
      resumo.acertos_11 += Number(r.acertos_11 || 0);
      resumo.acertos_12 += Number(r.acertos_12 || 0);
      resumo.acertos_13 += Number(r.acertos_13 || 0);
      resumo.acertos_14 += Number(r.acertos_14 || 0);
      resumo.acertos_15 += Number(r.acertos_15 || 0);
      resumo.acertos_11_mais += Number(r.acertos_11_mais || 0);
      resumo.media_acertos += Number(r.media_acertos || 0) * qtd;
      resumo.melhor_acerto = Math.max(resumo.melhor_acerto, Number(r.melhor_acerto || 0));
      for (const item of lab.estrategias || []) {
        const cur = estratMap.get(item.key) || {
          key: item.key, label: item.label, jogos: 0, soma_acertos: 0,
          acertos_11: 0, acertos_12: 0, acertos_13: 0, acertos_14: 0, acertos_15: 0,
          melhor_acerto: 0
        };
        cur.jogos += Number(item.jogos || 0);
        cur.soma_acertos += Number(item.soma_acertos || 0);
        cur.acertos_11 += Number(item.acertos_11 || 0);
        cur.acertos_12 += Number(item.acertos_12 || 0);
        cur.acertos_13 += Number(item.acertos_13 || 0);
        cur.acertos_14 += Number(item.acertos_14 || 0);
        cur.acertos_15 += Number(item.acertos_15 || 0);
        cur.melhor_acerto = Math.max(cur.melhor_acerto, Number(item.melhor_acerto || 0));
        estratMap.set(item.key, cur);
      }
    }
    if (resumo.quantidade) {
      resumo.media_acertos = Number((resumo.media_acertos / resumo.quantidade).toFixed(4));
    }
    const estrategias = Array.from(estratMap.values()).map((item) => ({
      ...item,
      media_acertos: item.jogos ? Number((item.soma_acertos / item.jogos).toFixed(4)) : 0,
      taxa_11_mais: item.jogos
        ? Number((((item.acertos_11 + item.acertos_12 + item.acertos_13 + item.acertos_14 + item.acertos_15) * 100) / item.jogos).toFixed(2))
        : 0
    })).sort((a, b) => b.taxa_11_mais - a.taxa_11_mais);
    laboratorio_acumulado = { resumo, estrategias, concursos: labsRecentes.map((l) => l.concurso) };
  }

  return json({
    ok: true,
    mode: 'seguro',
    total_concursos: totalRow?.total || 0,
    ultimo_resultado: ultimo,
    proximo_concurso: proximo,
    resultados_recentes,
    frequencia_dezenas,
    inicio_dezena: [],
    ultimo_ciclo,
    laboratorio: labProximo,
    laboratorio_ultimo_conferido: labConferido,
    laboratorio_acumulado,
    laboratorio_historico: labsRecentes,
    laboratorio_semana_atual: null,
    laboratorio_semana_historico: [],
    jogos_gerados,
    jogos_conferidor: [],
    note: 'Status seguro: só leitura. Geração de jogos e lab 20k ficam no ciclo (/api/ciclo/rodar), não no GET.'
  });
}

async function sistemaRapido(env) {
  const data = await sistemaStatusSeguro(env);
  // Reusa o mesmo payload; client espera mode
  return data;
}

async function exportHistoricalResults(env) {
  const rows = await safeAll(env, `
    SELECT concurso, data_sorteio, dezenas FROM resultados ORDER BY concurso ASC
  `);
  const resultados = rows.map((row) => {
    let dezenas = [];
    try { dezenas = JSON.parse(row.dezenas || '[]'); } catch { dezenas = []; }
    return { concurso: Number(row.concurso), data: String(row.data_sorteio || ''), dezenas };
  }).filter((row) => row.concurso > 0 && Array.isArray(row.dezenas) && row.dezenas.length === 15);
  return json({
    ok: true,
    purpose: 'historical_education_only',
    source: 'd1_resultados',
    total: resultados.length,
    resultados
  });
}

async function fetchAssetJson(request, env, assetPath) {
  const assetUrl = new URL(assetPath, request.url);
  const response = await env.ASSETS.fetch(new Request(assetUrl, { headers: request.headers }));
  if (!response.ok) return { ok: false, status: response.status };
  try {
    return { ok: true, payload: await response.json() };
  } catch {
    return { ok: false, status: 500, invalid: true };
  }
}

async function pythonCheckpoint(request, env) {
  const result = await fetchAssetJson(request, env, '/motor_python_v4/checkpoints/latest.json');
  if (!result.ok) {
    return json({
      ok: false,
      purpose: 'historical_education_only',
      status: 'aguardando_primeiro_checkpoint_python',
      message: 'O primeiro bloco histórico de 5 concursos ainda não foi publicado.'
    }, 503);
  }
  if (result.invalid) return json({ ok: false, message: 'Checkpoint Python inválido.' }, 500);
  return json(result.payload, 200);
}

async function pythonCheckpointOperacional(request, env) {
  const result = await fetchAssetJson(request, env, '/motor_python_v4/checkpoints/operacional.json');
  if (!result.ok) {
    return json({
      ok: false,
      purpose: 'historical_education_only',
      source_of_truth: 'python',
      status: 'aguardando_checkpoint_operacional',
      message: 'Rode scripts/exportar_checkpoint_cerebro.py no ciclo diário.'
    }, 503);
  }
  if (result.invalid) return json({ ok: false, message: 'Checkpoint operacional inválido.' }, 500);
  return json(result.payload, 200);
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
          console.error('cockpit asset', err);
          return json({ ok: false, message: 'Falha ao servir o cockpit: ' + (err.message || err) }, 500);
        }
      }

      // Intercepta status: versão segura (evita 500 do worker.js antigo)
      if (request.method === 'GET' && (url.pathname === '/api/sistema/status' || url.pathname === '/api/sistema/rapido')) {
        try {
          return await sistemaStatusSeguro(env);
        } catch (error) {
          console.error('sistemaStatusSeguro', error);
          return json({
            ok: true,
            mode: 'degraded',
            total_concursos: 0,
            ultimo_resultado: null,
            proximo_concurso: 1,
            jogos_gerados: [],
            frequencia_dezenas: [],
            message: String(error.message || error)
          });
        }
      }

      if (request.method === 'GET' && url.pathname === '/api/health') {
        return json({ ok: true, service: 'lotofacil', bridge: true });
      }

      if (request.method === 'GET' && url.pathname === '/api/aprendizado/exportar-resultados') {
        try { return await exportHistoricalResults(env); }
        catch (error) {
          return json({ ok: false, message: 'Falha ao exportar: ' + (error.message || error) }, 500);
        }
      }
      if (request.method === 'GET' && url.pathname === '/api/aprendizado/checkpoint-python') {
        return pythonCheckpoint(request, env);
      }
      if (request.method === 'GET' && url.pathname === '/api/aprendizado/checkpoint-operacional') {
        return pythonCheckpointOperacional(request, env);
      }

      try {
        return await historicalWorker.fetch(request, env, ctx);
      } catch (err) {
        console.error('historicalWorker', err);
        return json({
          ok: false,
          message: 'Erro no Worker: ' + String(err.message || err)
        }, 500);
      }
    } catch (err) {
      console.error('bridge top', err);
      return json({
        ok: false,
        message: 'Erro interno do servidor: ' + String(err.message || err)
      }, 500);
    }
  },

  async scheduled(event, env, ctx) {
    return historicalWorker.scheduled(event, env, ctx);
  }
};
