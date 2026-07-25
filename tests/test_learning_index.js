const assert = require('assert');
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
assert(html.includes('href="aprendizado.html"'));
assert(html.includes('Motor de Aprendizado'));
console.log('OK index: acesso ao Motor de Aprendizado presente.');
