const assert = require('assert');
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
assert(html.includes('href="aprendizado.html"'));
assert(html.includes('Robustez Histórica'));
assert(html.includes('intervalos de confiança'));
console.log('OK index: acesso à robustez histórica presente.');
