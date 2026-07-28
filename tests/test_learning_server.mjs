import assert from 'node:assert/strict';
import fs from 'node:fs';

const bridge = fs.readFileSync(new URL('../worker_python_bridge.js', import.meta.url), 'utf8');
const page = fs.readFileSync(new URL('../aprendizado.html', import.meta.url), 'utf8');
const wrangler = fs.readFileSync(new URL('../wrangler.jsonc', import.meta.url), 'utf8');
const auditCore = fs.readFileSync(new URL('../motor_python_v4/audit_core.py', import.meta.url), 'utf8');

[
  "import baseWorker from './worker.js'",
  '/api/aprendizado/exportar-resultados',
  '/api/aprendizado/checkpoint-python',
  'historical_education_only',
  'motor_python_v4/checkpoints/latest.json'
].forEach((marker) => assert(bridge.includes(marker), `marcador ausente na ponte: ${marker}`));

assert.doesNotMatch(bridge, /worker_learning\.js/);
assert.match(wrangler, /"main"\s*:\s*"worker_python_bridge\.js"/);

[
  'Cérebro Python',
  'bloco completo de 5 concursos',
  'Referências neutras',
  'Histórico de checkpoints',
  'Integridade',
  "fetch(`/api/aprendizado/checkpoint-python"
].forEach((marker) => assert(page.includes(marker), `marcador ausente na página: ${marker}`));

assert.doesNotMatch(page, /Champion|Challenger|promover|recomendação futura|Copiar base|ranking probabilístico/i);

[
  'CHECKPOINT_SIZE = 5',
  'purpose": "historical_education_only"',
  'source_of_truth": "python"',
  'temporal_violations',
  'assert_safe_report'
].forEach((marker) => assert(auditCore.includes(marker), `marcador ausente no núcleo Python: ${marker}`));

assert.doesNotMatch(auditCore, /historical_champion|best_model|winner/);

console.log('OK: cérebro Python histórico, ponte D1 e painel sem seleção futura.');
