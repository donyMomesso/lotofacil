import assert from 'node:assert/strict';
import * as core from '../learning_audit_core.mjs';

function makeDraw(contest, shift) {
  const values = [];
  for (let i = 0; i < 15; i += 1) values.push(((i * 7 + shift * 3) % 25) + 1);
  const unique = [...new Set(values)];
  for (let n = 1; unique.length < 15; n += 1) if (!unique.includes(n)) unique.push(n);
  return { concurso: contest, data: `${String((contest % 28) + 1).padStart(2, '0')}/07/2026`, dezenas: unique.sort((a, b) => a - b) };
}

const draws = Array.from({ length: 90 }, (_, i) => makeDraw(3500 + i, i + 1));
assert.equal(core.MODEL_VERSION, 'historical-audit-v1.1.0');
assert.equal(core.BASELINE_BRIER, 0.24);
assert.equal(core.THEORETICAL_TOP21, 12.6);

const score = core.scoreTrainingHistory(draws.slice(0, 50), 'stable');
assert.equal(score.ranking.length, 25);
assert(Math.abs(score.probabilitySum - 15) < 1e-6);

const evaluation = core.evaluateHistoricalScore(score, draws[50].dezenas);
assert(evaluation.brier >= 0 && evaluation.brier <= 1);
assert(evaluation.calibrationError >= 0 && evaluation.calibrationError <= 1);
assert(evaluation.sharpness >= 0);

const wf = core.historicalWalkForward(draws, 'adaptive', { minTraining: 12, maxTests: 60 });
assert.equal(wf.samples, 60);
assert(wf.rows.every((row) => row.trainingThrough < row.concurso), 'walk-forward vazou o concurso alvo');
assert(Number.isFinite(wf.calibrationError));
assert(wf.rows.every((row) => !('ranking' in row)));

const brierValues = wf.rows.map((row) => row.brier);
const ciA = core.bootstrapMeanCI(brierValues, { iterations: 1000, seed: 'fixed' });
const ciB = core.bootstrapMeanCI(brierValues, { iterations: 1000, seed: 'fixed' });
assert.deepEqual(ciA, ciB, 'bootstrap precisa ser reprodutível');
assert(ciA.low <= ciA.mean && ciA.mean <= ciA.high);

const permutation = core.permutationTop21Test(wf.rows.map((row) => row.top21), { iterations: 2000, seed: 'fixed' });
assert(permutation.pValue > 0 && permutation.pValue <= 1);
assert.equal(permutation.baseline, 12.6);

const windows = core.rollingWindows(wf.rows, [8, 16, 24]);
assert.deepEqual(windows.map((item) => item.size), [8, 16, 24]);
assert.equal(windows[0].samples, 8);

const drift = core.detectDrift(wf.rows, 8);
assert(['none', 'moderate', 'high'].includes(drift.level));

const insufficient = core.evidenceAssessment({ samples: 10, brierCI: ciA, top21CI: ciA, permutationPValue: 1 });
assert.equal(insufficient.level, 'insufficient');
const none = core.evidenceAssessment({ samples: 60, brierCI: { high: 0.25 }, top21CI: { low: 12.4 }, permutationPValue: 0.5 });
assert.equal(none.level, 'none');

console.log('OK: robustez histórica, bootstrap, permutação, drift e proteção temporal.');
