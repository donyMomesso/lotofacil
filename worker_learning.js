import baseWorker from './worker.js';
import * as Learning from './learning_audit_core.mjs';
import * as Governance from './learning_governance.mjs';
import { applyCerebroOrBlock } from './worker_cerebro_games.js';
import { cleanupExpiredGamesSafe, batchUpdateByIds } from './worker_d1_batch.js';

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

function bytesToHex(bytes) {
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
}

async function sha256Hex(value) {
  const bytes = new TextEncoder().encode(value);
  return bytesToHex(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)));
}

/** Canonicaliza números antes do hash — evita drift de float do SQLite REAL. */
function canonicalHistoricalRecord(record) {
  const ranking = (record.ranking || []).map((row) => ({
    number: Number(row.number),
    probability: Learning.round(Number(row.probability), 8),
    rank: Number(row.rank)
  })).sort((a, b) => a.rank - b.rank || a.number - b.number);
  const result = (record.result || []).map(Number).sort((a, b) => a - b);
  const evaluation = record.evaluation || {};
  return {
    schema: 2,
    purpose: 'historical_evaluation_only',
    contest: Number(record.contest),
    drawDate: String(record.drawDate || ''),
    modelKey: String(record.modelKey || ''),
    modelName: String(record.modelName || ''),
    modelVersion: String(record.modelVersion || ''),
    trainingThrough: Number(record.trainingThrough),
    trainingCount: Number(record.trainingCount),
    probabilitySum: Learning.round(Number(record.probabilitySum), 8),
    ranking,
    result,
    evaluation: {
      brier: Learning.round(Number(evaluation.brier), 8),
      logLoss: Learning.round(Number(evaluation.logLoss), 8),
      top15: Number(evaluation.top15),
      top18: Number(evaluation.top18),
      top19: Number(evaluation.top19),
      top20: Number(evaluation.top20),
      top21: Number(evaluation.top21),
      calibrationError: Learning.round(Number(evaluation.calibrationError), 8),
      sharpness: Learning.round(Number(evaluation.sharpness), 8)
    }
  };
}

async function hashHistoricalRecord(record) {
  return sha256Hex(Learning.stableStringify(canonicalHistoricalRecord(record)));
}
