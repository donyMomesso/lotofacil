/**
 * D1/SQLite tem limite de variáveis SQL (~100–999).
 * Nunca montar WHERE id IN (centenas de ?).
 */

const CHUNK = 40;

export async function batchUpdateByIds(env, sqlPrefix, ids, extraBinds = []) {
  if (!ids || !ids.length) return 0;
  let changes = 0;
  for (let i = 0; i < ids.length; i += CHUNK) {
    const chunk = ids.slice(i, i + CHUNK);
    const placeholders = chunk.map(() => '?').join(',');
    const sql = `${sqlPrefix} (${placeholders})`;
    const result = await env.DB.prepare(sql).bind(...extraBinds, ...chunk).run();
    changes += result.meta?.changes || 0;
  }
  return changes;
}

/**
 * Cancela jogos expirados sem lista gigante de binds.
 * Usa subquery aninhada (padrão SQLite para UPDATE + SELECT na mesma tabela).
 */
export async function cleanupExpiredGamesSafe(env, userId = null) {
  try {
    if (userId) {
      const result = await env.DB.prepare(`
        UPDATE jogos
        SET status = 'cancelado',
            atualizado_em = CURRENT_TIMESTAMP
        WHERE usuario_id = ?
          AND manter_salvo = 0
          AND status IN ('salvo', 'jogado', 'conferido')
          AND id IN (
            SELECT id FROM (
              SELECT j.id AS id
              FROM jogos j
              LEFT JOIN conferencias c ON c.jogo_id = j.id
              WHERE j.usuario_id = ?
                AND j.manter_salvo = 0
                AND j.status IN ('salvo', 'jogado', 'conferido')
              GROUP BY j.id, j.descartar_apos_rodadas
              HAVING COUNT(c.id) >= j.descartar_apos_rodadas
            )
          )
      `).bind(userId, userId).run();
      return result.meta?.changes || 0;
    }

    const result = await env.DB.prepare(`
      UPDATE jogos
      SET status = 'cancelado',
          atualizado_em = CURRENT_TIMESTAMP
      WHERE manter_salvo = 0
        AND status IN ('salvo', 'jogado', 'conferido')
        AND id IN (
          SELECT id FROM (
            SELECT j.id AS id
            FROM jogos j
            LEFT JOIN conferencias c ON c.jogo_id = j.id
            WHERE j.manter_salvo = 0
              AND j.status IN ('salvo', 'jogado', 'conferido')
            GROUP BY j.id, j.descartar_apos_rodadas
            HAVING COUNT(c.id) >= j.descartar_apos_rodadas
          )
        )
    `).run();
    return result.meta?.changes || 0;
  } catch (err) {
    console.error('cleanupExpiredGamesSafe', err);
    // fallback em lotes via SELECT + UPDATE
    const params = [];
    const userFilter = userId ? 'AND jogos.usuario_id = ?' : '';
    if (userId) params.push(userId);
    const result = await env.DB.prepare(`
      SELECT jogos.id
      FROM jogos
      LEFT JOIN conferencias ON conferencias.jogo_id = jogos.id
      WHERE jogos.manter_salvo = 0
        AND jogos.status IN ('salvo', 'jogado', 'conferido')
        ${userFilter}
      GROUP BY jogos.id, jogos.descartar_apos_rodadas
      HAVING COUNT(conferencias.id) >= jogos.descartar_apos_rodadas
      LIMIT 500
    `).bind(...params).all();
    const ids = (result.results || []).map((row) => row.id);
    if (!ids.length) return 0;
    await batchUpdateByIds(
      env,
      `UPDATE jogos SET status = 'cancelado', atualizado_em = CURRENT_TIMESTAMP WHERE id IN`,
      ids
    );
    return ids.length;
  }
}
