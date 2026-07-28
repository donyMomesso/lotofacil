import historicalWorker from './worker_learning.js';

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' }
  });
}

/** Rotas unificadas → cockpit (painéis legados ainda existem como assets). */
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
