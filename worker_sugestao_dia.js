/**
 * Sugestão do dia: ranking M1–M9 + snapshot imutável por concurso.
 */

function dezenasTexto(dezenas) {
  return (dezenas || []).map((d) => String(d).padStart(2, '0')).join('-');
}

function countHits(jogoDezenas, sorteadas) {
  const set = new Set((sorteadas || []).map(Number));
  return (jogoDezenas || []).filter((d) => set.has(Number(d))).length;
}

export async function ensureSugestaoSchema(env) {
  if (!env?.DB) return;
  try {
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS sugestao_dia_snapshot (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concurso INTEGER NOT NULL,
        metodo TEXT NOT NULL,
        dezenas TEXT NOT NULL,
        dezenas_texto TEXT,
        camada TEXT,
        rank_pos INTEGER,
        score REAL,
        origem TEXT,
        cerebro_version TEXT,
        checkpoint_hash TEXT,
        criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(concurso, metodo)
      )
    `).run();
  } catch (e) {
    console.error('sugestao_dia_snapshot', e);
  }
  try {
    await env.DB.prepare(`
      CREATE INDEX IF NOT EXISTS idx_sugestao_concurso ON sugestao_dia_snapshot(concurso)
    `).run();
  } catch { /* ok */ }
}

/**
 * Scores históricos por método (últimos N concursos com resultado).
 */
export async function computeMethodScores(env, limit = 30) {
  await ensureSugestaoSchema(env);
  const lim = Math.min(Math.max(Number(limit) || 30, 5), 80);

  const resultados = await env.DB.prepare(`
    SELECT concurso, dezenas FROM resultados
    ORDER BY concurso DESC LIMIT ?
  `).bind(lim).all();

  const rows = resultados?.results || [];
  if (!rows.length) return { scores: new Map(), por_metodo: [], n: 0 };

  const minC = Math.min(...rows.map((r) => Number(r.concurso)));
  const maxC = Math.max(...rows.map((r) => Number(r.concurso)));

  // Preferir snapshot; fallback jogos_sistema
  let jogos = [];
  try {
    const snap = await env.DB.prepare(`
      SELECT concurso, metodo, dezenas, origem
      FROM sugestao_dia_snapshot
      WHERE concurso >= ? AND concurso <= ?
    `).bind(minC, maxC).all();
    jogos = snap?.results || [];
  } catch { jogos = []; }

  if (!jogos.length) {
    try {
      const js = await env.DB.prepare(`
        SELECT concurso, metodo, dezenas, origem
        FROM jogos_sistema
        WHERE concurso >= ? AND concurso <= ?
      `).bind(minC, maxC).all();
      jogos = js?.results || [];
    } catch { jogos = []; }
  }

  const byConcursoJogos = new Map();
  for (const j of jogos) {
    const c = Number(j.concurso);
    if (!byConcursoJogos.has(c)) byConcursoJogos.set(c, []);
    byConcursoJogos.get(c).push(j);
  }

  // Preferir cerebro_python quando misturado
  for (const [c, list] of byConcursoJogos) {
    const py = list.filter((x) => x.origem === 'cerebro_python');
    if (py.length) byConcursoJogos.set(c, py);
  }

  const agg = new Map();

  for (const res of rows) {
    const concurso = Number(res.concurso);
    let sorteadas = [];
    try { sorteadas = JSON.parse(res.dezenas || '[]'); } catch { sorteadas = []; }
    const list = byConcursoJogos.get(concurso) || [];
    for (const j of list) {
      let dez = [];
      try { dez = JSON.parse(j.dezenas || '[]'); } catch { dez = []; }
      const acertos = countHits(dez, sorteadas);
      const key = j.metodo || 'desconhecido';
      const a = agg.get(key) || { metodo: key, jogos: 0, soma: 0, melhor: 0, a11: 0 };
      a.jogos += 1;
      a.soma += acertos;
      if (acertos > a.melhor) a.melhor = acertos;
      if (acertos >= 11) a.a11 += 1;
      agg.set(key, a);
    }
  }

  const por_metodo = Array.from(agg.values()).map((m) => {
    const media = m.jogos ? m.soma / m.jogos : 0;
    const taxa11 = m.jogos ? (m.a11 * 100) / m.jogos : 0;
    // Score: prioriza média e presença em 11+, com leve peso no melhor
    const score = media + taxa11 * 0.04 + m.melhor * 0.08;
    return {
      metodo: m.metodo,
      jogos: m.jogos,
      media: Number(media.toFixed(2)),
      melhor: m.melhor,
      taxa_11_mais: Number(taxa11.toFixed(1)),
      score: Number(score.toFixed(4))
    };
  }).sort((a, b) => b.score - a.score || b.media - a.media);

  const scores = new Map(por_metodo.map((m) => [m.metodo, m]));
  return { scores, por_metodo, n: rows.length };
}

/**
 * Monta carteira ranqueada: top3 prioritário, mid3 diversificação, rest exploração.
 */
export function buildSugestaoDoDia(games, methodStats, labHint = null) {
  const list = (games || []).map((g) => {
    const st = methodStats.scores?.get(g.metodo);
    let score = st?.score ?? 9;
    // Bônus leve se lab aponta perfil semelhante (heurística por nome)
    if (labHint && st) {
      const lab = String(labHint).toLowerCase();
      const met = String(g.metodo || '').toLowerCase();
      if (lab.includes('miolo') && met.includes('cobertura')) score += 0.15;
      if (lab.includes('inicio') && (met.includes('frequente') || met.includes('aleatorio'))) score += 0.1;
      if (lab.includes('repet') && met.includes('repeticao')) score += 0.2;
    }
    return {
      ...g,
      dezenas_texto: g.dezenas_texto || dezenasTexto(g.dezenas),
      hist_media: st?.media ?? null,
      hist_melhor: st?.melhor ?? null,
      hist_taxa_11: st?.taxa_11_mais ?? null,
      hist_jogos: st?.jogos ?? 0,
      score: Number(score.toFixed(4))
    };
  });

  list.sort((a, b) => b.score - a.score || String(a.metodo).localeCompare(String(b.metodo)));

  const ranked = list.map((g, idx) => {
    let camada = 'exploracao';
    if (idx < 3) camada = 'prioritario';
    else if (idx < 6) camada = 'diversificacao';
    return { ...g, rank_pos: idx + 1, camada };
  });

  return {
    prioritarios: ranked.filter((g) => g.camada === 'prioritario'),
    diversificacao: ranked.filter((g) => g.camada === 'diversificacao'),
    exploracao: ranked.filter((g) => g.camada === 'exploracao'),
    todos: ranked,
    ranking_metodos: methodStats.por_metodo || [],
    lab_hint: labHint,
    note: 'Carteira de estudo. Média aleatória ≈ 9. Ranking usa histórico recente + lab (quando houver).'
  };
}

/**
 * Grava snapshot IMUTÁVEL: INSERT OR IGNORE (não sobrescreve após criado).
 */
export async function saveSugestaoSnapshot(env, concurso, rankedGames) {
  await ensureSugestaoSchema(env);
  if (!rankedGames?.length) return { saved: 0 };

  let saved = 0;
  for (const g of rankedGames) {
    try {
      const result = await env.DB.prepare(`
        INSERT OR IGNORE INTO sugestao_dia_snapshot (
          concurso, metodo, dezenas, dezenas_texto,
          camada, rank_pos, score,
          origem, cerebro_version, checkpoint_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        concurso,
        g.metodo,
        JSON.stringify(g.dezenas),
        g.dezenas_texto || dezenasTexto(g.dezenas),
        g.camada || null,
        g.rank_pos || null,
        g.score ?? null,
        g.origem || 'cerebro_python',
        g.cerebro_version || null,
        g.checkpoint_hash || null
      ).run();
      if (result?.meta?.changes) saved += 1;
    } catch (e) {
      console.error('snapshot', g.metodo, e);
    }
  }
  return { saved, total: rankedGames.length };
}

export async function loadSnapshot(env, concurso) {
  await ensureSugestaoSchema(env);
  try {
    const rows = await env.DB.prepare(`
      SELECT concurso, metodo, dezenas, dezenas_texto, camada, rank_pos, score,
             origem, cerebro_version, checkpoint_hash, criado_em
      FROM sugestao_dia_snapshot
      WHERE concurso = ?
      ORDER BY rank_pos ASC, metodo
    `).bind(concurso).all();
    return (rows?.results || []).map((r) => {
      let dezenas = [];
      try { dezenas = JSON.parse(r.dezenas || '[]'); } catch { dezenas = []; }
      return { ...r, dezenas };
    });
  } catch {
    return [];
  }
}

export async function extractLabHint(env) {
  try {
    const row = await env.DB.prepare(`
      SELECT melhor_json, estrategias_json FROM laboratorio_execucoes
      WHERE status = 'conferido'
      ORDER BY concurso DESC, id DESC LIMIT 1
    `).first();
    if (!row) return null;
    let melhor = null;
    try { melhor = row.melhor_json ? JSON.parse(row.melhor_json) : null; } catch { melhor = null; }
    if (melhor?.estrategia) return String(melhor.estrategia);
    let estrat = [];
    try { estrat = row.estrategias_json ? JSON.parse(row.estrategias_json) : []; } catch { estrat = []; }
    if (estrat[0]?.label) return String(estrat[0].label);
    if (estrat[0]?.key) return String(estrat[0].key);
    return null;
  } catch {
    return null;
  }
}
