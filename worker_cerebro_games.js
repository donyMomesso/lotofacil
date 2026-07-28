/**
 * Consumo do checkpoint operacional do Cérebro Python.
 * Grava provenance no D1 para provar origem/versão/hash de cada jogo do sistema.
 */

function dezenasTexto(dezenas) {
  return dezenas.map((d) => String(d).padStart(2, '0')).join('-');
}

function scoreSet(dezenas) {
  const soma = dezenas.reduce((t, d) => t + d, 0);
  const pares = dezenas.filter((d) => d % 2 === 0).length;
  return { soma, pares, impares: dezenas.length - pares };
}

/**
 * Garante colunas de provenance (idempotente se migration ainda não rodou).
 */
export async function ensureJogosSistemaProvenance(env) {
  const alters = [
    'ALTER TABLE jogos_sistema ADD COLUMN origem TEXT',
    'ALTER TABLE jogos_sistema ADD COLUMN cerebro_version TEXT',
    'ALTER TABLE jogos_sistema ADD COLUMN checkpoint_hash TEXT',
    'ALTER TABLE jogos_sistema ADD COLUMN audit_brain_version TEXT',
    'ALTER TABLE jogos_sistema ADD COLUMN source_of_truth TEXT',
    'ALTER TABLE jogos_sistema ADD COLUMN checkpoint_generated_at TEXT'
  ];
  for (const sql of alters) {
    try {
      await env.DB.prepare(sql).run();
    } catch {
      // já existe
    }
  }
  try {
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS checkpoint_ingest (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concurso INTEGER NOT NULL,
        origem TEXT NOT NULL,
        cerebro_version TEXT,
        checkpoint_hash TEXT,
        audit_brain_version TEXT,
        source_of_truth TEXT,
        checkpoint_generated_at TEXT,
        metodos_json TEXT,
        jogos_count INTEGER NOT NULL DEFAULT 0,
        ingestido_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
      )
    `).run();
  } catch (err) {
    console.error('checkpoint_ingest', err);
  }
}

/**
 * @param {any} env Cloudflare env com ASSETS + DB
 * @param {number} concurso concurso alvo
 * @returns {Promise<null | Array<object>>}
 */
export async function loadGamesFromCerebroCheckpoint(env, concurso) {
  try {
    const response = await env.ASSETS.fetch(
      new Request('https://assets.local/motor_python_v4/checkpoints/operacional.json')
    );
    if (!response.ok) return null;
    const ck = await response.json();
    if (!ck || !ck.ok || !ck.jogos_estudo) return null;
    if (Number(ck.concurso_alvo) !== Number(concurso)) return null;

    const meta = {
      origem: 'cerebro_python',
      cerebro_version: ck.cerebro_version || null,
      checkpoint_hash: ck.checkpoint_hash || null,
      audit_brain_version: ck.audit_brain_version || null,
      source_of_truth: ck.source_of_truth || 'python',
      checkpoint_generated_at: ck.generated_at || null
    };

    const games = [];
    for (const [metodo, info] of Object.entries(ck.jogos_estudo)) {
      const dezenas = Array.isArray(info)
        ? info.map(Number)
        : (info.dezenas || []).map(Number);
      if (dezenas.length !== 15) continue;
      games.push({
        metodo,
        dezenas: dezenas.slice().sort((a, b) => a - b),
        ...meta
      });
    }
    return games.length ? games : null;
  } catch (err) {
    console.error('checkpoint operacional indisponível', err);
    return null;
  }
}

/**
 * Persiste jogos do sistema COM provenance.
 */
export async function persistSystemGames(env, concurso, games) {
  await ensureJogosSistemaProvenance(env);

  for (const game of games) {
    const stats = scoreSet(game.dezenas);
    const origem = game.origem || 'worker_js';
    const cerebroVersion = game.cerebro_version || null;
    const checkpointHash = game.checkpoint_hash || null;
    const auditBrain = game.audit_brain_version || null;
    const sourceOfTruth = game.source_of_truth || (origem === 'cerebro_python' ? 'python' : 'worker_js');
    const generatedAt = game.checkpoint_generated_at || null;

    await env.DB.prepare(`
      INSERT INTO jogos_sistema (
        concurso, metodo, dezenas, dezenas_texto, soma, pares, impares,
        origem, cerebro_version, checkpoint_hash,
        audit_brain_version, source_of_truth, checkpoint_generated_at
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(concurso, metodo) DO UPDATE SET
        dezenas = excluded.dezenas,
        dezenas_texto = excluded.dezenas_texto,
        soma = excluded.soma,
        pares = excluded.pares,
        impares = excluded.impares,
        origem = excluded.origem,
        cerebro_version = excluded.cerebro_version,
        checkpoint_hash = excluded.checkpoint_hash,
        audit_brain_version = excluded.audit_brain_version,
        source_of_truth = excluded.source_of_truth,
        checkpoint_generated_at = excluded.checkpoint_generated_at,
        criado_em = CURRENT_TIMESTAMP
    `).bind(
      concurso,
      game.metodo,
      JSON.stringify(game.dezenas),
      dezenasTexto(game.dezenas),
      stats.soma,
      stats.pares,
      stats.impares,
      origem,
      cerebroVersion,
      checkpointHash,
      auditBrain,
      sourceOfTruth,
      generatedAt
    ).run();
  }

  const first = games[0] || {};
  try {
    await env.DB.prepare(`
      INSERT INTO checkpoint_ingest (
        concurso, origem, cerebro_version, checkpoint_hash,
        audit_brain_version, source_of_truth, checkpoint_generated_at,
        metodos_json, jogos_count
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      concurso,
      first.origem || 'worker_js',
      first.cerebro_version || null,
      first.checkpoint_hash || null,
      first.audit_brain_version || null,
      first.source_of_truth || null,
      first.checkpoint_generated_at || null,
      JSON.stringify(games.map((g) => g.metodo)),
      games.length
    ).run();
  } catch (err) {
    console.error('checkpoint_ingest insert', err);
  }

  return games;
}

export function tagWorkerJsGames(games, extra = {}) {
  return (games || []).map((g) => ({
    ...g,
    origem: 'worker_js',
    source_of_truth: 'worker_js',
    cerebro_version: null,
    checkpoint_hash: null,
    audit_brain_version: null,
    checkpoint_generated_at: null,
    ...extra
  }));
}
