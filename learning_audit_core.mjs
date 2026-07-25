const TOTAL_NUMBERS = 25;
const DRAW_SIZE = 15;
const BASE_RATE = DRAW_SIZE / TOTAL_NUMBERS;
const THEORETICAL_TOP21 = 21 * BASE_RATE;
const BASELINE_BRIER = BASE_RATE * (1 - BASE_RATE);
const MODEL_VERSION = 'historical-audit-v1.0.0';

const MODELS = {
  stable: {
    key: 'stable',
    name: 'Modelo Estável',
    weights: {
      freq5: 0.72,
      freq10: 0.56,
      freq20: 0.38,
      freq50: 0.20,
      trend: 0.34,
      repeat: 0.16,
      pair: 0.22,
      gap: 0.06
    },
    temperature: 1.24
  },
  adaptive: {
    key: 'adaptive',
    name: 'Modelo Adaptativo',
    weights: {
      freq5: 0.92,
      freq10: 0.58,
      freq20: 0.22,
      freq50: 0.10,
      trend: 0.52,
      repeat: 0.10,
      pair: 0.30,
      gap: 0.03
    },
    temperature: 1.34
  }
};

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function round(value, digits = 8) {
  const factor = 10 ** digits;
  return Math.round((Number(value) + Number.EPSILON) * factor) / factor;
}

function uniqueNumbers(input) {
  return Array.from(new Set((input || [])
    .map(Number)
    .filter((number) => Number.isInteger(number) && number >= 1 && number <= TOTAL_NUMBERS)))
    .sort((a, b) => a - b);
}

function normalizeDraw(draw) {
  const dezenas = uniqueNumbers(draw?.dezenas || draw?.numbers || draw);
  if (dezenas.length !== DRAW_SIZE) return null;
  return {
    concurso: Number(draw?.concurso || draw?.contest || 0),
    data: String(draw?.data || draw?.date || ''),
    dezenas
  };
}

function normalizeDraws(draws) {
  const seen = new Set();
  return (draws || [])
    .map(normalizeDraw)
    .filter(Boolean)
    .filter((draw) => {
      const key = draw.concurso || draw.dezenas.join('-');
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .sort((a, b) => a.concurso - b.concurso);
}

function windowDraws(history, size) {
  return history.slice(Math.max(0, history.length - size));
}

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
  history.forEach((draw, index) => {
    if (draw.dezenas.includes(number)) positions.push(index);
  });
  if (positions.length < 2) return 1 / BASE_RATE;
  let total = 0;
  for (let index = 1; index < positions.length; index += 1) {
    total += positions[index] - positions[index - 1];
  }
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
    freq5: f5 - BASE_RATE,
    freq10: f10 - BASE_RATE,
    freq20: f20 - BASE_RATE,
    freq50: f50 - BASE_RATE,
    trend: f5 - f20,
    repeat: (lastDraw.includes(number) ? 1 : 0) - BASE_RATE,
    pair: pairSupport(history, number) - BASE_RATE,
    gap: clamp((delay - avgGap) / Math.max(2, avgGap * 2), -1, 1)
  };
}

function sigmoid(value) {
  if (value >= 0) {
    const z = Math.exp(-value);
    return 1 / (1 + z);
  }
  const z = Math.exp(value);
  return z / (1 + z);
}

function calibratedProbabilities(logits, target = DRAW_SIZE) {
  let low = -12;
  let high = 12;
  const probabilitiesFor = (shift) => logits.map((logit) => clamp(sigmoid(logit + shift), 0.18, 0.92));
  for (let iteration = 0; iteration < 100; iteration += 1) {
    const middle = (low + high) / 2;
    const sum = probabilitiesFor(middle).reduce((total, probability) => total + probability, 0);
    if (sum > target) high = middle;
    else low = middle;
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
    for (const [key, weight] of Object.entries(model.weights)) {
      adjustment += Number(features[key] || 0) * weight;
    }
    const logit = baseLogit + adjustment / model.temperature;
    rows.push({ number, logit });
    logits.push(logit);
  }

  const probabilities = calibratedProbabilities(logits);
  rows.forEach((row, index) => {
    row.probability = probabilities[index];
  });
  rows.sort((a, b) => b.probability - a.probability || a.number - b.number);
  rows.forEach((row, index) => { row.rank = index + 1; });

  return {
    model: model.key,
    modelName: model.name,
    modelVersion: MODEL_VERSION,
    trainingThrough: history[history.length - 1].concurso,
    drawsUsed: history.length,
    probabilitySum: round(rows.reduce((total, row) => total + row.probability, 0)),
    ranking: rows
  };
}

function logLossTerm(probability, actual) {
  const p = clamp(probability, 1e-9, 1 - 1e-9);
  return -(actual * Math.log(p) + (1 - actual) * Math.log(1 - p));
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
  const hits = (size) => score.ranking.slice(0, size)
    .reduce((total, row) => total + (actual.has(row.number) ? 1 : 0), 0);
  return {
    brier: round(brier / TOTAL_NUMBERS),
    logLoss: round(logLoss / TOTAL_NUMBERS),
    top15: hits(15),
    top18: hits(18),
    top19: hits(19),
    top20: hits(20),
    top21: hits(21)
  };
}

function historicalWalkForward(draws, modelKey = 'stable', options = {}) {
  const history = normalizeDraws(draws);
  const minTraining = Math.max(8, Number(options.minTraining || 12));
  const maxTests = Math.max(1, Number(options.maxTests || 24));
  const start = Math.max(minTraining, history.length - maxTests);
  const rows = [];
  for (let targetIndex = start; targetIndex < history.length; targetIndex += 1) {
    const training = history.slice(0, targetIndex);
    const target = history[targetIndex];
    const score = scoreTrainingHistory(training, modelKey);
    const metrics = evaluateHistoricalScore(score, target.dezenas);
    rows.push({
      concurso: target.concurso,
      data: target.data,
      trainingThrough: score.trainingThrough,
      trainingCount: score.drawsUsed,
      ...metrics
    });
  }
  const average = (key) => rows.length
    ? rows.reduce((total, row) => total + Number(row[key] || 0), 0) / rows.length
    : 0;
  return {
    model: modelKey,
    modelName: (MODELS[modelKey] || MODELS.stable).name,
    modelVersion: MODEL_VERSION,
    samples: rows.length,
    brier: round(average('brier')),
    logLoss: round(average('logLoss')),
    avgTop15: round(average('top15'), 4),
    avgTop18: round(average('top18'), 4),
    avgTop19: round(average('top19'), 4),
    avgTop20: round(average('top20'), 4),
    avgTop21: round(average('top21'), 4),
    deltaTop21: round(average('top21') - THEORETICAL_TOP21, 4),
    deltaBrier: round(BASELINE_BRIER - average('brier')),
    rows
  };
}

function stableStringify(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
}

export {
  TOTAL_NUMBERS,
  DRAW_SIZE,
  BASE_RATE,
  THEORETICAL_TOP21,
  BASELINE_BRIER,
  MODEL_VERSION,
  MODELS,
  normalizeDraws,
  scoreTrainingHistory,
  evaluateHistoricalScore,
  historicalWalkForward,
  stableStringify,
  round
};
