import historicalWorker from './worker_learning.js';

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' }
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

/**
 * Status leve para o Cockpit: só lê o D1.
 * Não chama generateNextContestGames, sincronizarLaboratorios nem varre frequência completa.
 * Isso evita o atraso de vários segundos do /api/sistema/status.
 */
async function sistemaRapido(env) {
  const totalRow = await env.DB.prepare('SELECT COUNT(*) AS total FROM resultados').first();
  const latest = await env.DB.prepare(`
    SELECT concurso, data_sorteio, dezenas, dezenas_texto
    FROM resultados
    ORDER BY concurso DESC
    LIMIT 1
  `).first();

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

  const jogosRows = await env.DB.prepare(`
    SELECT concurso, metodo, dezenas, dezenas_texto, soma, pares, impares
    FROM jogos_sistema
    WHERE concurso = ?
    ORDER BY metodo
  `).bind(proximo).all();

  const jogos_gerados = (jogosRows.results || []).map((row) => {
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

  const ciclo = await env.DB.prepare(`
    SELECT id, iniciado_em, finalizado_em, status, novos_concursos, conferencias,
           jogos_descartados, sessoes_expiradas, proximo_concurso, jogos_gerados, erro
    FROM execucoes_ciclo
    ORDER BY datetime(iniciado_em) DESC
    LIMIT 1
  `).first();

  let ultimo_ciclo = null;
  if (ciclo) {
    let novos = [];
    try { novos = JSON.parse(ciclo.novos_concursos || '[]'); } catch { novos = []; }
    ultimo_ciclo = { ...ciclo, novos_concursos: novos };
  }

  // Frequência só nos últimos 120 concursos (barato e suficiente para a aba)
  const recent = await env.DB.prepare(`
    SELECT dezenas FROM resultados ORDER BY concurso DESC LIMIT 120
  `).all();
  const freq = new Map(Array.from({ length: 25 }, (_, i) => [i + 1, 0]));
  const atraso = new Map(Array.from({ length: 25 }, (_, i) => [i + 1, recent.results.length]));
  const seen = new Set();
  (recent.results || []).forEach((row, idx) => {
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
  const n = (recent.results || []).length || 1;
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

  return json({
    ok: true,
    mode: 'rapido',
    total_concursos: totalRow?.total || 0,
    ultimo_resultado: ultimo,
    proximo_concurso: proximo,
    jogos_gerados,
    ultimo_ciclo,
    frequencia_dezenas,
    inicio_dezena: [],
    laboratorio: null,
    laboratorio_acumulado: null,
    laboratorio_semana_atual: null,
    laboratorio_semana_historico: [],
    hint: 'Use /api/sistema/status só quando precisar de lab completo (mais lento).'
  });
}

async function exportHistoricalResults(env) {
  const query = await env.DB.prepare(`
    SELECT concurso, data_sorteio, dezenas
    FROM resultados
    ORDER BY concurso ASC
  `).all();
  const resultados = (query.results || []).map((row) => {
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
      message: 'Rode scripts/exportar_checkpoint_cerebro.py no ciclo diário para publicar o checkpoint operacional.'
    }, 503);
  }
  if (result.invalid) return json({ ok: false, message: 'Checkpoint operacional inválido.' }, 500);
  return json(result.payload, 200);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === 'GET' && COCKPIT_ROUTES.has(url.pathname)) {
      return env.ASSETS.fetch(assetRequest(request, url, '/painel_cockpit.html'));
    }

    if (request.method === 'GET' && url.pathname === '/api/sistema/rapido') {
      try { return await sistemaRapido(env); }
      catch (error) {
        console.error(error);
        return json({ ok: false, message: 'Falha no status rápido.' }, 500);
      }
    }

    if (request.method === 'GET' && url.pathname === '/api/aprendizado/exportar-resultados') {
      try { return await exportHistoricalResults(env); }
      catch (error) {
        console.error(error);
        return json({ ok: false, message: 'Falha ao exportar resultados históricos.' }, 500);
      }
    }
    if (request.method === 'GET' && url.pathname === '/api/aprendizado/checkpoint-python') {
      return pythonCheckpoint(request, env);
    }
    if (request.method === 'GET' && url.pathname === '/api/aprendizado/checkpoint-operacional') {
      return pythonCheckpointOperacional(request, env);
    }
    return historicalWorker.fetch(request, env, ctx);
  },
  async scheduled(event, env, ctx) {
    return historicalWorker.scheduled(event, env, ctx);
  }
};
