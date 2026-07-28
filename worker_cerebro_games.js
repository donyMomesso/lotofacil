/**
 * Consumo do checkpoint operacional do Cérebro Python.
 * Quando o asset existir e o concurso_alvo bater, o Worker NÃO recalcula métodos em JS.
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
 * @param {any} env Cloudflare env com ASSETS + DB
 * @param {number} concurso concurso alvo
 * @returns {Promise<null | Array<{metodo: string, dezenas: number[]}>>}
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

    const games = [];
    for (const [metodo, info] of Object.entries(ck.jogos_estudo)) {
      const dezenas = Array.isArray(info)
        ? info.map(Number)
        : (info.dezenas || []).map(Number);
      if (dezenas.length !== 15) continue;
      games.push({
        metodo,
        dezenas: dezenas.slice().sort((a, b) => a - b),
        source: 'cerebro_python',
        cerebro_version: ck.cerebro_version || null,
        checkpoint_hash: ck.checkpoint_hash || null
      });
    }
    return games.length ? games : null;
  } catch (err) {
    console.error('checkpoint operacional indisponível', err);
    return null;
  }
}

export async function persistSystemGames(env, concurso, games) {
  for (const game of games) {
    const stats = scoreSet(game.dezenas);
    await env.DB.prepare(`
      INSERT INTO jogos_sistema (concurso, metodo, dezenas, dezenas_texto, soma, pares, impares)
      VALUES (?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(concurso, metodo) DO UPDATE SET
        dezenas = excluded.dezenas,
        dezenas_texto = excluded.dezenas_texto,
        soma = excluded.soma,
        pares = excluded.pares,
        impares = excluded.impares,
        criado_em = CURRENT_TIMESTAMP
    `).bind(
      concurso,
      game.metodo,
      JSON.stringify(game.dezenas),
      dezenasTexto(game.dezenas),
      stats.soma,
      stats.pares,
      stats.impares
    ).run();
  }
  return games;
}
