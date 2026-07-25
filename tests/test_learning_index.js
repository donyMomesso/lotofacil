const assert = require('assert');
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
assert(html.includes('href="aprendizado.html"'));
assert(html.includes('Avaliação Histórica'));
assert(html.includes('D1'));
assert(!html.includes('Livro de Previsoes com hash'));
console.log('OK index: acesso à avaliação histórica presente.');
