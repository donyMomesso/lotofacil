import assert from 'node:assert/strict';
import fs from 'node:fs';

const worker = fs.readFileSync(new URL('../worker_learning.js', import.meta.url), 'utf8');
const page = fs.readFileSync(new URL('../aprendizado.html', import.meta.url), 'utf8');
const migration = fs.readFileSync(new URL('../migrations/0002_aprendizado_historico.sql', import.meta.url), 'utf8');

assert.match(worker, /historical_evaluation_only/);
assert.match(worker, /trainingThrough >= target\.concurso/);
assert.match(worker, /UNIQUE\(concurso, modelo_chave, versao_modelo\)/);
assert.match(worker, /\/api\/aprendizado\/historico/);
assert.doesNotMatch(worker, /proximo_concurso.*ranking/i);
assert.doesNotMatch(page, /Copiar base|Abrir Laboratório 21|próximo concurso/i);
assert.match(page, /Avaliação histórica/);
assert.match(page, /Brier/);
assert.match(migration, /aprendizado_historico/);

console.log('Servidor e painel histórico: testes concluídos com sucesso.');
