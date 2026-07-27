import assert from 'node:assert/strict';
import fs from 'node:fs';

const worker = fs.readFileSync(new URL('../worker_learning.js', import.meta.url), 'utf8');
const governance = fs.readFileSync(new URL('../learning_governance.mjs', import.meta.url), 'utf8');
const page = fs.readFileSync(new URL('../aprendizado.html', import.meta.url), 'utf8');
const migration2 = fs.readFileSync(new URL('../migrations/0002_aprendizado_historico.sql', import.meta.url), 'utf8');
const migration3 = fs.readFileSync(new URL('../migrations/0003_aprendizado_robustez.sql', import.meta.url), 'utf8');
const migration4 = fs.readFileSync(new URL('../migrations/0004_champion_challenger.sql', import.meta.url), 'utf8');

[
  'historical_evaluation_only',
  'trainingThrough >= target.concurso',
  'UNIQUE(concurso, modelo_chave, versao_modelo)',
  '/api/aprendizado/historico',
  'bootstrapMeanCI',
  'permutationTop21Test',
  'detectDrift',
  'integritySummary',
  'aprendizado_resumos',
  'aprendizado_campeoes',
  'aprendizado_decisoes',
  'evaluateChampionChallenger',
  'ultima_avaliacao_concurso'
].forEach((marker) => assert(worker.includes(marker), `marcador ausente no worker: ${marker}`));

[
  'champion-governance-v1.0.0',
  'benjaminiHochberg',
  'compareChampionChallenger',
  'promotionDecision',
  'MIN_PAIRED_SAMPLES',
  'MIN_CONTESTS_BETWEEN_PROMOTIONS'
].forEach((marker) => assert(governance.includes(marker), `marcador ausente na governança: ${marker}`));

[
  'Champion × Challenger',
  'Benjamini–Hochberg',
  'Decisão automática controlada',
  'Comparação por janelas',
  'Histórico de decisões',
  'Integridade do arquivo',
  "fetch(`/api/aprendizado/historico"
].forEach((marker) => assert(page.includes(marker), `marcador ausente na página: ${marker}`));

assert.doesNotMatch(page, /Copiar base|Abrir Laboratório 21|concurso-alvo|ranking probabilístico/i);
assert.doesNotMatch(worker, /proximo_concurso.*ranking/i);
assert.match(migration2, /aprendizado_historico/);
assert.match(migration3, /aprendizado_resumos/);
assert.match(migration4, /aprendizado_campeoes/);
assert.match(migration4, /aprendizado_decisoes/);
assert.match(migration4, /UNIQUE\(versao_modelo, versao_governanca, concurso_ate, campeao_atual, desafiante\)/);

console.log('OK: Worker, governança, D1 e painel Champion Challenger sem controles futuros.');
