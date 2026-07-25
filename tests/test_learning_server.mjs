import assert from 'node:assert/strict';
import fs from 'node:fs';

const worker = fs.readFileSync(new URL('../worker_learning.js', import.meta.url), 'utf8');
const page = fs.readFileSync(new URL('../aprendizado.html', import.meta.url), 'utf8');
const migration2 = fs.readFileSync(new URL('../migrations/0002_aprendizado_historico.sql', import.meta.url), 'utf8');
const migration3 = fs.readFileSync(new URL('../migrations/0003_aprendizado_robustez.sql', import.meta.url), 'utf8');

[
  'historical_evaluation_only',
  'trainingThrough >= target.concurso',
  'UNIQUE(concurso, modelo_chave, versao_modelo)',
  '/api/aprendizado/historico',
  'bootstrapMeanCI',
  'permutationTop21Test',
  'detectDrift',
  'integritySummary',
  'aprendizado_resumos'
].forEach((marker) => assert(worker.includes(marker), `marcador ausente no worker: ${marker}`));

[
  'Robustez histórica',
  'IC de 95%',
  'Valor-p',
  'Janelas móveis 8 / 16 / 24',
  'Integridade do arquivo',
  'Registro de versões',
  "fetch(`/api/aprendizado/historico"
].forEach((marker) => assert(page.includes(marker), `marcador ausente na página: ${marker}`));

assert.doesNotMatch(page, /Copiar base|Abrir Laboratório 21|concurso-alvo|ranking probabilístico/i);
assert.doesNotMatch(worker, /proximo_concurso.*ranking/i);
assert.match(migration2, /aprendizado_historico/);
assert.match(migration3, /aprendizado_resumos/);
assert.match(migration3, /UNIQUE\(modelo_chave, versao_modelo, amostras, ultimo_concurso\)/);

console.log('OK: Worker, D1 e painel robusto sem controles de previsão futura.');
