import baseWorker from './worker.js';
import * as Learning from './learning_audit_core.mjs';

const HISTORY_LIMIT = 180;
const DEFAULT_TESTS = 48;
const MAX_TESTS = 96;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' }
  });
}
function parseJson(value, fallback = null) {
  try { return value ? JSON.parse(value) : fallback; } catch { return fallback; }
}
function bytesToHex(bytes) { return Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join(''); }
async function sha256Hex(value) {
  const bytes = new TextEncoder().encode(value);
  return bytesToHex(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)));
}

async function ensureHistoricalLearningTables(env) {
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
  await env.DB.prepare(`
    CREATE TABLE IF NOT EXISTS aprendizado_resumos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      modelo_chave TEXT NOT NULL,
      versao_modelo TEXT NOT NULL,
      amostras INTEGER NOT NULL,
      ultimo_concurso INTEGER NOT NULL,
      resumo_json TEXT NOT NULL,
      hash_resumo TEXT NOT NULL,
      atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(modelo_chave, versao_modelo, amostras, ultimo_concurso)
    )
  `).run();
  await env.DB.prepare(`
    CREATE INDEX IF NOT EXISTS idx_aprendizado_resumos_versao
    ON aprendizado_resumos (versao_modelo, atualizado_em DESC)
  `).run();
}

async function historicalDraws(env) {
  const rows = await env.DB.prepare(`
    SELECT concurso, data_sorteio, dezenas
    FROM resultados
    ORDER BY concurso DESC
    LIMIT ?
  `).bind(HISTORY_LIMIT).all();
  return rows.results.map((row) => ({
    concurso: Number(row.concurso), data: String(row.data_sorteio || ''), dezenas: parseJson(row.dezenas, [])
  })).reverse();
}
function compactRanking(score) {
  return score.ranking.map((row) => ({ rank: row.rank, number: row.number, probability: Learning.round(row.probability, 8) }));
}

async function insertHistoricalEvaluation(env, training, target, modelKey) {
  const score = Learning.scoreTrainingHistory(training, modelKey);
  if (score.trainingThrough >= target.concurso) throw new Error(`Vazamento temporal detectado no concurso ${target.concurso}.`);
  const evaluation = Learning.evaluateHistoricalScore(score, target.dezenas);
  const record = {
    schema: 2,
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
  const hash = await sha256Hex(Learning.stableStringify(record));
  const inserted = await env.DB.prepare(`
    INSERT OR IGNORE INTO aprendizado_historico (
      concurso, data_sorteio, modelo_chave, modelo_nome, versao_modelo,
      treino_ate, quantidade_treino, probabilidade_soma, ranking_json,
      resultado_json, brier, log_loss, top15, top18, top19, top20, top21,
      hash_registro
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    target.concurso, target.data, score.model, score.modelName, score.modelVersion,
    score.trainingThrough, score.drawsUsed, score.probabilitySum, JSON.stringify(record.ranking),
    JSON.stringify(target.dezenas), evaluation.brier, evaluation.logLoss,
    evaluation.top15, evaluation.top18, evaluation.top19, evaluation.top20, evaluation.top21, hash
  ).run();
  return Boolean(inserted.meta.changes);
}

async function syncHistoricalLearning(env, maxTests = DEFAULT_TESTS) {
  await ensureHistoricalLearningTables(env);
  const draws = Learning.normalizeDraws(await historicalDraws(env));
  if (draws.length < 13) return { inserted: 0, evaluatedContests: 0, reason: 'historico_insuficiente' };
  const safeTests = Math.min(Math.max(1, Number(maxTests || DEFAULT_TESTS)), MAX_TESTS);
  const start = Math.max(12, draws.length - safeTests);
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
  return { inserted, evaluatedContests, requestedTests: safeTests, modelVersion: Learning.MODEL_VERSION };
}

function rowCalibration(row) {
  const ranking = parseJson(row.ranking_json, []);
  const result = parseJson(row.resultado_json, []);
  try { return Learning.calibrationDiagnostics(ranking, result); }
  catch { return { ece: 0, sharpness: 0, bins: [] }; }
}

function modelAggregate(rows, key) {
  const selected = rows.filter((row) => row.modelo_chave === key)
    .sort((a, b) => Number(a.concurso) - Number(b.concurso));
  const values = (field) => selected.map((row) => Number(row[field] || 0));
  const calibrations = selected.map(rowCalibration);
  const decorated = selected.map((row, index) => ({
    concurso: Number(row.concurso), brier: Number(row.brier), logLoss: Number(row.log_loss), top21: Number(row.top21),
    calibrationError: Number(calibrations[index]?.ece || 0)
  }));
  const latestContest = selected[selected.length - 1]?.concurso || 0;
  const seedBase = `${Learning.MODEL_VERSION}-${key}-${selected.length}-${latestContest}`;
  const brierCI = Learning.bootstrapMeanCI(values('brier'), { seed: `${seedBase}-brier` });
  const top21CI = Learning.bootstrapMeanCI(values('top21'), { seed: `${seedBase}-top21` });
  const permutation = Learning.permutationTop21Test(values('top21'), { seed: `${seedBase}-perm` });
  const rolling = Learning.rollingWindows(decorated, [8, 16, 24]);
  const drift = Learning.detectDrift(decorated, 8);
  const brier = Learning.round(Learning.average(values('brier')));
  const avgTop21 = Learning.round(Learning.average(values('top21')), 4);
  const evidence = Learning.evidenceAssessment({
    samples: selected.length, brierCI, top21CI, permutationPValue: permutation.pValue
  });
  return {
    key,
    name: Learning.MODELS[key]?.name || key,
    version: Learning.MODEL_VERSION,
    samples: selected.length,
    firstContest: selected[0]?.concurso || null,
    latestContest,
    brier,
    brierCI,
    logLoss: Learning.round(Learning.average(values('log_loss'))),
    avgTop15: Learning.round(Learning.average(values('top15')), 4),
    avgTop18: Learning.round(Learning.average(values('top18')), 4),
    avgTop19: Learning.round(Learning.average(values('top19')), 4),
    avgTop20: Learning.round(Learning.average(values('top20')), 4),
    avgTop21,
    top21CI,
    deltaBrier: Learning.round(Learning.BASELINE_BRIER - brier),
    deltaTop21: Learning.round(avgTop21 - Learning.THEORETICAL_TOP21, 4),
    calibrationError: Learning.round(Learning.average(calibrations.map((item) => item.ece))),
    sharpness: Learning.round(Learning.average(calibrations.map((item) => item.sharpness))),
    permutation,
    rolling,
    drift,
    evidence,
    overfitAlert: ['moderate', 'high'].includes(drift.level)
  };
}

async function persistModelSummary(env, summary) {
  if (!summary.samples || !summary.latestContest) return;
  const record = { schema: 1, purpose: 'historical_robustness_summary', generatedAt: new Date().toISOString(), ...summary };
  const serialized = Learning.stableStringify(record);
  const hash = await sha256Hex(serialized);
  await env.DB.prepare(`
    INSERT INTO aprendizado_resumos (
      modelo_chave, versao_modelo, amostras, ultimo_concurso, resumo_json, hash_resumo, atualizado_em
    ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(modelo_chave, versao_modelo, amostras, ultimo_concurso) DO UPDATE SET
      resumo_json = excluded.resumo_json,
      hash_resumo = excluded.hash_resumo,
      atualizado_em = CURRENT_TIMESTAMP
  `).bind(summary.key, summary.version, summary.samples, summary.latestContest, serialized, hash).run();
}

async function versionRegistry(env) {
  const rows = await env.DB.prepare(`
    SELECT versao_modelo, COUNT(*) AS registros, COUNT(DISTINCT concurso) AS concursos,
           MIN(concurso) AS primeiro_concurso, MAX(concurso) AS ultimo_concurso,
           MIN(criado_em) AS criado_em
    FROM aprendizado_historico
    GROUP BY versao_modelo
    ORDER BY MAX(criado_em) DESC
  `).all();
  return rows.results.map((row) => ({
    version: row.versao_modelo,
    records: Number(row.registros || 0),
    contests: Number(row.concursos || 0),
    firstContest: Number(row.primeiro_concurso || 0),
    lastContest: Number(row.ultimo_concurso || 0),
    createdAt: row.criado_em,
    current: row.versao_modelo === Learning.MODEL_VERSION
  }));
}

async function integritySummary(env, rows) {
  const temporal = rows.filter((row) => Number(row.treino_ate) >= Number(row.concurso)).length;
  const probability = rows.filter((row) => Math.abs(Number(row.probabilidade_soma) - Learning.DRAW_SIZE) > 0.000001).length;
  let hashViolations = 0;
  for (const row of rows) {
    const ranking = parseJson(row.ranking_json, []);
    const result = parseJson(row.resultado_json, []);
    let calibration;
    try { calibration = Learning.calibrationDiagnostics(ranking, result); }
    catch { hashViolations += 1; continue; }
    const evaluation = {
      brier: Number(row.brier), logLoss: Number(row.log_loss), top15: Number(row.top15), top18: Number(row.top18),
      top19: Number(row.top19), top20: Number(row.top20), top21: Number(row.top21),
      calibrationError: calibration.ece, sharpness: calibration.sharpness
    };
    const record = {
      schema: 2, purpose: 'historical_evaluation_only', contest: Number(row.concurso), drawDate: row.data_sorteio,
      modelKey: row.modelo_chave, modelName: row.modelo_nome, modelVersion: row.versao_modelo,
      trainingThrough: Number(row.treino_ate), trainingCount: Number(row.quantidade_treino),
      probabilitySum: Number(row.probabilidade_soma), ranking, result, evaluation
    };
    const hash = await sha256Hex(Learning.stableStringify(record));
    if (hash !== row.hash_registro) hashViolations += 1;
  }
  return {
    checkedRecords: rows.length,
    temporalViolations: temporal,
    probabilitySumViolations: probability,
    hashViolations,
    ok: temporal === 0 && probability === 0 && hashViolations === 0
  };
}

async function historicalLearningSummary(env, limit = 1000) {
  await ensureHistoricalLearningTables(env);
  const totals = await env.DB.prepare(`
    SELECT COUNT(*) AS total_records, COUNT(DISTINCT concurso) AS total_contests,
           COUNT(DISTINCT versao_modelo) AS total_versions
    FROM aprendizado_historico
  `).first();
  const rows = await env.DB.prepare(`
    SELECT concurso, data_sorteio, modelo_chave, modelo_nome, versao_modelo,
           treino_ate, quantidade_treino, probabilidade_soma, ranking_json, resultado_json,
           brier, log_loss, top15, top18, top19, top20, top21, hash_registro, criado_em
    FROM aprendizado_historico
    WHERE versao_modelo = ?
    ORDER BY concurso DESC, modelo_chave ASC
    LIMIT ?
  `).bind(Learning.MODEL_VERSION, Math.min(Math.max(Number(limit || 1000), 20), 2000)).all();
  const models = Object.keys(Learning.MODELS).map((key) => modelAggregate(rows.results, key));
  for (const model of models) await persistModelSummary(env, model);
  const ranked = models.slice().sort((a, b) => {
    const evidenceRank = { moderate: 3, exploratory: 2, none: 1, insufficient: 0 };
    const evidenceDelta = (evidenceRank[b.evidence.level] || 0) - (evidenceRank[a.evidence.level] || 0);
    if (evidenceDelta) return evidenceDelta;
    const aScore = (Learning.BASELINE_BRIER - a.brier) * 100 + (a.avgTop21 - Learning.THEORETICAL_TOP21);
    const bScore = (Learning.BASELINE_BRIER - b.brier) * 100 + (b.avgTop21 - Learning.THEORETICAL_TOP21);
    return bScore - aScore;
  });
  const recent = rows.results.slice(0, 96).map((row) => ({
    concurso: Number(row.concurso), data: row.data_sorteio, model: row.modelo_chave, modelName: row.modelo_nome,
    modelVersion: row.versao_modelo, trainingThrough: Number(row.treino_ate), trainingCount: Number(row.quantidade_treino),
    probabilitySum: Number(row.probabilidade_soma), brier: Number(row.brier), logLoss: Number(row.log_loss),
    top15: Number(row.top15), top18: Number(row.top18), top19: Number(row.top19), top20: Number(row.top20), top21: Number(row.top21),
    hash: row.hash_registro, createdAt: row.criado_em
  }));
  return {
    ok: true,
    purpose: 'historical_evaluation_only',
    modelVersion: Learning.MODEL_VERSION,
    baselines: { brier: Learning.BASELINE_BRIER, logLoss: Learning.BASELINE_LOG_LOSS, top21: Learning.THEORETICAL_TOP21 },
    totalRecords: Number(totals?.total_records || 0),
    totalContests: Number(totals?.total_contests || 0),
    totalVersions: Number(totals?.total_versions || 0),
    currentVersionRecords: rows.results.length,
    bestHistoricalModel: ranked[0] || null,
    models,
    driftAlerts: models.filter((model) => ['moderate', 'high'].includes(model.drift.level)).map((model) => model.key),
    versions: await versionRegistry(env),
    integrity: await integritySummary(env, rows.results),
    recent
  };
}

async function historicalApi(env, url) {
  const requested = Number(url.searchParams.get('tests') || DEFAULT_TESTS);
  const sync = await syncHistoricalLearning(env, requested);
  return json({ ...(await historicalLearningSummary(env)), sync });
}
async function runBaseScheduled(event, env) {
  const tasks = [];
  await baseWorker.scheduled(event, env, { waitUntil(promise) { tasks.push(Promise.resolve(promise)); } });
  await Promise.all(tasks);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === '/api/aprendizado/historico' && request.method === 'GET') {
      try { return await historicalApi(env, url); }
      catch (error) {
        console.error(error);
        return json({ ok: false, message: 'Falha ao atualizar a auditoria histórica robusta.' }, 500);
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
