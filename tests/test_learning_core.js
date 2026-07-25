const assert = require('assert');
const core = require('../learning_core.js');

function makeDraw(contest, shift) {
  const nums = [];
  for (let i = 0; i < 15; i += 1) nums.push(((i * 7 + shift * 3) % 25) + 1);
  const unique = [...new Set(nums)];
  let n = 1;
  while (unique.length < 15) {
    if (!unique.includes(n)) unique.push(n);
    n += 1;
  }
  return { concurso: contest, data: `${String((contest % 28) + 1).padStart(2,'0')}/07/2026`, dezenas: unique.sort((a,b)=>a-b) };
}

const draws = Array.from({ length: 55 }, (_, i) => makeDraw(3600 + i, i + 1));
const prediction = core.predictFromHistory(draws.slice(0, 40), 'stable');
assert.strictEqual(prediction.ranking.length, 25);
assert.strictEqual(prediction.top21.length, 21);
assert.strictEqual(new Set(prediction.top21).size, 21);
assert(Math.abs(prediction.probabilitySum - 15) < 1e-6, `soma=${prediction.probabilitySum}`);
assert(prediction.ranking.every((row, idx, arr) => idx === 0 || arr[idx - 1].probability >= row.probability));

const evaluation = core.evaluatePrediction(prediction, draws[40].dezenas);
assert(evaluation.brier >= 0 && evaluation.brier <= 1);
assert(evaluation.top15 >= 5 && evaluation.top15 <= 15);
assert(evaluation.top21 >= evaluation.top20);

const wf = core.walkForward(draws, 'stable', { minTraining: 12, maxTests: 30 });
assert.strictEqual(wf.samples, 30);
assert.strictEqual(wf.rows[0].trainingThrough, draws[24].concurso);
assert.strictEqual(wf.rows[0].concurso, draws[25].concurso);
assert(wf.rows.every((row) => row.trainingThrough < row.concurso), 'walk-forward vazou o concurso alvo');

const status = {
  total_concursos: 3655,
  proximo_concurso: 3655,
  resultados_recentes: draws,
  jogos_gerados: Array.from({ length: 9 }, (_, i) => ({ metodo: `M${i + 1}`, dezenas: makeDraw(0, i + 4).dezenas })),
  laboratorio_acumulado: {
    concursos: [3648, 3649],
    resumo: { quantidade: 40000 },
    melhor: { dezenas: draws[54].dezenas },
    estrategias: [
      { media_acertos: 9.7, melhor_dezenas: draws[53].dezenas },
      { media_acertos: 9.5, melhor_dezenas: draws[52].dezenas }
    ]
  },
  laboratorio_semana_atual: {
    agregado: {
      concursos: [3653, 3654],
      resumo: { quantidade: 40000 },
      melhor: { dezenas: draws[51].dezenas },
      estrategias: []
    }
  }
};
const forecast = core.buildForecast(status, { maxTests: 30 });
assert.strictEqual(forecast.targetContest, 3655);
assert.strictEqual(forecast.trainingThrough, draws[54].concurso);
assert.strictEqual(forecast.top21.length, 21);
assert.strictEqual(forecast.ecosystem.laboratoryGames, 40000);
assert(['stable', 'adaptive'].includes(forecast.champion.model));

const ledger = core.compactForecastForLedger(forecast);
assert.strictEqual(ledger.ranking.length, 25);
assert.strictEqual(ledger.result, null);
assert(core.stableStringify(ledger).includes('targetContest'));

const deterministicA = core.predictFromHistory(draws.slice(0, 40), 'adaptive');
const deterministicB = core.predictFromHistory(draws.slice(0, 40), 'adaptive');
assert.deepStrictEqual(deterministicA.top21, deterministicB.top21);
assert.deepStrictEqual(
  deterministicA.ranking.map(r => r.probability),
  deterministicB.ranking.map(r => r.probability)
);

console.log('OK learning_core: previsão calibrada, walk-forward sem vazamento e livro compacto.');
