const GOVERNANCE_VERSION = 'champion-governance-v1.0.0';
const MIN_PAIRED_SAMPLES = 30;
const MIN_CONTESTS_BETWEEN_PROMOTIONS = 12;
const ALPHA = 0.05;

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function round(value, digits = 8) {
  const factor = 10 ** digits;
  return Math.round((Number(value) + Number.EPSILON) * factor) / factor;
}

function average(values) {
  const clean = (values || []).map(Number).filter(Number.isFinite);
  return clean.length ? clean.reduce((sum, value) => sum + value, 0) / clean.length : 0;
}

function quantile(values, probability) {
  const clean = (values || []).map(Number).filter(Number.isFinite).sort((a, b) => a - b);
  if (!clean.length) return 0;
  const position = (clean.length - 1) * clamp(Number(probability), 0, 1);
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return clean[lower];
  return clean[lower] + (clean[upper] - clean[lower]) * (position - lower);
}

function hashSeed(input) {
  const text = String(input || 'lotofacil-governance');
  let hash = 2166136261;
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function seededRandom(seedInput) {
  let state = hashSeed(seedInput) || 0x6d2b79f5;
  return () => {
    state += 0x6d2b79f5;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function normalizeMetricRows(rows) {
  const byContest = new Map();
  for (const row of rows || []) {
    const contest = Number(row.concurso ?? row.contest);
    const brier = Number(row.brier);
    const top21 = Number(row.top21);
    if (!Number.isInteger(contest) || !Number.isFinite(brier) || !Number.isFinite(top21)) continue;
    byContest.set(contest, { contest, brier, top21 });
  }
  return Array.from(byContest.values()).sort((a, b) => a.contest - b.contest);
}

function alignModelRows(championRows, challengerRows) {
  const champion = new Map(normalizeMetricRows(championRows).map((row) => [row.contest, row]));
  const challenger = new Map(normalizeMetricRows(challengerRows).map((row) => [row.contest, row]));
  return Array.from(champion.keys())
    .filter((contest) => challenger.has(contest))
    .sort((a, b) => a - b)
    .map((contest) => ({ contest, champion: champion.get(contest), challenger: challenger.get(contest) }));
}

function pairedBootstrapMeanCI(values, options = {}) {
  const clean = (values || []).map(Number).filter(Number.isFinite);
  if (!clean.length) return { mean: 0, low: 0, high: 0, confidence: 0.95, iterations: 0 };
  const iterations = Math.max(500, Math.min(10000, Number(options.iterations || 4000)));
  const confidence = clamp(Number(options.confidence || 0.95), 0.5, 0.999);
  const random = seededRandom(options.seed || `paired-bootstrap-${clean.length}`);
  const means = [];
  for (let iteration = 0; iteration < iterations; iteration += 1) {
    let total = 0;
    for (let index = 0; index < clean.length; index += 1) total += clean[Math.floor(random() * clean.length)];
    means.push(total / clean.length);
  }
  const alpha = (1 - confidence) / 2;
  return {
    mean: round(average(clean)),
    low: round(quantile(means, alpha)),
    high: round(quantile(means, 1 - alpha)),
    confidence,
    iterations
  };
}

function signFlipPValue(values, options = {}) {
  const clean = (values || []).map(Number).filter(Number.isFinite);
  if (!clean.length) return { observed: 0, pValue: 1, iterations: 0 };
  const observed = average(clean);
  if (observed <= 0) return { observed: round(observed), pValue: 1, iterations: 0 };
  const iterations = Math.max(1000, Math.min(50000, Number(options.iterations || 10000)));
  const random = seededRandom(options.seed || `sign-flip-${clean.length}`);
  let equalOrBetter = 0;
  for (let iteration = 0; iteration < iterations; iteration += 1) {
    let total = 0;
    for (const value of clean) total += (random() < 0.5 ? -value : value);
    if (total / clean.length >= observed - 1e-12) equalOrBetter += 1;
  }
  return {
    observed: round(observed),
    pValue: round((equalOrBetter + 1) / (iterations + 1), 8),
    iterations
  };
}

function benjaminiHochberg(tests, alpha = ALPHA) {
  const normalized = (tests || []).map((test, index) => ({
    id: String(test.id ?? index),
    pValue: clamp(Number(test.pValue), 0, 1),
    originalIndex: index
  })).sort((a, b) => a.pValue - b.pValue || a.originalIndex - b.originalIndex);
  const total = normalized.length;
  let runningMinimum = 1;
  for (let index = total - 1; index >= 0; index -= 1) {
    const rank = index + 1;
    runningMinimum = Math.min(runningMinimum, normalized[index].pValue * total / rank);
    normalized[index].qValue = round(clamp(runningMinimum, 0, 1), 8);
    normalized[index].rejected = normalized[index].qValue <= alpha;
  }
  return normalized.sort((a, b) => a.originalIndex - b.originalIndex)
    .map(({ originalIndex, ...test }) => test);
}

function windowComparisons(pairs, sizes = [8, 16, 24]) {
  return sizes.map((rawSize) => {
    const size = Math.max(1, Number(rawSize));
    const selected = pairs.slice(-size);
    const brierGain = average(selected.map((pair) => pair.champion.brier - pair.challenger.brier));
    const top21Gain = average(selected.map((pair) => pair.challenger.top21 - pair.champion.top21));
    const passed = selected.length >= Math.min(8, size) && brierGain > 0 && top21Gain >= -0.125;
    return {
      size,
      samples: selected.length,
      firstContest: selected[0]?.contest || null,
      lastContest: selected[selected.length - 1]?.contest || null,
      brierGain: round(brierGain),
      top21Gain: round(top21Gain, 4),
      passed
    };
  });
}

function compareChampionChallenger(championRows, challengerRows, options = {}) {
  const pairs = alignModelRows(championRows, challengerRows);
  const championKey = String(options.championKey || 'champion');
  const challengerKey = String(options.challengerKey || 'challenger');
  const seed = `${GOVERNANCE_VERSION}-${championKey}-${challengerKey}-${pairs.length}-${pairs[pairs.length - 1]?.contest || 0}`;
  const brierGains = pairs.map((pair) => pair.champion.brier - pair.challenger.brier);
  const top21Gains = pairs.map((pair) => pair.challenger.top21 - pair.champion.top21);
  const brierCI = pairedBootstrapMeanCI(brierGains, { seed: `${seed}-brier` });
  const top21CI = pairedBootstrapMeanCI(top21Gains, { seed: `${seed}-top21` });
  const rawTests = [
    { id: 'brier', ...signFlipPValue(brierGains, { seed: `${seed}-brier-test` }) },
    { id: 'top21', ...signFlipPValue(top21Gains, { seed: `${seed}-top21-test` }) }
  ];
  const corrected = benjaminiHochberg(rawTests.map((test) => ({ id: test.id, pValue: test.pValue })), options.alpha || ALPHA);
  const tests = rawTests.map((test) => ({
    ...test,
    qValue: corrected.find((item) => item.id === test.id)?.qValue ?? 1,
    rejected: corrected.find((item) => item.id === test.id)?.rejected ?? false
  }));
  return {
    governanceVersion: GOVERNANCE_VERSION,
    championKey,
    challengerKey,
    pairedSamples: pairs.length,
    firstContest: pairs[0]?.contest || null,
    latestContest: pairs[pairs.length - 1]?.contest || null,
    brierGain: brierCI.mean,
    brierGainCI: brierCI,
    top21Gain: top21CI.mean,
    top21GainCI: top21CI,
    tests,
    windows: windowComparisons(pairs, options.windowSizes || [8, 16, 24])
  };
}

function promotionDecision(comparison, context = {}) {
  const brierTest = comparison?.tests?.find((test) => test.id === 'brier') || { qValue: 1 };
  const integrityOk = context.integrityOk === true;
  const driftLevel = String(context.challengerDriftLevel || 'insufficient');
  const contestsSincePromotion = Number(context.contestsSincePromotion || 0);
  const checks = [
    { id: 'samples', label: `Mínimo de ${MIN_PAIRED_SAMPLES} concursos pareados`, passed: Number(comparison?.pairedSamples || 0) >= MIN_PAIRED_SAMPLES },
    { id: 'integrity', label: 'Integridade temporal, probabilística e de hashes', passed: integrityOk },
    { id: 'cooldown', label: `Intervalo mínimo de ${MIN_CONTESTS_BETWEEN_PROMOTIONS} concursos`, passed: contestsSincePromotion >= MIN_CONTESTS_BETWEEN_PROMOTIONS },
    { id: 'drift', label: 'Desafiante sem drift moderado ou alto', passed: driftLevel === 'none' },
    { id: 'brier-direction', label: 'Brier médio do desafiante é menor', passed: Number(comparison?.brierGain || 0) > 0 },
    { id: 'brier-ci', label: 'IC95% da melhora de Brier está acima de zero', passed: Number(comparison?.brierGainCI?.low || 0) > 0 },
    { id: 'multiple-tests', label: `Valor-q Benjamini–Hochberg ≤ ${ALPHA}`, passed: Number(brierTest.qValue || 1) <= ALPHA },
    { id: 'top21-safety', label: 'Sem regressão relevante no top 21', passed: Number(comparison?.top21GainCI?.low ?? -Infinity) >= -0.15 },
    { id: 'windows', label: 'Estabilidade nas janelas 8, 16 e 24', passed: Boolean(comparison?.windows?.length) && comparison.windows.every((window) => window.passed) }
  ];
  const failed = checks.filter((check) => !check.passed);
  const criticalFailure = failed.some((check) => ['integrity'].includes(check.id));
  const status = criticalFailure ? 'blocked' : failed.length ? 'hold' : 'promote';
  return {
    governanceVersion: GOVERNANCE_VERSION,
    status,
    promotedModel: status === 'promote' ? comparison.challengerKey : null,
    checks,
    failedChecks: failed.map((check) => check.id),
    reason: status === 'promote'
      ? 'O desafiante cumpriu todas as regras de promoção histórica.'
      : failed.map((check) => check.label).join('; '),
    policy: {
      minimumPairedSamples: MIN_PAIRED_SAMPLES,
      minimumContestsBetweenPromotions: MIN_CONTESTS_BETWEEN_PROMOTIONS,
      alpha: ALPHA
    }
  };
}

export {
  GOVERNANCE_VERSION,
  MIN_PAIRED_SAMPLES,
  MIN_CONTESTS_BETWEEN_PROMOTIONS,
  ALPHA,
  normalizeMetricRows,
  alignModelRows,
  pairedBootstrapMeanCI,
  signFlipPValue,
  benjaminiHochberg,
  windowComparisons,
  compareChampionChallenger,
  promotionDecision
};
