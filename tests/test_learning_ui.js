const assert = require('assert');
const fs = require('fs');
const html = fs.readFileSync('aprendizado.html', 'utf8');

[
  'Motor de Aprendizado',
  'Livro de Previsões',
  "fetch('/api/sistema/status'",
  'core.buildForecast',
  'core.compactForecastForLedger',
  'crypto.subtle.digest',
  'lotofacil_prediction_ledger_v1',
  'evaluatePendingLedger',
  'laboratorio_21.html?base=',
  'Exportar livro JSON'
].forEach((marker) => assert(html.includes(marker), `marcador ausente: ${marker}`));

assert(html.toLowerCase().includes('previsão probabilística experimental'));
assert(html.includes('Referência teórica: 12,60'));
console.log('OK aprendizado.html: API, walk-forward, congelamento, hash e exportação presentes.');
