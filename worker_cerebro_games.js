/**
 * Checkpoint operacional do Cérebro Python + provenance no D1.
 * Política: falha explícita. Sem hash/versão/concurso alinhado → NÃO grava.
 */

import {
  ensureSugestaoSchema,
  computeMethodScores,
  buildSugestaoDoDia,
  saveSugestaoSnapshot,
  extractLabHint
} from './worker_sugestao_dia.js';

function dezenasTexto(dezenas) {
  return dezenas.map((d) => String(d).padStart(2, '0')).join('-');
}

function scoreSet(dezenas) {
  const soma = dezenas.reduce((t, d) => t + d, 0);
  const pares = dezenas.filter((d) => d % 2 === 0).length;
  return { soma, pares, impares: dezenas.length - pares };
}

const CHECKPOINT_CANDIDATE_PATHS = [
  '/motor_python_v4/checkpoints/operacional.json',
  '/dados/checkpoint_cerebro.json',
  '/checkpoints/operacional.json',
  '/operacional.json'
];

async function fetchCheckpointAsset(env) {
  const attempts = [];
  for (const path of CHECKPOINT_CANDIDATE_PATHS) {
    try {
      const response = await env.ASSETS.fetch(
        new Request(new URL(path, 'https://assets.local').toString())
      );
      attempts.push({ path, status: response.status });
      if (response.ok) {
        return { response, path, attempts };
      }
    } catch (err) {
      attempts.push({ path, status: 0, error: String(err.message || err) });
    }
  }
  return { response: null, path: null, attempts };
}

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
    try { await env.DB.prepare(sql).run(); } catch { /* ok */ }
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
  try { await ensureSugestaoSchema(env); } catch (e) { console.error(e); }
}

/**
 * Inspeciona o checkpoint operacional sem gravar.
 * status: active | missing | invalid | concurso_mismatch | incomplete
 */
export async function inspectCerebroCheckpoint(env, concursoEsperado) {
  const base = {
    status: 'missing',
    blocked: true,
    concurso_esperado: Number(concursoEsperado),
    message: 'Checkpoint operacional ausente.'
  };
  try {
    const { response, path, attempts } = await fetchCheckpointAsset(env);
    if (!response || !response.ok) {
      return {
        ...base,
        http_status: response?.status || 404,
        message: 'Asset operacional.json não encontrado via ASSETS.',
        attempts
      };
    }
    let ck;
    try {
      ck = await response.json();
    } catch {
      return { ...base, status: 'invalid', message: 'operacional.json não é JSON válido.', path };
    }
    if (!ck || ck.ok !== true) {
      return { ...base, status: 'invalid', message: 'Checkpoint com ok=false ou vazio.', path };
    }
    if (!ck.checkpoint_hash || !String(ck.checkpoint_hash).trim()) {
      return {
        ...base,
        status: 'incomplete',
        message: 'Checkpoint sem checkpoint_hash — gravação bloqueada.',
        cerebro_version: ck.cerebro_version || null,
        concurso_alvo: ck.concurso_alvo ?? null,
        path
      };
    }
    if (!ck.cerebro_version) {
      return {
        ...base,
        status: 'incomplete',
        message: 'Checkpoint sem cerebro_version — gravação bloqueada.',
        checkpoint_hash: ck.checkpoint_hash,
        path
      };
    }
    if (!ck.jogos_estudo || typeof ck.jogos_estudo !== 'object') {
      return { ...base, status: 'invalid', message: 'Checkpoint sem jogos_estudo.', path };
    }
    const alvo = Number(ck.concurso_alvo);
    if (Number(concursoEsperado) && alvo !== Number(concursoEsperado)) {
      return {
        status: 'concurso_mismatch',
        blocked: true,
        concurso_esperado: Number(concursoEsperado),
        concurso_alvo: alvo,
        cerebro_version: ck.cerebro_version,
        checkpoint_hash: ck.checkpoint_hash,
        path,
        message: `Checkpoint é para concurso ${alvo}, esperado ${concursoEsperado}. Atualize o histórico e reexporte o operacional.json.`
      };
    }

    const games = [];
    for (const [metodo, info] of Object.entries(ck.jogos_estudo)) {
      const dezenas = Array.isArray(info)
        ? info.map(Number)
        : (info.dezenas || []).map(Number);
      if (dezenas.length !== 15) continue;
      if (new Set(dezenas).size !== 15) continue;
      if (dezenas.some((d) => d < 1 || d > 25)) continue;
      games.push({
        metodo,
        dezenas: dezenas.slice().sort((a, b) => a - b),
        origem: 'cerebro_python',
        cerebro_version: ck.cerebro_version,
        checkpoint_hash: ck.checkpoint_hash,
        audit_brain_version: ck.audit_brain_version || null,
        source_of_truth: ck.source_of_truth || 'python',
        checkpoint_generated_at: ck.generated_at || null
      });
    }
    if (!games.length) {
      return {
        status: 'invalid',
        blocked: true,
        concurso_alvo: alvo,
        cerebro_version: ck.cerebro_version,
        checkpoint_hash: ck.checkpoint_hash,
        path,
        message: 'Checkpoint sem nenhum jogo de 15 dezenas válido.'
      };
    }

    return {
      status: 'active',
      blocked: false,
      concurso_esperado: Number(concursoEsperado),
      concurso_alvo: alvo,
      cerebro_version: ck.cerebro_version,
      checkpoint_hash: ck.checkpoint_hash,
      audit_brain_version: ck.audit_brain_version || null,
      source_of_truth: ck.source_of_truth || 'python',
      generated_at: ck.generated_at || null,
      jogos: games.length,
      metodos: games.map((g) => g.metodo),
      games,
      path,
      message: 'Checkpoint Python válido e alinhado ao concurso.'
    };
  } catch (err) {
    return {
      status: 'invalid',
      blocked: true,
      concurso_esperado: Number(concursoEsperado),
      message: 'Falha ao ler checkpoint: ' + String(err.message || err)
    };
  }
}

/** @deprecated use inspectCerebroCheckpoint — mantido para compat */
export async function loadGamesFromCerebroCheckpoint(env, concurso) {
  const gate = await inspectCerebroCheckpoint(env, concurso);
  if (gate.blocked || !gate.games) return null;
  return gate.games;
}

/**
 * Só persiste se TODOS os jogos tiverem origem cerebro_python + hash.
 * Também grava snapshot imutável da sugestão do dia (INSERT OR IGNORE).
 */
export async function persistSystemGames(env, concurso, games, options = {}) {
  const strict = options.strict !== false;
  await ensureJogosSistemaProvenance(env);

  if (!games || !games.length) {
    throw new Error('persistSystemGames: lista vazia');
  }

  if (strict) {
    for (const game of games) {
      if (game.origem !== 'cerebro_python') {
        throw new Error('Bloqueado: origem deve ser cerebro_python (sem fallback JS).');
      }
      if (!game.checkpoint_hash) {
        throw new Error('Bloqueado: checkpoint_hash obrigatório.');
      }
      if (!game.cerebro_version) {
        throw new Error('Bloqueado: cerebro_version obrigatória.');
      }
    }
  }

  for (const game of games) {
    const stats = scoreSet(game.dezenas);
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
      game.origem || 'cerebro_python',
      game.cerebro_version || null,
      game.checkpoint_hash || null,
      game.audit_brain_version || null,
      game.source_of_truth || 'python',
      game.checkpoint_generated_at || null
    ).run();
  }

  const first = games[0];
  try {
    await env.DB.prepare(`
      INSERT INTO checkpoint_ingest (
        concurso, origem, cerebro_version, checkpoint_hash,
        audit_brain_version, source_of_truth, checkpoint_generated_at,
        metodos_json, jogos_count
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      concurso,
      first.origem,
      first.cerebro_version,
      first.checkpoint_hash,
      first.audit_brain_version || null,
      first.source_of_truth || 'python',
      first.checkpoint_generated_at || null,
      JSON.stringify(games.map((g) => g.metodo)),
      games.length
    ).run();
  } catch (err) {
    console.error('checkpoint_ingest insert', err);
  }

  // Snapshot imutável ranqueado (não sobrescreve se já existir)
  try {
    const stats = await computeMethodScores(env, 30);
    const labHint = await extractLabHint(env);
    const sugestao = buildSugestaoDoDia(games, stats, labHint);
    await saveSugestaoSnapshot(env, concurso, sugestao.todos);
  } catch (err) {
    console.error('sugestao snapshot', err);
  }

  return games;
}

/**
 * Aplica checkpoint ao D1 ou retorna bloqueio explícito (nunca gera JS).
 */
export async function applyCerebroOrBlock(env, concurso) {
  const gate = await inspectCerebroCheckpoint(env, concurso);
  if (gate.blocked) {
    return {
      applied: false,
      blocked: true,
      concurso,
      status: gate.status,
      reason: gate.message,
      gate
    };
  }
  try {
    await persistSystemGames(env, concurso, gate.games, { strict: true });
    return {
      applied: true,
      blocked: false,
      concurso,
      status: 'active',
      jogos: gate.games.length,
      source: 'cerebro_python',
      cerebro_version: gate.cerebro_version,
      checkpoint_hash: gate.checkpoint_hash,
      metodos: gate.metodos,
      gate
    };
  } catch (err) {
    return {
      applied: false,
      blocked: true,
      concurso,
      status: 'persist_error',
      reason: String(err.message || err),
      gate
    };
  }
}
