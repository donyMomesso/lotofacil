(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.LotofacilLearningCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const TOTAL_NUMBERS = 25;
  const DRAW_SIZE = 15;
  const BASE_RATE = DRAW_SIZE / TOTAL_NUMBERS;
  const THEORETICAL_TOP21 = 21 * BASE_RATE;
  const BASELINE_BRIER = BASE_RATE * (1 - BASE_RATE);
  const MODEL_VERSION = 'learning-v1.0.0';

  const MODELS = {
    stable: {
      key: 'stable',
      name: 'Champion Estável',
      description: 'Prioriza estabilidade entre janelas, tendência moderada e baixa confiança em atraso.',
      weights: {
        freq5: 0.72,
        freq10: 0.56,
        freq20: 0.38,
        freq50: 0.20,
        trend: 0.34,
        repeat: 0.16,
        pair: 0.22,
        gap: 0.06,
        method: 0.34,
        lab: 0.24,
        week: 0.14
      },
      temperature: 1.24
    },
    adaptive: {
      key: 'adaptive',
      name: 'Challenger Adaptativo',
      description: 'Reage mais à janela curta, aos votos M1–M9 e aos sinais recentes do laboratório.',
      weights: {
        freq5: 0.92,
        freq10: 0.58,
        freq20: 0.22,
        freq50: 0.10,
        trend: 0.52,
        repeat: 0.10,
        pair: 0.30,
        gap: 0.03,
        method: 0.48,
        lab: 0.34,
        week: 0.24
      },
      temperature: 1.34
    }
  };

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function round(value, digits = 6) {
    const factor = 10 ** digits;
    return Math.round((Number(value) + Number.EPSILON) * factor) / factor;
  }

  function pad(number) {
    return String(number).padStart(2, '0');
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
    const count = sample.reduce((total, draw) => total + (draw.dezenas.includes(number) ? 1 : 0), 0);
    return count / sample.length;
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
    for (let index = 1; index < positions.length; index += 1) total += positions[index] - positions[index - 1];
    return total / (positions.length - 1);
  }

  function pairSupport(history, number) {
    const sample = windowDraws(history, 20);
    const last = history[history.length - 1]?.dezenas || [];
    if (!sample.length || !last.length) return BASE_RATE;
    let total = 0;
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
    }
    return total / Math.max(1, last.length - (last.includes(number) ? 1 : 0));
  }

  function normalizeVoteMap(map) {
    const values = Array.from({ length: TOTAL_NUMBERS }, (_, index) => Number(map.get(index + 1) || 0));
    const max = Math.max(0, ...values);
    if (!max) return new Map(values.map((_value, index) => [index + 1, BASE_RATE]));
    return new Map(values.map((value, index) => [index + 1, value / max]));
  }

  function systemMethodVotes(status) {
    const games = status?.jogos_gerados || [];
    const counts = new Map(Array.from({ length: TOTAL_NUMBERS }, (_, index) => [index + 1, 0]));
    for (const game of games) {
      for (const number of uniqueNumbers(game.dezenas)) counts.set(number, counts.get(number) + 1);
    }
    if (!games.length) return new Map(Array.from({ length: TOTAL_NUMBERS }, (_, index) => [index + 1, BASE_RATE]));
    return new Map(Array.from({ length: TOTAL_NUMBERS }, (_, index) => [index + 1, counts.get(index + 1) / games.length]));
  }

  function laboratoryVotes(aggregate) {
    const raw = new Map(Array.from({ length: TOTAL_NUMBERS }, (_, index) => [index + 1, 0]));
    const add = (numbers, weight) => {
      for (const number of uniqueNumbers(numbers)) raw.set(number, raw.get(number) + weight);
    };
    add(aggregate?.melhor?.dezenas, 5);
    (aggregate?.estrategias || []).slice(0, 5).forEach((strategy, index) => {
      const quality = Math.max(0.5, Number(strategy.media_acertos || 0) - 8.5);
      add(strategy.melhor_dezenas, Math.max(0.5, (5 - index) * quality));
    });
    return normalizeVoteMap(raw);
  }

  function buildEcosystemSignals(status) {
    const method = systemMethodVotes(status);
    const lab = laboratoryVotes(status?.laboratorio_acumulado);
    const weekAggregate = status?.laboratorio_semana_atual?.agregado || null;
    const week = laboratoryVotes(weekAggregate);
    return { method, lab, week };
  }

  function featureVector(history, number, ecosystem = null) {
    const f5 = frequency(history, number, 5);
    const f10 = frequency(history, number, 10);
    const f20 = frequency(history, number, 20);
    const f50 = frequency(history, number, 50);
    const delay = currentDelay(history, number);
    const avgGap = averageGap(history, number);
    const lastDraw = history[history.length - 1]?.dezenas || [];
    const methodVote = ecosystem?.method?.get(number) ?? BASE_RATE;
    const labVote = ecosystem?.lab?.get(number) ?? BASE_RATE;
    const weekVote = ecosystem?.week?.get(number) ?? BASE_RATE;

    return {
      freq5: f5 - BASE_RATE,
      freq10: f10 - BASE_RATE,
      freq20: f20 - BASE_RATE,
      freq50: f50 - BASE_RATE,
      trend: f5 - f20,
      repeat: (lastDraw.includes(number) ? 1 : 0) - BASE_RATE,
      pair: pairSupport(history, number) - BASE_RATE,
      gap: clamp((delay - avgGap) / Math.max(2, avgGap * 2), -1, 1),
      method: methodVote - BASE_RATE,
      lab: labVote - BASE_RATE,
      week: weekVote - BASE_RATE,
      delay,
      methodVote,
      labVote,
      weekVote,
      f5,
      f10,
      f20,
      f50
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

  function calibratedProbabilities(logits, target = DRAW_SIZE, minProbability = 0.18, maxProbability = 0.92) {
    let low = -12;
    let high = 12;
    const probabilitiesFor = (shift) => logits.map((logit) => clamp(sigmoid(logit + shift), minProbability, maxProbability));
    for (let iteration = 0; iteration < 100; iteration += 1) {
      const middle = (low + high) / 2;
      const sum = probabilitiesFor(middle).reduce((total, probability) => total + probability, 0);
      if (sum > target) high = middle;
      else low = middle;
    }
    return probabilitiesFor((low + high) / 2);
  }

  function predictFromHistory(draws, modelKey = 'stable', options = {}) {
    const history = normalizeDraws(draws);
    if (!history.length) throw new Error('Histórico insuficiente para previsão.');
    const model = MODELS[modelKey] || MODELS.stable;
    const ecosystem = options.ecosystem || null;
    const baseLogit = Math.log(BASE_RATE / (1 - BASE_RATE));
    const rows = [];
    const logits = [];

    for (let number = 1; number <= TOTAL_NUMBERS; number += 1) {
      const features = featureVector(history, number, ecosystem);
      let adjustment = 0;
      for (const [key, weight] of Object.entries(model.weights)) adjustment += Number(features[key] || 0) * weight;
      const logit = baseLogit + adjustment / model.temperature;
      rows.push({ number, features, logit });
      logits.push(logit);
    }

    const probabilities = calibratedProbabilities(logits);
    rows.forEach((row, index) => {
      row.probability = probabilities[index];
      row.probabilityPct = round(probabilities[index] * 100, 4);
    });
    rows.sort((a, b) => b.probability - a.probability || a.number - b.number);
    rows.forEach((row, index) => { row.rank = index + 1; });

    return {
      model: model.key,
      modelName: model.name,
      modelVersion: MODEL_VERSION,
      trainingThrough: history[history.length - 1].concurso,
      drawsUsed: history.length,
      probabilitySum: round(rows.reduce((total, row) => total + row.probability, 0), 8),
      ranking: rows,
      top15: rows.slice(0, 15).map((row) => row.number),
      top18: rows.slice(0, 18).map((row) => row.number),
      top19: rows.slice(0, 19).map((row) => row.number),
      top20: rows.slice(0, 20).map((row) => row.number),
      top21: rows.slice(0, 21).map((row) => row.number)
    };
  }

  function logLossTerm(probability, actual) {
    const p = clamp(probability, 1e-9, 1 - 1e-9);
    return -(actual * Math.log(p) + (1 - actual) * Math.log(1 - p));
  }

  function evaluatePrediction(prediction, actualNumbers) {
    const actual = new Set(uniqueNumbers(actualNumbers));
    if (actual.size !== DRAW_SIZE) throw new Error('Resultado deve conter 15 dezenas.');
    const ranking = prediction?.ranking || [];
    if (ranking.length !== TOTAL_NUMBERS) throw new Error('Previsão inválida: ranking incompleto.');
    let brier = 0;
    let logLoss = 0;
    for (const row of ranking) {
      const y = actual.has(row.number) ? 1 : 0;
      brier += (row.probability - y) ** 2;
      logLoss += logLossTerm(row.probability, y);
    }
    const hits = (size) => ranking.slice(0, size).reduce((total, row) => total + (actual.has(row.number) ? 1 : 0), 0);
    return {
      brier: round(brier / TOTAL_NUMBERS, 8),
      logLoss: round(logLoss / TOTAL_NUMBERS, 8),
      top15: hits(15),
      top18: hits(18),
      top19: hits(19),
      top20: hits(20),
      top21: hits(21)
    };
  }

  function average(items, key) {
    if (!items.length) return 0;
    return items.reduce((total, item) => total + Number(item[key] || 0), 0) / items.length;
  }

  function walkForward(draws, modelKey = 'stable', options = {}) {
    const history = normalizeDraws(draws);
    const minTraining = Math.max(8, Number(options.minTraining || 12));
    const maxTests = Math.max(1, Number(options.maxTests || 36));
    const start = Math.max(minTraining, history.length - maxTests);
    const rows = [];

    for (let targetIndex = start; targetIndex < history.length; targetIndex += 1) {
      const training = history.slice(0, targetIndex);
      const target = history[targetIndex];
      const prediction = predictFromHistory(training, modelKey);
      const metrics = evaluatePrediction(prediction, target.dezenas);
      rows.push({
        concurso: target.concurso,
        data: target.data,
        trainingThrough: prediction.trainingThrough,
        ...metrics
      });
    }

    return {
      model: modelKey,
      modelName: (MODELS[modelKey] || MODELS.stable).name,
      samples: rows.length,
      brier: round(average(rows, 'brier'), 8),
      logLoss: round(average(rows, 'logLoss'), 8),
      avgTop15: round(average(rows, 'top15'), 4),
      avgTop18: round(average(rows, 'top18'), 4),
      avgTop19: round(average(rows, 'top19'), 4),
      avgTop20: round(average(rows, 'top20'), 4),
      avgTop21: round(average(rows, 'top21'), 4),
      deltaTop21: round(average(rows, 'top21') - THEORETICAL_TOP21, 4),
      deltaBrier: round(BASELINE_BRIER - average(rows, 'brier'), 8),
      rows
    };
  }

  function modelScore(report) {
    if (!report?.samples) return -Infinity;
    return (BASELINE_BRIER - report.brier) * 120
      + (report.avgTop21 - THEORETICAL_TOP21) * 0.8
      + (report.avgTop15 - DRAW_SIZE * BASE_RATE) * 0.25
      - Math.max(0, 18 - report.samples) * 0.01;
  }

  function compareModels(draws, options = {}) {
    const stable = walkForward(draws, 'stable', options);
    const adaptive = walkForward(draws, 'adaptive', options);
    const stableScore = modelScore(stable);
    const adaptiveScore = modelScore(adaptive);
    const champion = adaptiveScore > stableScore ? adaptive : stable;
    const challenger = champion.model === 'stable' ? adaptive : stable;
    const margin = Math.abs(stableScore - adaptiveScore);
    const confidence = champion.samples >= 30 && margin >= 0.08
      ? 'moderada'
      : champion.samples >= 18 ? 'exploratória' : 'baixa';
    return {
      champion,
      challenger,
      stable,
      adaptive,
      stableScore: round(stableScore, 6),
      adaptiveScore: round(adaptiveScore, 6),
      confidence
    };
  }

  function ecosystemSummary(status) {
    const aggregate = status?.laboratorio_acumulado;
    const weekly = status?.laboratorio_semana_atual?.agregado;
    return {
      totalResultsAvailable: Number(status?.total_concursos || 0),
      recentDrawsUsed: normalizeDraws(status?.resultados_recentes).length,
      systemMethods: (status?.jogos_gerados || []).length,
      laboratoryGames: Number(aggregate?.resumo?.quantidade || aggregate?.quantidade || 0),
      laboratoryContests: (aggregate?.concursos || []).length,
      weeklyGames: Number(weekly?.resumo?.quantidade || weekly?.quantidade || 0),
      weeklyContests: (weekly?.concursos || []).length
    };
  }

  function buildForecast(status, options = {}) {
    const draws = normalizeDraws(status?.resultados_recentes);
    if (draws.length < 9) throw new Error('São necessários ao menos 9 resultados recentes.');
    const comparison = compareModels(draws, {
      minTraining: options.minTraining || 12,
      maxTests: options.maxTests || 36
    });
    const ecosystem = buildEcosystemSignals(status);
    const current = predictFromHistory(draws, comparison.champion.model, { ecosystem });
    const latestContest = draws[draws.length - 1].concurso;
    const targetContest = Number(status?.proximo_concurso || latestContest + 1);
    return {
      modelVersion: MODEL_VERSION,
      generatedAt: new Date().toISOString(),
      trainingThrough: latestContest,
      targetContest,
      champion: comparison.champion,
      challenger: comparison.challenger,
      confidence: comparison.confidence,
      ranking: current.ranking,
      probabilitySum: current.probabilitySum,
      top15: current.top15,
      top18: current.top18,
      top19: current.top19,
      top20: current.top20,
      top21: current.top21,
      ecosystem: ecosystemSummary(status),
      backtest: comparison.champion.rows
    };
  }

  function stableStringify(value) {
    if (value === null || typeof value !== 'object') return JSON.stringify(value);
    if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
    const keys = Object.keys(value).sort();
    return `{${keys.map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
  }

  function compactForecastForLedger(forecast) {
    return {
      schema: 1,
      modelVersion: forecast.modelVersion,
      generatedAt: forecast.generatedAt,
      targetContest: forecast.targetContest,
      trainingThrough: forecast.trainingThrough,
      champion: {
        model: forecast.champion.model,
        modelName: forecast.champion.modelName,
        samples: forecast.champion.samples,
        brier: forecast.champion.brier,
        avgTop21: forecast.champion.avgTop21,
        deltaTop21: forecast.champion.deltaTop21
      },
      challenger: {
        model: forecast.challenger.model,
        modelName: forecast.challenger.modelName,
        samples: forecast.challenger.samples,
        brier: forecast.challenger.brier,
        avgTop21: forecast.challenger.avgTop21
      },
      confidence: forecast.confidence,
      probabilitySum: forecast.probabilitySum,
      ecosystem: forecast.ecosystem,
      ranking: forecast.ranking.map((row) => ({
        rank: row.rank,
        number: row.number,
        probability: round(row.probability, 8)
      })),
      top15: forecast.top15,
      top18: forecast.top18,
      top19: forecast.top19,
      top20: forecast.top20,
      top21: forecast.top21,
      result: null,
      evaluation: null
    };
  }

  return {
    TOTAL_NUMBERS,
    DRAW_SIZE,
    BASE_RATE,
    THEORETICAL_TOP21,
    BASELINE_BRIER,
    MODEL_VERSION,
    MODELS,
    normalizeDraws,
    buildEcosystemSignals,
    predictFromHistory,
    evaluatePrediction,
    walkForward,
    compareModels,
    buildForecast,
    stableStringify,
    compactForecastForLedger,
    pad,
    round
  };
});
