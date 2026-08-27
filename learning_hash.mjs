/** Canonical hash helpers for aprendizado_historico (avoid SQLite REAL drift). */
import * as Learning from './learning_audit_core.mjs';

function bytesToHex(bytes) {
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
}

async function sha256Hex(value) {
  const bytes = new TextEncoder().encode(value);
  return bytesToHex(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)));
}

export function canonicalHistoricalRecord(record) {
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

export async function hashHistoricalRecord(record) {
  return sha256Hex(Learning.stableStringify(canonicalHistoricalRecord(record)));
}

export { sha256Hex };
