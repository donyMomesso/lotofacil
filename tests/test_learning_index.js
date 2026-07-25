const assert = require('assert');
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
assert(html.includes('href="aprendizado.html"'));
assert(html.includes('Champion × Challenger'));
assert(html.includes('Benjamini-Hochberg'));
assert(html.includes('governanca estatistica'));
console.log('OK index: acesso à governança Champion Challenger presente.');
