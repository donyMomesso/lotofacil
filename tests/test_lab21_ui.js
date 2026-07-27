'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, '..', 'laboratorio_21.html'), 'utf8');

assert.match(html, /id="copyBtn"/, 'O botão de cópia deve existir.');
assert.match(html, /function copyTextCompat\(text\)/, 'A cópia compatível deve existir.');
assert.match(html, /navigator\.clipboard/, 'Deve tentar a API moderna da área de transferência.');
assert.match(html, /document\.execCommand\('copy'\)/, 'Deve ter fallback para ambientes sem Clipboard API.');
assert.match(html, /id="manualCopy"/, 'Deve oferecer cópia manual quando o navegador bloquear a automática.');
assert.match(html, /lastOptimizedGames\.join\('\\n'\)/, 'Deve copiar a carteira completa em linhas separadas.');

console.log('Teste de interface do Laboratório 21 concluído com sucesso.');
