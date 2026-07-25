const assert = require('assert');
const core = require('../lab21_core.js');

(async () => {
  assert.strictEqual(core.combinationCount(21, 15), 54264);
  const base = Array.from({length:21}, (_,i)=>i+1);
  assert.deepStrictEqual(core.validateBase(base), base);
  assert.throws(() => core.validateBase(base.slice(0,20)));
  const masks = core.generateAllMasks();
  assert.strictEqual(masks.length, 54264);
  assert.strictEqual(new Set(masks).size, 54264);

  const portfolio = await core.generateOptimizedPortfolio(base, 8, {seed:123, masks, yieldEvery:1000});
  assert.strictEqual(portfolio.selectedMasks.length, 8);
  assert.strictEqual(new Set(portfolio.selectedMasks).size, 8);

  const one = await core.evaluatePortfolio(masks, [masks[0]]);
  assert.strictEqual(one.minimum, 9);
  assert.strictEqual(one.count15, 1);

  const full = await core.evaluatePortfolio(masks, masks);
  assert.strictEqual(full.minimum, 15);
  assert.strictEqual(full.pct15, 100);
  console.log('lab21_core: todos os testes passaram');
})().catch(err => { console.error(err); process.exit(1); });
