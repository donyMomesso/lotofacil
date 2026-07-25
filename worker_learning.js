import baseWorker from './worker.js';
import * as Learning from './learning_audit_core.mjs';

const HISTORY_LIMIT = 140;
const DEFAULT_TESTS = 24;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store'
    }
  });
}

function parseJson(value, fallback = null) {
  try {
    return value ? JSON.parse(value) : fallback;
  } catch {
    return fallback;
  }
}

function bytesToHex(bytes) {
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
}

async function sha256Hex(value) {
  const bytes = new TextEncoder().encode(value);
  return bytesToHex(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)));
}

async function ensureHistoricalLearningTable(env) {
  await env.DB.prepare(`
    CREATE TABLE IF NOT EXISTS aprendizado_historico (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      concurso INTEGER NOT NULL,
      data_sorteio TEXT,
      modelo_chave TEXT NOT NULL,
      modelo_nome TEXT NOT NULL,
      versao_modelo TEXT NOT NULL,
      treino_ate INTEGER NOT NULL,
      quantidade_treino INTEGER NOT NULL,
      probabilidade_soma REAL NOT NULL,
      ranking_json TEXT NOT NULL,
      resultado_json TEXT NOT NULL,
      brier REAL NOT NULL,
      log_loss REAL NOT NULL,
      top15 INTEGER NOT NULL,
      top18 INTEGER NOT NULL,
      top19 INTEGER NOT NULL,
      top20 INTEGER NOT NULL,
      top21 INTEGER NOT NULL,
      hash_registro TEXT NOT NULL,
      criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(concurso, modelo_chave, versao_modelo)
    )
  `).run();
  await env.DB.prepare(`
    CREATE INDEX IF NOT EXISTS idx_aprendizado_historico_concurso
    ON aprendizado_historico (concurso DESC)
  `).run();
}

async function historicalDraws(env) {
  const rows = await env.DB.prepare(`
    SELECT concurso, data_sorteio, dezenas
    FROM resultados
    ORDER BY concurso DESC
    LIMIT ?
  `).bind(HISTORY_LIMIT).all();
  return rows.results
    .map((row) => ({
      concurso: Number(row.concurso),
      data: String(row.data_sorteio || ''),
      dezenas: parseJson(row.dezenas, [])
    }))
    .reverse();
}

function compactRanking(score) {
  return score.ranking.map((row) => ({
    rank: row.rank,
    number: row.number,
    probability: Learning.round(row.probability, 8)
  }));
}

async function insertHistoricalEvaluation(env, training, target, modelKey) {
  const score = Learning.scoreTrainingHistory(training, modelKey);
  if (score.trainingThrough >= target.concurso) {
    throw new Error(`Vazamento temporal detectado no concurso ${target.concurso}.`);
  }
  const evaluation = Learning.evaluateHistoricalScore(score, target.dezenas);
  const record = {
    schema: 1,
    purpose: 'historical_evaluation_only',
    contest: target.concurso,
    drawDate: target.data,
    modelKey: score.model,
    modelName: score.modelName,
    modelVersion: score.modelVersion,
    trainingThrough: score.trainingThrough,
    trainingCount: score.drawsUsed,
    probabilitySum: score.probabilitySum,
    ranking: compactRanking(score),
    result: target.dezenas,
    evaluation
  };
  const serialized = Learning.stableStringify(record);
  const hash = await sha256Hex(serialized);
  const inserted = await env.DB.prepare(`
    INSERT OR IGNORE INTO aprendizado_historico (
      concurso, data_sorteio, modelo_chave, modelo_nome, versao_modelo,
      treino_ate, quantidade_treino, probabilidade_soma, ranking_json,
      resultado_json, brier, log_loss, top15, top18, top19, top20, top21,
      hash_registro
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    target.concurso,
    target.data,
    score.model,
    score.modelName,
    score.modelVersion,
    score.trainingThrough,
    score.drawsUsed,
    score.probabilitySum,
    JSON.stringify(record.ranking),
    JSON.stringify(target.dezenas),
    evaluation.brier,
    evaluation.logLoss,
    evaluation.top15,
    evaluation.top18,
    evaluation.top19,
    evaluation.top20,
    evaluation.top21,
    hash
  ).run();
  return Boolean(inserted.meta.changes);
}

async function syncHistoricalLearning(env, maxTests = DEFAULT_TESTS) {
  await ensureHistoricalLearningTable(env);
  const draws = Learning.normalizeDraws(await historicalDraws(env));
  if (draws.length < 13) {
    return { inserted: 0, evaluatedContests: 0, reason: 'historico_insuficiente' };
  }
  const start = Math.max(12, draws.length - Math.max(1, Number(maxTests || DEFAULT_TESTS)));
  let inserted = 0;
  let evaluatedContests = 0;
  for (let targetIndex = start; targetIndex < draws.length; targetIndex += 1) {
    const target = draws[targetIndex];
    const training = draws.slice(0, targetIndex);
    let touched = false;
    for (const modelKey of Object.keys(Learning.MODELS)) {
      const created = await insertHistoricalEvaluation(env, training, target, modelKey);
      if (created) inserted += 1;
      touched = touched || created;
    }
    if (touched) evaluatedContests += 1;
  }
  return { inserted, evaluatedContests, modelVersion: Learning.MODEL_VERSION };
}

function modelAggregate(rows, key) {
  const selected = rows.filter((row) => row.modelo_chave === key);
  const average = (field) => selected.length
    ? selected.reduce((sum, row) => sum + Number(row[field] || 0), 0) / selected.length
    : 0;
  const recent = selected.slice(0, 8);
  const recentAverage = (field) => recent.length
    ? recent.reduce((sum, row) => sum + Number(row[field] || 0), 0) / recent.length
    : 0;
  const brier = Learning.round(average('brier'));
  const avgTop21 = Learning.round(average('top21'), 4);
  const recentBrier = Learning.round(recentAverage('brier'));
  const recentTop21 = Learning.round(recentAverage('top21'), 4);
  return {
    key,
    name: Learning.MODELS[key]?.name || key,
    samples: selected.length,
    brier,
    logLoss: Learning.round(average('log_loss')),
    avgTop15: Learning.round(average('top15'), 4),
    avgTop18: Learning.round(average('top18'), 4),
    avgTop19: Learning.round(average('top19'), 4),
    avgTop20: Learning.round(average('top20'), 4),
    avgTop21,
    deltaBrier: Learning.round(Learning.BASELINE_BRIER - brier),
    deltaTop21: Learning.round(avgTop21 - Learning.THEORETICAL_TOP21, 4),
    recentBrier,
    recentTop21,
    overfitAlert: selected.length >= 12 && (
      recentBrier > brier + 0.012 || recentTop21 < avgTop21 - 0.35
    )
  };
}

async function historicalLearningSummary(env, limit = 1000) {
  await ensureHistoricalLearningTable(env);
  const totals = await env.DB.prepare(`
    SELECT COUNT(*) AS total_records, COUNT(DISTINCT concurso) AS total_contests
    FROM aprendizado_historico
  `).first();
  const rows = await env.DB.prepare(`
    SELECT concurso, data_sorteio, modelo_chave, modelo_nome, versao_modelo,
           treino_ate, quantidade_treino, probabilidade_soma, brier, log_loss,
           top15, top18, top19, top20, top21, hash_registro, criado_em
    FROM aprendizado_historico
    ORDER BY concurso DESC, modelo_chave ASC
    LIMIT ?
  `).bind(Math.min(Math.max(Number(limit || 1000), 20), 2000)).all();
  const models = Object.keys(Learning.MODELS).map((key) => modelAggregate(rows.results, key));
  const ranked = models.slice().sort((a, b) => {
    const aScore = (Learning.BASELINE_BRIER - a.brier) * 100 + (a.avgTop21 - Learning.THEORETICAL_TOP21);
    const bScore = (Learning.BASELINE_BRIER - b.brier) * 100 + (b.avgTop21 - Learning.THEORETICAL_TOP21);
    return bScore - aScore;
  });
  const recent = rows.results.slice(0, 60).map((row) => ({
    concurso: row.concurso,
    data: row.data_sorteio,
    model: row.modelo_chave,
    modelName: row.modelo_nome,
    modelVersion: row.versao_modelo,
    trainingThrough: row.treino_ate,
    trainingCount: row.quantidade_treino,
    probabilitySum: row.probabilidade_soma,
    brier: row.brier,
    logLoss: row.log_loss,
    top15: row.top15,
    top18: row.top18,
    top19: row.top19,
    top20: row.top20,
    top21: row.top21,
    hash: row.hash_registro,
    createdAt: row.criado_em
  }));
  return {
    ok: true,
    purpose: 'historical_evaluation_only',
    modelVersion: Learning.MODEL_VERSION,
    baselines: {
      brier: Learning.BASELINE_BRIER,
      top21: Learning.THEORETICAL_TOP21
    },
    totalRecords: Number(totals?.total_records || 0),
    totalContests: Number(totals?.total_contests || 0),
    bestHistoricalModel: ranked[0] || null,
    models,
    overfitAlerts: models.filter((model) => model.overfitAlert).map((model) => model.key),
    recent
  };
}

async function historicalApi(env, url) {
  const sync = await syncHistoricalLearning(env, Number(url.searchParams.get('tests') || DEFAULT_TESTS));
  return json({ ...(await historicalLearningSummary(env)), sync });
}

async function runBaseScheduled(event, env) {
  const tasks = [];
  await baseWorker.scheduled(event, env, {
    waitUntil(promise) {
      tasks.push(Promise.resolve(promise));
    }
  });
  await Promise.all(tasks);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === '/api/aprendizado/historico' && request.method === 'GET') {
      try {
        return await historicalApi(env, url);
      } catch (error) {
        console.error(error);
        return json({ ok: false, message: 'Falha ao atualizar o arquivo histórico.' }, 500);
      }
    }

    const response = await baseWorker.fetch(request, env, ctx);
    if (url.pathname === '/api/ciclo/rodar' && request.method === 'POST' && response.ok && ctx?.waitUntil) {
      ctx.waitUntil(syncHistoricalLearning(env));
    }
    return response;
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil((async () => {
      await runBaseScheduled(event, env);
      await syncHistoricalLearning(env);
    })());
  }
};
