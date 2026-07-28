import historicalWorker from './worker_learning.js';

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' }
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

async function pythonCheckpoint(request, env) {
  const assetUrl = new URL('/motor_python_v4/checkpoints/latest.json', request.url);
  const response = await env.ASSETS.fetch(new Request(assetUrl, { headers: request.headers }));
  if (!response.ok) {
    return json({
      ok: false,
      purpose: 'historical_education_only',
      status: 'aguardando_primeiro_checkpoint_python',
      message: 'O primeiro bloco histórico de 5 concursos ainda não foi publicado.'
    }, 503);
  }
  try {
    const payload = await response.json();
    return json(payload, 200);
  } catch {
    return json({ ok: false, message: 'Checkpoint Python inválido.' }, 500);
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
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
    return historicalWorker.fetch(request, env, ctx);
  },
  async scheduled(event, env, ctx) {
    return historicalWorker.scheduled(event, env, ctx);
  }
};
