import assert from 'node:assert/strict';
import {
  GOVERNANCE_VERSION,
  benjaminiHochberg,
  compareChampionChallenger,
  promotionDecision
} from '../learning_governance.mjs';

assert.equal(GOVERNANCE_VERSION, 'champion-governance-v1.0.0');

const championRows = Array.from({ length: 48 }, (_, index) => ({
  concurso: 5000 + index,
  brier: 0.25 + (index % 3) * 0.0002,
  top21: 12 + (index % 2)
}));
const challengerRows = championRows.map((row, index) => ({
  concurso: row.concurso,
  brier: row.brier - 0.018 - (index % 2) * 0.0001,
  top21: row.top21 + 0.25
}));

const comparison = compareChampionChallenger(championRows, challengerRows, {
  championKey: 'stable',
  challengerKey: 'adaptive'
});
assert.equal(comparison.pairedSamples, 48);
assert.ok(comparison.brierGain > 0);
assert.ok(comparison.brierGainCI.low > 0);
assert.ok(comparison.tests.find((test) => test.id === 'brier').qValue <= 0.05);
assert.ok(comparison.windows.every((window) => window.passed));

const decision = promotionDecision(comparison, {
  integrityOk: true,
  challengerDriftLevel: 'none',
  contestsSincePromotion: 30
});
assert.equal(decision.status, 'promote');
assert.equal(decision.promotedModel, 'adaptive');
assert.ok(decision.checks.every((check) => check.passed));

const cooldownDecision = promotionDecision(comparison, {
  integrityOk: true,
  challengerDriftLevel: 'none',
  contestsSincePromotion: 3
});
assert.equal(cooldownDecision.status, 'hold');
assert.ok(cooldownDecision.failedChecks.includes('cooldown'));

const blockedDecision = promotionDecision(comparison, {
  integrityOk: false,
  challengerDriftLevel: 'none',
  contestsSincePromotion: 30
});
assert.equal(blockedDecision.status, 'blocked');

const corrected = benjaminiHochberg([
  { id: 'a', pValue: 0.01 },
  { id: 'b', pValue: 0.04 },
  { id: 'c', pValue: 0.03 }
]);
assert.deepEqual(corrected.map((item) => item.id), ['a', 'b', 'c']);
assert.ok(corrected.every((item) => item.qValue >= item.pValue));
assert.ok(corrected.find((item) => item.id === 'a').rejected);

console.log('Governança Champion Challenger: promoção, bloqueios e Benjamini–Hochberg validados.');
