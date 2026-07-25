const TOTAL_NUMBERS = 25;
const DRAW_SIZE = 15;
const BASE_RATE = DRAW_SIZE / TOTAL_NUMBERS;
const THEORETICAL_TOP21 = 21 * BASE_RATE;
const BASELINE_BRIER = BASE_RATE * (1 - BASE_RATE);
const BASELINE_LOG_LOSS = -(BASE_RATE * Math.log(BASE_RATE) + (1 - BASE_RATE) * Math.log(1 - BASE_RATE));
const MODEL_VERSION = 'historical-audit-v1.1.0';

const MODELS = {
  stable: {
    key: 'stable',
    name: 'Modelo Estável',
    weights: { freq5: 0.72, freq10: 0.56, freq20: 0.38, freq50: 0.20, trend: 0.34, repeat: 0.16, pair: 0.22, gap: 0.06 },
    temperature: 1.24
  },
  adaptive: {
    key: 'adaptive',
    name: 'Modelo Adaptativo',
    weights: { freq5: 0.92, freq10: 0.58, freq20: 0.22, freq50: 0.10, trend: 0.52, repeat: 0.10, pair: 0.30, gap: 0.03 },
    temperature: 1.34
  }
};

function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
function round(value, digits = 8) {
  const factor = 10 ** digits;
  return Math.round((Number(value) + Number.EPSILON) * factor) / factor;
}
function average(values) {
  const clean = (values || []).map(Number).filter(Number.isFinite);
  return clean.length ? clean.reduce((sum, value) => sum + value, 0) / clean.length : 0;
}
function standardDeviation(values) {
  const clean = (values || []).map(Number).filter(Number.isFinite);
  if (clean.length < 2) return 0;
  const mean = average(clean);
  return Math.sqrt(clean.reduce((sum, value) => sum + (value - mean) ** 2, 0) / clean.length);
}
function quantile(values, probability) {
  const clean = (values || []).map(Number).filter(Number.isFinite).sort((a, b) => a - b);
  if (!clean.length) return 0;
  const p = clamp(Number(probability), 0, 1);
  const position = (clean.length - 1) * p;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return clean[lower];
  return clean[lower] + (clean[upper] - clean[lower]) * (position - lower);
}
function hashSeed(input) {
  const text = String(input || 'lotofacil');
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
function uniqueNumbers(input) {
  return Array.from(new Set((input || []).map(Number)
    .filter((number) => Number.isInteger(number) && number >= 1 && number <= TOTAL_NUMBERS)))
    .sort((a, b) => a - b);
}
function normalizeDraw(draw) {
  const dezenas = uniqueNumbers(draw?.dezenas || draw?.numbers || draw);
  if (dezenas.length !== DRAW_SIZE) return null;
  return { concurso: Number(draw?.concurso || draw?.contest || 0), data: String(draw?.data || draw?.date || ''), dezenas };
}
function normalizeDraws(draws) {
  const seen = new Set();
  return (draws || []).map(normalizeDraw).filter(Boolean).filter((draw) => {
    const key = draw.concurso || draw.dezenas.join('-');
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  }).sort((a, b) => a.concurso - b.concurso);
}
function windowDraws(history, size) { return history.slice(Math.max(0, history.length - size)); }
function frequency(history, number, size) {
  const sample = windowDraws(history, size);
  if (!sample.length) return BASE_RATE;
  return sample.reduce((total, draw) => total + (draw.dezenas.includes(number) ? 1 : 0), 0) / sample.length;
}
function currentDelay(history, number) {
  for (let index = history.length - 1, delay = 0; index >= 0; index -= 1, delay += 1) {
    if (history[index].dezenas.includes(number)) return delay;
  }
  return history.length;
}
function averageGap(history, number) {
  const positions = [];
  history.forEach((draw, index) => { if (draw.dezenas.includes(number)) positions.push(index); });
  if (positions.length < 2) return 1 / BASE_RATE;
  let total = 0;
  for (let index = 1; index < positions.length; index += 1) total += positions[index] - positions[index - 1];
  return total / (positions.length - 1);
}
function pairSupport(history, number) {
  const sample = windowDraws(history, 20);
  const last = history[history.length - 1]?.dezenas || [];
  if (!sample.length || !last.length) return BASE_RATE;
  let total = 0;
  let partners = 0;
  for (const partner of last) {
    if (partner === number) continue;
    let together = 0;
    let partnerCount = 0;
    for (const draw of sample) {
      const hasPartner = draw.dezenas.includes(partner);
      if (hasPartner) partnerCount += 1;
      if (hasPartner && draw.dezenas.includes(number)) together += 1;
    }
    total += partnerCount ? together / partnerCount : BASE_RATE;
    partners += 1;
  }
  return partners ? total / partners : BASE_RATE;
}
function featureVector(history, number) {
  const f5 = frequency(history, number, 5);
  const f10 = frequency(history, number, 10);
  const f20 = frequency(history, number, 20);
  const f50 = frequency(history, number, 50);
  const delay = currentDelay(history, number);
  const avgGap = averageGap(history, number);
  const lastDraw = history[history.length - 1]?.dezenas || [];
  return {
    freq5: f5 - BASE_RATE, freq10: f10 - BASE_RATE, freq20: f20 - BASE_RATE, freq50: f50 - BASE_RATE,
    trend: f5 - f20, repeat: (lastDraw.includes(number) ? 1 : 0) - BASE_RATE,
    pair: pairSupport(history, number) - BASE_RATE,
    gap: clamp((delay - avgGap) / Math.max(2, avgGap * 2), -1, 1)
  };
}
function sigmoid(value) {
  if (value >= 0) { const z = Math.exp(-value); return 1 / (1 + z); }
  const z = Math.exp(value); return z / (1 + z);
}
function calibratedProbabilities(logits, target = DRAW_SIZE) {
  let low = -12;
  let high = 12;
  const probabilitiesFor = (shift) => logits.map((logit) => clamp(sigmoid(logit + shift), 0.18, 0.92));
  for (let iteration = 0; iteration < 100; iteration += 1) {
    const middle = (low + high) / 2;
    const sum = probabilitiesFor(middle).reduce((total, probability) => total + probability, 0);
    if (sum > target) high = middle; else low = middle;
  }
  return probabilitiesFor((low + high) / 2);
}
function scoreTrainingHistory(draws, modelKey = 'stable') {
  const history = normalizeDraws(draws);
  if (history.length < 8) throw new Error('Histórico insuficiente para avaliação.');
  const model = MODELS[modelKey] || MODELS.stable;
  const baseLogit = Math.log(BASE_RATE / (1 - BASE_RATE));
  const rows = [];
  const logits = [];
  for (let number = 1; number <= TOTAL_NUMBERS; number += 1) {
    const features = featureVector(history, number);
    let adjustment = 0;
    for (const [key, weight] of Object.entries(model.weights)) adjustment += Number(features[key] || 0) * weight;
    const logit = baseLogit + adjustment / model.temperature;
    rows.push({ number, logit });
    logits.push(logit);
  }
  const probabilities = calibratedProbabilities(logits);
  rows.forEach((row, index) => { row.probability = probabilities[index]; });
  rows.sort((a, b) => b.probability - a.probability || a.number - b.number);
  rows.forEach((row, index) => { row.rank = index + 1; });
  return {
    model: model.key, modelName: model.name, modelVersion: MODEL_VERSION,
    trainingThrough: history[history.length - 1].concurso, drawsUsed: history.length,
    probabilitySum: round(rows.reduce((total, row) => total + row.probability, 0)), ranking: rows
  };
}
function logLossTerm(probability, actual) {
  const p = clamp(probability, 1e-9, 1 - 1e-9);
  return -(actual * Math.log(p) + (1 - actual) * Math.log(1 - p));
}
function calibrationDiagnostics(ranking, actualNumbers, binCount = 5) {
  const actual = new Set(uniqueNumbers(actualNumbers));
  const rows = (ranking || []).map((row) => ({ probability: Number(row.probability), actual: actual.has(Number(row.number)) ? 1 : 0 }))
    .filter((row) => Number.isFinite(row.probability));
  if (rows.length !== TOTAL_NUMBERS || actual.size !== DRAW_SIZE) throw new Error('Dados insuficientes para calibração.');
  const bins = Array.from({ length: Math.max(2, Number(binCount || 5)) }, (_, index) => ({ index, count: 0, predicted: 0, observed: 0 }));
  for (const row of rows) {
    const index = Math.min(bins.length - 1, Math.floor(clamp(row.probability, 0, 0.999999) * bins.length));
    bins[index].count += 1;
    bins[index].predicted += row.probability;
    bins[index].observed += row.actual;
  }
  let ece = 0;
  const normalized = bins.filter((bin) => bin.count).map((bin) => {
    const predicted = bin.predicted / bin.count;
    const observed = bin.observed / bin.count;
    ece += (bin.count / rows.length) * Math.abs(predicted - observed);
    return { index: bin.index, count: bin.count, predicted: round(predicted), observed: round(observed), gap: round(observed - predicted) };
  });
  return { ece: round(ece), sharpness: round(standardDeviation(rows.map((row) => row.probability))), bins: normalized };
}
function evaluateHistoricalScore(score, actualNumbers) {
  const actual = new Set(uniqueNumbers(actualNumbers));
  if (actual.size !== DRAW_SIZE) throw new Error('Resultado histórico inválido.');
  if (!score?.ranking || score.ranking.length !== TOTAL_NUMBERS) throw new Error('Ranking histórico incompleto.');
  let brier = 0;
  let logLoss = 0;
  for (const row of score.ranking) {
    const y = actual.has(row.number) ? 1 : 0;
    brier += (row.probability - y) ** 2;
    logLoss += logLossTerm(row.probability, y);
  }
  const hits = (size) => score.ranking.slice(0, size).reduce((total, row) => total + (actual.has(row.number) ? 1 : 0), 0);
  const calibration = calibrationDiagnostics(score.ranking, actualNumbers);
  return {
    brier: round(brier / TOTAL_NUMBERS), logLoss: round(logLoss / TOTAL_NUMBERS),
    top15: hits(15), top18: hits(18), top19: hits(19), top20: hits(20), top21: hits(21),
    calibrationError: calibration.ece, sharpness: calibration.sharpness
  };
}
function historicalWalkForward(draws, modelKey = 'stable', options = {}) {
  const history = normalizeDraws(draws);
  const minTraining = Math.max(8, Number(options.minTraining || 12));
  const maxTests = Math.max(1, Number(options.maxTests || 60));
  const start = Math.max(minTraining, history.length - maxTests);
  const rows = [];
  for (let targetIndex = start; targetIndex < history.length; targetIndex += 1) {
    const training = history.slice(0, targetIndex);
    const target = history[targetIndex];
    const score = scoreTrainingHistory(training, modelKey);
    if (score.trainingThrough >= target.concurso) throw new Error(`Vazamento temporal no concurso ${target.concurso}.`);
    rows.push({ concurso: target.concurso, data: target.data, trainingThrough: score.trainingThrough, trainingCount: score.drawsUsed, ...evaluateHistoricalScore(score, target.dezenas) });
  }
  const fieldAverage = (key) => average(rows.map((row) => row[key]));
  return {
    model: modelKey, modelName: (MODELS[modelKey] || MODELS.stable).name, modelVersion: MODEL_VERSION,
    samples: rows.length, brier: round(fieldAverage('brier')), logLoss: round(fieldAverage('logLoss')),
    calibrationError: round(fieldAverage('calibrationError')), sharpness: round(fieldAverage('sharpness')),
    avgTop15: round(fieldAverage('top15'), 4), avgTop18: round(fieldAverage('top18'), 4),
    avgTop19: round(fieldAverage('top19'), 4), avgTop20: round(fieldAverage('top20'), 4), avgTop21: round(fieldAverage('top21'), 4),
    deltaTop21: round(fieldAverage('top21') - THEORETICAL_TOP21, 4), deltaBrier: round(BASELINE_BRIER - fieldAverage('brier')), rows
  };
}
function bootstrapMeanCI(values, options = {}) {
  const clean = (values || []).map(Number).filter(Number.isFinite);
  if (!clean.length) return { mean: 0, low: 0, high: 0, confidence: 0.95, iterations: 0 };
  const iterations = Math.max(200, Math.min(10000, Number(options.iterations || 2000)));
  const confidence = clamp(Number(options.confidence || 0.95), 0.5, 0.999);
  const random = seededRandom(options.seed || `bootstrap-${clean.length}`);
  const means = [];
  for (let iteration = 0; iteration < iterations; iteration += 1) {
    let total = 0;
    for (let index = 0; index < clean.length; index += 1) total += clean[Math.floor(random() * clean.length)];
    means.push(total / clean.length);
  }
  const alpha = (1 - confidence) / 2;
  return { mean: round(average(clean)), low: round(quantile(means, alpha)), high: round(quantile(means, 1 - alpha)), confidence, iterations };
}
function sampleHypergeometric(random, population = TOTAL_NUMBERS, successes = DRAW_SIZE, draws = 21) {
  let remainingPopulation = population;
  let remainingSuccesses = successes;
  let hits = 0;
  for (let index = 0; index < draws; index += 1) {
    if (random() < remainingSuccesses / remainingPopulation) { hits += 1; remainingSuccesses -= 1; }
    remainingPopulation -= 1;
  }
  return hits;
}
function permutationTop21Test(observedValues, options = {}) {
  const clean = (observedValues || []).map(Number).filter(Number.isFinite);
  if (!clean.length) return { observed: 0, baseline: THEORETICAL_TOP21, pValue: 1, iterations: 0 };
  const iterations = Math.max(500, Math.min(20000, Number(options.iterations || 5000)));
  const random = seededRandom(options.seed || `permutation-${clean.length}`);
  const observed = average(clean);
  let equalOrBetter = 0;
  for (let iteration = 0; iteration < iterations; iteration += 1) {
    let total = 0;
    for (let sample = 0; sample < clean.length; sample += 1) total += sampleHypergeometric(random);
    if (total / clean.length >= observed - 1e-12) equalOrBetter += 1;
  }
  return { observed: round(observed, 4), baseline: THEORETICAL_TOP21, pValue: round((equalOrBetter + 1) / (iterations + 1), 6), iterations };
}
function rollingWindows(rows, sizes = [8, 16, 24]) {
  const ordered = (rows || []).slice().sort((a, b) => Number(a.concurso) - Number(b.concurso));
  return sizes.map((size) => {
    const selected = ordered.slice(-Math.max(1, Number(size)));
    return {
      size: Number(size), samples: selected.length,
      firstContest: selected[0]?.concurso || null, lastContest: selected[selected.length - 1]?.concurso || null,
      brier: round(average(selected.map((row) => row.brier))),
      logLoss: round(average(selected.map((row) => row.logLoss ?? row.log_loss))),
      avgTop21: round(average(selected.map((row) => row.top21)), 4),
      calibrationError: round(average(selected.map((row) => row.calibrationError ?? row.calibration_error)))
    };
  });
}
function detectDrift(rows, windowSize = 8) {
  const ordered = (rows || []).slice().sort((a, b) => Number(a.concurso) - Number(b.concurso));
  const size = Math.max(4, Number(windowSize || 8));
  if (ordered.length < size * 2) return { level: 'insufficient', reason: 'Amostra insuficiente para comparar duas janelas.', windowSize: size };
  const recent = ordered.slice(-size);
  const previous = ordered.slice(-size * 2, -size);
  const recentBrier = average(recent.map((row) => row.brier));
  const previousBrier = average(previous.map((row) => row.brier));
  const recentTop21 = average(recent.map((row) => row.top21));
  const previousTop21 = average(previous.map((row) => row.top21));
  const brierDelta = recentBrier - previousBrier;
  const top21Delta = recentTop21 - previousTop21;
  let level = 'none';
  if (brierDelta > 0.02 || top21Delta < -0.6) level = 'high';
  else if (brierDelta > 0.01 || top21Delta < -0.3) level = 'moderate';
  return {
    level, windowSize: size, brierDelta: round(brierDelta), top21Delta: round(top21Delta, 4),
    recent: { brier: round(recentBrier), avgTop21: round(recentTop21, 4) },
    previous: { brier: round(previousBrier), avgTop21: round(previousTop21, 4) },
    reason: level === 'none' ? 'Sem piora relevante entre as duas janelas.' : 'A janela recente piorou em Brier ou top 21.'
  };
}
function evidenceAssessment({ samples, brierCI, top21CI, permutationPValue }) {
  if (samples < 20) return { level: 'insufficient', label: 'Amostra insuficiente', reason: 'São necessários ao menos 20 concursos fora da amostra.' };
  const beatsBrier = Number(brierCI?.high) < BASELINE_BRIER;
  const beatsTop21 = Number(top21CI?.low) > THEORETICAL_TOP21 && Number(permutationPValue) < 0.05;
  if (beatsBrier && beatsTop21 && samples >= 50) return { level: 'moderate', label: 'Sinal histórico moderado', reason: 'As duas métricas superaram as referências com IC de 95% e amostra maior.' };
  if (beatsBrier || beatsTop21) return { level: 'exploratory', label: 'Sinal histórico exploratório', reason: 'Uma métrica superou a referência; ainda requer mais concursos e estabilidade.' };
  return { level: 'none', label: 'Sem evidência de vantagem', reason: 'Os intervalos de confiança ainda incluem as referências neutras.' };
}
function stableStringify(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
}

export {
  TOTAL_NUMBERS, DRAW_SIZE, BASE_RATE, THEORETICAL_TOP21, BASELINE_BRIER, BASELINE_LOG_LOSS,
  MODEL_VERSION, MODELS, normalizeDraws, scoreTrainingHistory, calibrationDiagnostics,
  evaluateHistoricalScore, historicalWalkForward, bootstrapMeanCI, permutationTop21Test,
  rollingWindows, detectDrift, evidenceAssessment, stableStringify, round, average, standardDeviation
};
