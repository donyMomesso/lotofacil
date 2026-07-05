const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store"
};

const RECENT_RESULTS = [
  {
    concurso: 3726,
    data: "03/07/2026",
    dezenas: [2, 5, 6, 7, 10, 13, 14, 17, 18, 19, 20, 21, 22, 24, 25]
  },
  {
    concurso: 3725,
    data: "02/07/2026",
    dezenas: [1, 2, 4, 5, 6, 8, 11, 13, 14, 16, 17, 19, 21, 24, 25]
  }
];
const LOTOFACIL_API_BASE = "https://loteriascaixa-api.herokuapp.com/api/lotofacil";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: JSON_HEADERS
  });
}

function error(message, status = 400) {
  return json({ ok: false, message }, status);
}

async function readJson(request) {
  try {
    return await request.json();
  } catch {
    return {};
  }
}

function normalizeEmail(email) {
  return String(email || "").trim().toLowerCase();
}

function bytesToHex(bytes) {
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function bufferToBase64(buffer) {
  let binary = "";
  const bytes = new Uint8Array(buffer);

  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }

  return btoa(binary);
}

function base64ToBuffer(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);

  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }

  return bytes.buffer;
}

async function hashPassword(password) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    "PBKDF2",
    false,
    ["deriveBits"]
  );
  const derived = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: 100000, hash: "SHA-256" },
    key,
    256
  );

  return `pbkdf2_sha256$100000$${bytesToHex(salt)}$${bufferToBase64(derived)}`;
}

async function verifyPassword(password, storedHash) {
  const [method, iterationsRaw, saltHex, expectedBase64] = String(storedHash || "").split("$");

  if (method !== "pbkdf2_sha256" || !iterationsRaw || !saltHex || !expectedBase64) {
    return false;
  }

  const salt = new Uint8Array(saltHex.match(/.{1,2}/g).map((part) => parseInt(part, 16)));
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    "PBKDF2",
    false,
    ["deriveBits"]
  );
  const derived = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: Number(iterationsRaw), hash: "SHA-256" },
    key,
    256
  );
  const expected = new Uint8Array(base64ToBuffer(expectedBase64));
  const actual = new Uint8Array(derived);

  if (expected.length !== actual.length) {
    return false;
  }

  let diff = 0;

  for (let index = 0; index < expected.length; index += 1) {
    diff |= expected[index] ^ actual[index];
  }

  return diff === 0;
}

function createToken() {
  return bytesToHex(crypto.getRandomValues(new Uint8Array(32)));
}

function tokenExpirationDate() {
  const date = new Date();
  date.setDate(date.getDate() + 90);
  return date.toISOString();
}

function getBearerToken(request) {
  const header = request.headers.get("authorization") || "";
  const match = header.match(/^Bearer\s+(.+)$/i);
  return match ? match[1].trim() : "";
}

async function requireUser(request, env) {
  const token = getBearerToken(request);

  if (!token) {
    return null;
  }

  return env.DB.prepare(`
    SELECT usuarios.id, usuarios.nome, usuarios.email, usuarios.criado_em
    FROM sessoes
    JOIN usuarios ON usuarios.id = sessoes.usuario_id
    WHERE sessoes.token = ? AND datetime(sessoes.expira_em) > datetime('now')
  `).bind(token).first();
}

function normalizeDezenas(input) {
  const numbers = Array.isArray(input)
    ? input
    : String(input || "").match(/\d{1,2}/g) || [];
  const dezenas = numbers
    .map((value) => Number(value))
    .filter((value) => Number.isInteger(value) && value >= 1 && value <= 25);
  const unique = Array.from(new Set(dezenas)).sort((a, b) => a - b);

  if (unique.length < 15 || unique.length > 20) {
    throw new Error("Informe entre 15 e 20 dezenas validas.");
  }

  return unique;
}

function dezenasTexto(dezenas) {
  return dezenas.map((dezena) => String(dezena).padStart(2, "0")).join("-");
}

function parseApiResult(data) {
  const concurso = Number(data?.concurso || data?.numero || data?.numeroConcurso);
  const dataSorteio = String(data?.data || data?.dataApuracao || data?.dataSorteio || "").trim();
  const rawDezenas = data?.dezenas || data?.listaDezenas || data?.dezenasSorteadasOrdemSorteio || [];
  const dezenas = rawDezenas.map((value) => Number(value)).filter((value) => Number.isInteger(value));

  if (!concurso || dezenas.length !== 15) {
    return null;
  }

  return {
    concurso,
    data: dataSorteio,
    dezenas: dezenas.sort((a, b) => a - b)
  };
}

async function fetchConcurso(concurso) {
  const response = await fetch(`${LOTOFACIL_API_BASE}/${concurso}`, {
    headers: { accept: "application/json" }
  });

  if (!response.ok) {
    return null;
  }

  return parseApiResult(await response.json());
}

async function seedInitialResults(env) {
  const row = await env.DB.prepare("SELECT COUNT(*) AS total FROM resultados").first();

  if (row.total) {
    return;
  }

  for (const resultado of RECENT_RESULTS.slice().reverse()) {
    await env.DB.prepare(`
      INSERT OR IGNORE INTO resultados (concurso, data_sorteio, dezenas, dezenas_texto)
      VALUES (?, ?, ?, ?)
    `).bind(
      resultado.concurso,
      resultado.data,
      JSON.stringify(resultado.dezenas),
      dezenasTexto(resultado.dezenas)
    ).run();
  }
}

async function latestResult(env) {
  await seedInitialResults(env);
  const row = await env.DB.prepare(`
    SELECT concurso, data_sorteio, dezenas, dezenas_texto
    FROM resultados
    ORDER BY concurso DESC
    LIMIT 1
  `).first();

  if (!row) {
    return null;
  }

  return {
    concurso: row.concurso,
    data: row.data_sorteio,
    dezenas: JSON.parse(row.dezenas),
    dezenas_texto: row.dezenas_texto
  };
}

async function insertResult(env, resultado) {
  const inserted = await env.DB.prepare(`
    INSERT OR IGNORE INTO resultados (concurso, data_sorteio, dezenas, dezenas_texto)
    VALUES (?, ?, ?, ?)
  `).bind(
    resultado.concurso,
    resultado.data,
    JSON.stringify(resultado.dezenas),
    dezenasTexto(resultado.dezenas)
  ).run();

  return Boolean(inserted.meta.changes);
}

function scoreSet(dezenas) {
  const soma = dezenas.reduce((total, dezena) => total + dezena, 0);
  const pares = dezenas.filter((dezena) => dezena % 2 === 0).length;

  return { soma, pares, impares: dezenas.length - pares };
}

async function recentResultsForGeneration(env) {
  await seedInitialResults(env);
  const rows = await env.DB.prepare(`
    SELECT concurso, dezenas
    FROM resultados
    ORDER BY concurso DESC
    LIMIT 120
  `).all();

  return rows.results.map((row) => ({
    concurso: row.concurso,
    dezenas: JSON.parse(row.dezenas)
  }));
}

function generatedGamesFromResults(results, concurso) {
  const all = Array.from({ length: 25 }, (_, index) => index + 1);
  const freq = new Map(all.map((number) => [number, 0]));
  const lastSeen = new Map(all.map((number) => [number, 9999]));

  results.forEach((result, idx) => {
    const set = new Set(result.dezenas);
    for (const number of all) {
      if (set.has(number)) {
        freq.set(number, freq.get(number) + 1);
        lastSeen.set(number, Math.min(lastSeen.get(number), idx));
      }
    }
  });

  const byFreq = all.slice().sort((a, b) => freq.get(b) - freq.get(a) || a - b);
  const byLate = all.slice().sort((a, b) => lastSeen.get(b) - lastSeen.get(a) || a - b);
  const seed = (concurso * 9301 + 49297) % 233280;
  const shuffled = all.slice().sort((a, b) => ((a * seed) % 97) - ((b * seed) % 97));
  const balanced = [
    ...byFreq.slice(0, 5),
    ...byLate.slice(0, 5),
    ...shuffled
  ];
  const unique15 = (list) => Array.from(new Set(list)).slice(0, 15).sort((a, b) => a - b);
  const makeSumRange = () => {
    let best = unique15(balanced);
    let bestDiff = Math.abs(scoreSet(best).soma - 200);

    for (let offset = 0; offset < 25; offset += 1) {
      const candidate = unique15([...balanced.slice(offset), ...balanced.slice(0, offset), ...byFreq, ...byLate]);
      const diff = Math.abs(scoreSet(candidate).soma - 200);
      if (diff < bestDiff) {
        best = candidate;
        bestDiff = diff;
      }
    }

    return best;
  };

  return [
    { metodo: "M1_aleatorio_deterministico", dezenas: unique15(shuffled) },
    { metodo: "M2_mais_frequentes", dezenas: unique15(byFreq) },
    { metodo: "M3_mais_atrasadas", dezenas: unique15(byLate) },
    { metodo: "M4_balanceado", dezenas: unique15([...byFreq.slice(0, 8), ...byLate.slice(0, 7), ...shuffled]) },
    { metodo: "M5_soma_faixa_comum", dezenas: makeSumRange() }
  ];
}

async function generateNextContestGames(env, concurso) {
  const results = await recentResultsForGeneration(env);
  const games = generatedGamesFromResults(results, concurso);

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

async function register(request, env) {
  const body = await readJson(request);
  const nome = String(body.nome || "").trim();
  const email = normalizeEmail(body.email);
  const senha = String(body.senha || "");

  if (nome.length < 2) {
    return error("Informe o nome.");
  }

  if (!email.includes("@")) {
    return error("Informe um email valido.");
  }

  if (senha.length < 6) {
    return error("A senha precisa ter pelo menos 6 caracteres.");
  }

  const senhaHash = await hashPassword(senha);

  try {
    await env.DB.prepare(
      "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)"
    ).bind(nome, email, senhaHash).run();
    const user = await env.DB.prepare(
      "SELECT id, nome, email FROM usuarios WHERE email = ?"
    ).bind(email).first();
    const token = createToken();
    const expiraEm = tokenExpirationDate();

    await env.DB.prepare(
      "INSERT INTO sessoes (token, usuario_id, expira_em) VALUES (?, ?, ?)"
    ).bind(token, user.id, expiraEm).run();

    return json({
      ok: true,
      token,
      user
    }, 201);
  } catch (err) {
    if (String(err.message || "").includes("UNIQUE")) {
      return error("Este email ja esta cadastrado.", 409);
    }

    throw err;
  }
}

async function login(request, env) {
  const body = await readJson(request);
  const email = normalizeEmail(body.email);
  const senha = String(body.senha || "");
  const user = await env.DB.prepare(
    "SELECT id, nome, email, senha_hash FROM usuarios WHERE email = ?"
  ).bind(email).first();

  if (!user || !(await verifyPassword(senha, user.senha_hash))) {
    return error("Email ou senha invalidos.", 401);
  }

  const token = createToken();
  const expiraEm = tokenExpirationDate();

  await env.DB.prepare(
    "INSERT INTO sessoes (token, usuario_id, expira_em) VALUES (?, ?, ?)"
  ).bind(token, user.id, expiraEm).run();

  return json({
    ok: true,
    token,
    user: { id: user.id, nome: user.nome, email: user.email }
  });
}

async function logout(request, env) {
  const token = getBearerToken(request);

  if (token) {
    await env.DB.prepare("DELETE FROM sessoes WHERE token = ?").bind(token).run();
  }

  return json({ ok: true });
}

async function listJogos(user, env) {
  const result = await env.DB.prepare(`
    SELECT id, concurso, metodo, dezenas, dezenas_texto, status, observacao,
           manter_salvo, descartar_apos_rodadas, criado_em, atualizado_em
    FROM jogos
    WHERE usuario_id = ?
    ORDER BY datetime(criado_em) DESC
    LIMIT 200
  `).bind(user.id).all();

  const jogos = result.results.map((jogo) => ({
    ...jogo,
    manter_salvo: Boolean(jogo.manter_salvo),
    dezenas: JSON.parse(jogo.dezenas),
    conferencias: []
  }));
  const ids = jogos.map((jogo) => jogo.id);

  if (ids.length) {
    const placeholders = ids.map(() => "?").join(",");
    const confResult = await env.DB.prepare(`
      SELECT conferencias.jogo_id,
             conferencias.concurso,
             conferencias.dezenas_sorteadas,
             conferencias.acertos,
             conferencias.conferido_em
      FROM conferencias
      JOIN jogos ON jogos.id = conferencias.jogo_id
      WHERE jogos.usuario_id = ? AND conferencias.jogo_id IN (${placeholders})
      ORDER BY conferencias.concurso DESC
    `).bind(user.id, ...ids).all();
    const byGame = new Map(jogos.map((jogo) => [jogo.id, jogo]));

    for (const conferencia of confResult.results) {
      const jogo = byGame.get(conferencia.jogo_id);

      if (jogo) {
        jogo.conferencias.push({
          concurso: conferencia.concurso,
          dezenas_sorteadas: conferencia.dezenas_sorteadas,
          acertos: conferencia.acertos,
          conferido_em: conferencia.conferido_em
        });
      }
    }
  }

  return json({
    ok: true,
    jogos
  });
}

async function createJogo(request, user, env) {
  const body = await readJson(request);
  let dezenas;

  try {
    dezenas = normalizeDezenas(body.dezenas || body.dezenas_texto);
  } catch (err) {
    return error(err.message);
  }

  const concurso = body.concurso ? Number(body.concurso) : null;
  const metodo = String(body.metodo || "").trim() || null;
  const observacao = String(body.observacao || "").trim() || null;
  const manterSalvo = body.manter_salvo ? 1 : 0;
  const descartarAposRodadas = Number(body.descartar_apos_rodadas || 2);
  const texto = dezenasTexto(dezenas);
  const result = await env.DB.prepare(`
    INSERT INTO jogos (
      usuario_id, concurso, metodo, dezenas, dezenas_texto, observacao,
      manter_salvo, descartar_apos_rodadas
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    user.id,
    concurso,
    metodo,
    JSON.stringify(dezenas),
    texto,
    observacao,
    manterSalvo,
    Math.max(1, descartarAposRodadas)
  ).run();

  return json({
    ok: true,
    jogo: {
      id: result.meta.last_row_id,
      concurso,
      metodo,
      dezenas,
      dezenas_texto: texto,
      status: "salvo",
      observacao,
      manter_salvo: Boolean(manterSalvo),
      descartar_apos_rodadas: Math.max(1, descartarAposRodadas)
    }
  }, 201);
}

async function updateJogo(request, user, env, id) {
  const body = await readJson(request);
  const status = String(body.status || "").trim();
  const observacao = body.observacao === undefined ? undefined : String(body.observacao || "").trim();
  const manterSalvo = body.manter_salvo === undefined ? null : (body.manter_salvo ? 1 : 0);
  const allowedStatuses = new Set(["salvo", "jogado", "conferido", "cancelado"]);

  if (status && !allowedStatuses.has(status)) {
    return error("Status invalido.");
  }

  const existing = await env.DB.prepare(
    "SELECT id FROM jogos WHERE id = ? AND usuario_id = ?"
  ).bind(id, user.id).first();

  if (!existing) {
    return error("Jogo nao encontrado.", 404);
  }

  await env.DB.prepare(`
    UPDATE jogos
    SET status = COALESCE(NULLIF(?, ''), status),
        observacao = COALESCE(?, observacao),
        manter_salvo = COALESCE(?, manter_salvo),
        atualizado_em = CURRENT_TIMESTAMP
    WHERE id = ? AND usuario_id = ?
  `).bind(status, observacao, manterSalvo, id, user.id).run();

  return json({ ok: true });
}

async function deleteJogo(user, env, id) {
  await env.DB.prepare(
    "DELETE FROM jogos WHERE id = ? AND usuario_id = ?"
  ).bind(id, user.id).run();

  return json({ ok: true });
}

async function cleanupExpiredGames(env, userId = null) {
  const params = [];
  const userFilter = userId ? "AND jogos.usuario_id = ?" : "";

  if (userId) {
    params.push(userId);
  }

  const result = await env.DB.prepare(`
    SELECT jogos.id
    FROM jogos
    LEFT JOIN conferencias ON conferencias.jogo_id = jogos.id
    WHERE jogos.manter_salvo = 0
      AND jogos.status IN ('salvo', 'jogado', 'conferido')
      ${userFilter}
    GROUP BY jogos.id, jogos.descartar_apos_rodadas
    HAVING COUNT(conferencias.id) >= jogos.descartar_apos_rodadas
  `).bind(...params).all();
  const ids = result.results.map((row) => row.id);

  if (!ids.length) {
    return 0;
  }

  const placeholders = ids.map(() => "?").join(",");
  await env.DB.prepare(`DELETE FROM jogos WHERE id IN (${placeholders})`).bind(...ids).run();
  return ids.length;
}

async function conferirDuasRodadas(user, env) {
  await seedInitialResults(env);
  const latestRows = await env.DB.prepare(`
    SELECT concurso, data_sorteio, dezenas, dezenas_texto
    FROM resultados
    ORDER BY concurso DESC
    LIMIT 2
  `).all();
  const rodadas = latestRows.results.map((row) => ({
    concurso: row.concurso,
    data: row.data_sorteio,
    dezenas: JSON.parse(row.dezenas),
    dezenas_texto: row.dezenas_texto
  }));
  const result = await env.DB.prepare(`
    SELECT id, dezenas
    FROM jogos
    WHERE usuario_id = ? AND status IN ('salvo', 'jogado', 'conferido')
    ORDER BY datetime(criado_em) DESC
    LIMIT 200
  `).bind(user.id).all();
  let novas = 0;
  let atualizadas = 0;
  const resumo = [];

  for (const jogo of result.results) {
    const dezenas = new Set(JSON.parse(jogo.dezenas));

    for (const rodada of rodadas) {
      const acertos = rodada.dezenas.filter((dezena) => dezenas.has(dezena)).length;
      const dezenasSorteadas = rodada.dezenas_texto;
      const insert = await env.DB.prepare(`
        INSERT OR IGNORE INTO conferencias (jogo_id, concurso, dezenas_sorteadas, acertos)
        VALUES (?, ?, ?, ?)
      `).bind(jogo.id, rodada.concurso, dezenasSorteadas, acertos).run();

      if (insert.meta.changes) {
        novas += 1;
      } else {
        await env.DB.prepare(`
          UPDATE conferencias
          SET dezenas_sorteadas = ?, acertos = ?, conferido_em = CURRENT_TIMESTAMP
          WHERE jogo_id = ? AND concurso = ?
        `).bind(dezenasSorteadas, acertos, jogo.id, rodada.concurso).run();
        atualizadas += 1;
      }

      resumo.push({
        jogo_id: jogo.id,
        concurso: rodada.concurso,
        dezenas_sorteadas: dezenasSorteadas,
        acertos
      });
    }
  }

  if (result.results.length) {
    await env.DB.prepare(`
      UPDATE jogos
      SET status = 'conferido', atualizado_em = CURRENT_TIMESTAMP
      WHERE usuario_id = ? AND status IN ('salvo', 'jogado', 'conferido')
    `).bind(user.id).run();
  }
  const descartados = await cleanupExpiredGames(env, user.id);

  return json({
    ok: true,
    rodadas: rodadas.map((rodada) => ({
      concurso: rodada.concurso,
      data: rodada.data,
      dezenas_sorteadas: rodada.dezenas_texto
    })),
    jogos_conferidos: result.results.length,
    conferencias_novas: novas,
    conferencias_atualizadas: atualizadas,
    jogos_descartados: descartados,
    resumo
  });
}

async function conferirResultadoParaJogos(env, resultado) {
  const jogos = await env.DB.prepare(`
    SELECT id, dezenas
    FROM jogos
    WHERE concurso = ? AND status IN ('salvo', 'jogado', 'conferido')
  `).bind(resultado.concurso).all();
  let conferidos = 0;

  for (const jogo of jogos.results) {
    const dezenas = new Set(JSON.parse(jogo.dezenas));
    const acertos = resultado.dezenas.filter((dezena) => dezenas.has(dezena)).length;

    await env.DB.prepare(`
      INSERT OR IGNORE INTO conferencias (jogo_id, concurso, dezenas_sorteadas, acertos)
      VALUES (?, ?, ?, ?)
    `).bind(jogo.id, resultado.concurso, dezenasTexto(resultado.dezenas), acertos).run();
    await env.DB.prepare(`
      UPDATE conferencias
      SET dezenas_sorteadas = ?, acertos = ?, conferido_em = CURRENT_TIMESTAMP
      WHERE jogo_id = ? AND concurso = ?
    `).bind(dezenasTexto(resultado.dezenas), acertos, jogo.id, resultado.concurso).run();
    conferidos += 1;
  }

  if (conferidos) {
    await env.DB.prepare(`
      UPDATE jogos
      SET status = 'conferido', atualizado_em = CURRENT_TIMESTAMP
      WHERE concurso = ? AND status IN ('salvo', 'jogado', 'conferido')
    `).bind(resultado.concurso).run();
    await cleanupExpiredGames(env);
  }

  return conferidos;
}

async function runAutoCycle(env) {
  const latest = await latestResult(env);
  let nextToFetch = latest ? latest.concurso + 1 : 1;
  const novos = [];
  let conferencias = 0;

  for (let attempts = 0; attempts < 5; attempts += 1) {
    const resultado = await fetchConcurso(nextToFetch);

    if (!resultado) {
      break;
    }

    const inserted = await insertResult(env, resultado);

    if (inserted) {
      novos.push(resultado);
      conferencias += await conferirResultadoParaJogos(env, resultado);
    }

    nextToFetch += 1;
  }

  const currentLatest = await latestResult(env);
  const proximoConcurso = currentLatest ? currentLatest.concurso + 1 : 1;
  const jogosGerados = await generateNextContestGames(env, proximoConcurso);

  return {
    ok: true,
    novos_concursos: novos.map((resultado) => resultado.concurso),
    conferencias,
    proximo_concurso: proximoConcurso,
    jogos_gerados: jogosGerados.length
  };
}

async function systemStatus(env) {
  const latest = await latestResult(env);
  const proximoConcurso = latest ? latest.concurso + 1 : 1;
  await generateNextContestGames(env, proximoConcurso);
  const generated = await env.DB.prepare(`
    SELECT concurso, metodo, dezenas, dezenas_texto, soma, pares, impares
    FROM jogos_sistema
    WHERE concurso = ?
    ORDER BY metodo
  `).bind(proximoConcurso).all();

  return json({
    ok: true,
    ultimo_resultado: latest,
    proximo_concurso: proximoConcurso,
    jogos_gerados: generated.results.map((jogo) => ({
      ...jogo,
      dezenas: JSON.parse(jogo.dezenas)
    }))
  });
}

async function handleApi(request, env, url) {
  const method = request.method;
  const path = url.pathname;

  if (method === "OPTIONS") {
    return new Response(null, { status: 204 });
  }

  if (path === "/api/health") {
    return json({ ok: true, service: "lotofacil" });
  }

  if (path === "/api/sistema/status" && method === "GET") {
    return systemStatus(env);
  }

  if (path === "/api/auth/register" && method === "POST") {
    return register(request, env);
  }

  if (path === "/api/auth/login" && method === "POST") {
    return login(request, env);
  }

  const user = await requireUser(request, env);

  if (!user) {
    return error("Acesso nao autorizado.", 401);
  }

  if (path === "/api/auth/logout" && method === "POST") {
    return logout(request, env);
  }

  if (path === "/api/me" && method === "GET") {
    return json({ ok: true, user });
  }

  if (path === "/api/ciclo/rodar" && method === "POST") {
    return json(await runAutoCycle(env));
  }

  if (path === "/api/jogos" && method === "GET") {
    return listJogos(user, env);
  }

  if (path === "/api/jogos" && method === "POST") {
    return createJogo(request, user, env);
  }

  if (path === "/api/jogos/conferir-duas-rodadas" && method === "POST") {
    return conferirDuasRodadas(user, env);
  }

  const jogoMatch = path.match(/^\/api\/jogos\/(\d+)$/);

  if (jogoMatch && method === "PATCH") {
    return updateJogo(request, user, env, Number(jogoMatch[1]));
  }

  if (jogoMatch && method === "DELETE") {
    return deleteJogo(user, env, Number(jogoMatch[1]));
  }

  return error("Rota nao encontrada.", 404);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    try {
      if (url.pathname.startsWith("/api/")) {
        return await handleApi(request, env, url);
      }

      return env.ASSETS.fetch(request);
    } catch (err) {
      console.error(err);
      return error("Erro interno do servidor.", 500);
    }
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(runAutoCycle(env));
  }
};
