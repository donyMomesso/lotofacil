(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.Lab21Core = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const BASE_SIZE = 21;
  const GAME_SIZE = 15;
  const TOTAL_SCENARIOS = 54264;
  const PRIMES = new Set([2, 3, 5, 7, 11, 13, 17, 19, 23]);
  const MOLDURA = new Set([1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25]);

  function validateBase(base) {
    const values = [...base].map(Number).sort((a, b) => a - b);
    if (values.length !== BASE_SIZE) throw new Error('A base deve conter exatamente 21 dezenas.');
    if (new Set(values).size !== BASE_SIZE) throw new Error('A base não pode ter dezenas repetidas.');
    if (values.some(n => !Number.isInteger(n) || n < 1 || n > 25)) {
      throw new Error('Use somente dezenas inteiras entre 01 e 25.');
    }
    return values;
  }

  function combinationCount(n, k) {
    if (k < 0 || k > n) return 0;
    let result = 1;
    for (let i = 1; i <= k; i++) result = (result * (n - k + i)) / i;
    return Math.round(result);
  }

  function bitCount32(value) {
    value >>>= 0;
    value = value - ((value >>> 1) & 0x55555555);
    value = (value & 0x33333333) + ((value >>> 2) & 0x33333333);
    return (((value + (value >>> 4)) & 0x0f0f0f0f) * 0x01010101) >>> 24;
  }

  function generateAllMasks() {
    const masks = [];
    function visit(start, depth, mask) {
      if (depth === GAME_SIZE) {
        masks.push(mask >>> 0);
        return;
      }
      const remaining = GAME_SIZE - depth;
      for (let pos = start; pos <= BASE_SIZE - remaining; pos++) {
        visit(pos + 1, depth + 1, (mask | (1 << pos)) >>> 0);
      }
    }
    visit(0, 0, 0);
    if (masks.length !== TOTAL_SCENARIOS) {
      throw new Error(`Falha combinatória: esperado ${TOTAL_SCENARIOS}, obtido ${masks.length}.`);
    }
    return masks;
  }

  function maskToNumbers(mask, base) {
    const values = [];
    for (let i = 0; i < BASE_SIZE; i++) {
      if ((mask & (1 << i)) !== 0) values.push(base[i]);
    }
    return values;
  }

  function gameScore(mask, base) {
    const game = maskToNumbers(mask, base);
    const sum = game.reduce((a, b) => a + b, 0);
    const even = game.filter(n => n % 2 === 0).length;
    const primes = game.filter(n => PRIMES.has(n)).length;
    const frame = game.filter(n => MOLDURA.has(n)).length;
    const rows = new Set(game.map(n => Math.floor((n - 1) / 5))).size;

    let score = 0;
    score += Math.max(0, 30 - Math.abs(sum - 195) * 1.2);
    score += Math.max(0, 16 - Math.abs(even - 7.5) * 4);
    score += Math.max(0, 12 - Math.abs(primes - 5.5) * 3);
    score += Math.max(0, 10 - Math.abs(frame - 9.5) * 2);
    if (rows >= 4) score += 8;
    return score;
  }

  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0;
      a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function sampleUniqueIndices(total, count, rng, excluded) {
    const result = [];
    const seen = new Set(excluded || []);
    while (result.length < count && seen.size < total) {
      const idx = Math.floor(rng() * total);
      if (seen.has(idx)) continue;
      seen.add(idx);
      result.push(idx);
    }
    return result;
  }

  function buildCandidatePool(masks, base, quantity, seed) {
    const poolSize = quantity <= 60 ? 2600 : quantity <= 120 ? 4200 : 6500;
    const topCount = Math.floor(poolSize * 0.42);
    const ranked = masks.map((mask, index) => ({ index, score: gameScore(mask, base) }));
    ranked.sort((a, b) => b.score - a.score || a.index - b.index);
    const selected = ranked.slice(0, topCount).map(x => x.index);
    const rng = mulberry32(seed ^ 0x9e3779b9);
    selected.push(...sampleUniqueIndices(masks.length, poolSize - selected.length, rng, selected));
    return selected;
  }

  function buildScenarioSample(masks, seed, size) {
    const rng = mulberry32(seed ^ 0x85ebca6b);
    const indices = sampleUniqueIndices(masks.length, Math.min(size, masks.length), rng);
    return indices.map(i => masks[i]);
  }

  async function generateOptimizedPortfolio(baseInput, quantity, options) {
    const base = validateBase(baseInput);
    const qtd = Math.max(1, Math.min(Number(quantity) || 120, 300));
    const opts = options || {};
    const seed = Number.isInteger(opts.seed) ? opts.seed : 21;
    const onProgress = typeof opts.onProgress === 'function' ? opts.onProgress : function () {};
    const yieldEvery = Math.max(5, opts.yieldEvery || 15);
    const masks = opts.masks || generateAllMasks();
    const sampleSize = qtd <= 60 ? 1536 : 2048;
    const scenarioSample = buildScenarioSample(masks, seed, sampleSize);
    const candidates = buildCandidatePool(masks, base, qtd, seed);
    const candidateScores = new Map(candidates.map(i => [i, gameScore(masks[i], base)]));

    let first = candidates[0];
    for (const idx of candidates) {
      if (candidateScores.get(idx) > candidateScores.get(first)) first = idx;
    }

    const selected = [first];
    const selectedSet = new Set(selected);
    const bestSample = new Uint8Array(scenarioSample.length);
    const maxOverlap = new Uint8Array(masks.length);

    function applySelected(mask) {
      for (let i = 0; i < scenarioSample.length; i++) {
        const hit = bitCount32(mask & scenarioSample[i]);
        if (hit > bestSample[i]) bestSample[i] = hit;
      }
      for (const idx of candidates) {
        if (selectedSet.has(idx)) continue;
        const overlap = bitCount32(mask & masks[idx]);
        if (overlap > maxOverlap[idx]) maxOverlap[idx] = overlap;
      }
    }
    applySelected(masks[first]);

    while (selected.length < qtd) {
      const available = candidates.filter(i => !selectedSet.has(i));
      available.sort((a, b) => {
        const d = maxOverlap[a] - maxOverlap[b];
        if (d) return d;
        return (candidateScores.get(b) - candidateScores.get(a)) || (a - b);
      });
      const shortlist = available.slice(0, qtd <= 60 ? 110 : 90);
      let bestIndex = shortlist[0];
      let bestKey = null;

      for (const idx of shortlist) {
        const mask = masks[idx];
        let gain14 = 0;
        let gain13 = 0;
        let gain12 = 0;
        let improvement = 0;
        for (let i = 0; i < scenarioSample.length; i++) {
          const current = bestSample[i];
          const hit = bitCount32(mask & scenarioSample[i]);
          if (hit <= current) continue;
          improvement += hit - current;
          if (current < 14 && hit >= 14) gain14++;
          if (current < 13 && hit >= 13) gain13++;
          if (current < 12 && hit >= 12) gain12++;
        }
        const key = [gain14, gain13, gain12, improvement, -maxOverlap[idx], candidateScores.get(idx), -idx];
        if (!bestKey || compareKeys(key, bestKey) > 0) {
          bestKey = key;
          bestIndex = idx;
        }
      }

      selected.push(bestIndex);
      selectedSet.add(bestIndex);
      applySelected(masks[bestIndex]);
      onProgress({ phase: 'optimize', current: selected.length, total: qtd });
      if (selected.length % yieldEvery === 0) await new Promise(resolve => setTimeout(resolve, 0));
    }

    return { base, masks, selectedMasks: selected.map(i => masks[i]), selectedIndices: selected };
  }

  function compareKeys(a, b) {
    for (let i = 0; i < a.length; i++) {
      if (a[i] > b[i]) return 1;
      if (a[i] < b[i]) return -1;
    }
    return 0;
  }

  function generateRandomPortfolio(masks, quantity, seed) {
    const rng = mulberry32((seed || 21) ^ 0xc2b2ae35);
    return sampleUniqueIndices(masks.length, quantity, rng).map(i => masks[i]);
  }

  async function evaluatePortfolio(masks, portfolio, options) {
    if (!portfolio || !portfolio.length) throw new Error('A carteira precisa ter ao menos uma combinação.');
    const opts = options || {};
    const onProgress = typeof opts.onProgress === 'function' ? opts.onProgress : function () {};
    const distribution = {};
    let minimum = GAME_SIZE;

    for (let i = 0; i < masks.length; i++) {
      const scenario = masks[i];
      let best = 0;
      for (let j = 0; j < portfolio.length; j++) {
        const hit = bitCount32(scenario & portfolio[j]);
        if (hit > best) best = hit;
        if (best === GAME_SIZE) break;
      }
      distribution[best] = (distribution[best] || 0) + 1;
      if (best < minimum) minimum = best;
      if (i > 0 && i % 4096 === 0) {
        onProgress({ phase: 'validate', current: i, total: masks.length });
        await new Promise(resolve => setTimeout(resolve, 0));
      }
    }

    function countAtLeast(target) {
      return Object.entries(distribution).reduce((sum, [hit, count]) => sum + (Number(hit) >= target ? count : 0), 0);
    }
    function pct(count) { return Number((count * 100 / masks.length).toFixed(4)); }

    const c15 = countAtLeast(15);
    const c14 = countAtLeast(14);
    const c13 = countAtLeast(13);
    const c12 = countAtLeast(12);
    onProgress({ phase: 'validate', current: masks.length, total: masks.length });
    return {
      scenarios: masks.length,
      games: portfolio.length,
      minimum,
      distribution,
      count15: c15,
      count14Plus: c14,
      count13Plus: c13,
      count12Plus: c12,
      pct15: pct(c15),
      pct14Plus: pct(c14),
      pct13Plus: pct(c13),
      pct12Plus: pct(c12),
      condition: 'As 15 dezenas do cenário precisam estar contidas na base de 21 dezenas.'
    };
  }

  function formatGame(mask, base) {
    return maskToNumbers(mask, base).map(n => String(n).padStart(2, '0')).join(' ');
  }

  return {
    BASE_SIZE,
    GAME_SIZE,
    TOTAL_SCENARIOS,
    validateBase,
    combinationCount,
    bitCount32,
    generateAllMasks,
    maskToNumbers,
    gameScore,
    generateOptimizedPortfolio,
    generateRandomPortfolio,
    evaluatePortfolio,
    formatGame,
    mulberry32
  };
});
