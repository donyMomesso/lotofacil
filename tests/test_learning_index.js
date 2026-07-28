const assert = require('assert');
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
assert(html.includes('href="aprendizado.html"'));
assert(html.includes('Cérebro Python'));
assert(html.includes('checkpoints de 5 concursos'));
assert(html.includes('auditoria retrospectiva'));
assert(!/Champion|Challenger|Benjamini-Hochberg|promocao controlada/i.test(html));
console.log('OK index: acesso ao cérebro Python histórico presente.');
