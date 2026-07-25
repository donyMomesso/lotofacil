import assert from 'node:assert/strict';
import {
  BASELINE_BRIER,
  THEORETICAL_TOP21,
  MODEL_VERSION,
  scoreTrainingHistory,
  evaluateHistoricalScore,
  historicalWalkForward
} from '../learning_audit_core.mjs';

const draws = Array.from({ length: 50 }, (_, index) => {
  const start = (index * 7) % 25;
  const dezenas = Array.from({ length: 15 }, (_value, offset) => ((start + offset * 3) % 25) + 1)
    .sort((a, b) => a - b);
  return { concurso: 4000 + index, data: `${String((index % 28) + 1).padStart(2, '0')}/01/2026`, dezenas };
});

assert.equal(MODEL_VERSION, 'historical-audit-v1.0.0');
assert.equal(BASELINE_BRIER, 0.24);
assert.equal(THEORETICAL_TOP21, 12.6);

const training = draws.slice(0, 30);
const target = draws[30];
const score = scoreTrainingHistory(training, 'stable');
assert.equal(score.trainingThrough, draws[29].concurso);
assert.ok(score.trainingThrough < target.concurso);
assert.equal(score.ranking.length, 25);
assert.ok(Math.abs(score.probabilitySum - 15) < 1e-6);

const evaluation = evaluateHistoricalScore(score, target.dezenas);
assert.ok(evaluation.brier >= 0 && evaluation.brier <= 1);
assert.ok(evaluation.top21 >= 11 && evaluation.top21 <= 15);

const report = historicalWalkForward(draws, 'adaptive', { minTraining: 12, maxTests: 18 });
assert.equal(report.samples, 18);
assert.ok(report.rows.every((row) => row.trainingThrough < row.concurso));
assert.ok(report.rows.every((row) => !('ranking' in row)));

console.log('Motor histórico: testes concluídos com sucesso.');
