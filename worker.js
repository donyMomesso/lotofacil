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
    SELECT id, concurso, metodo, dezenas, dezenas_texto, status, observacao, criado_em, atualizado_em
    FROM jogos
    WHERE usuario_id = ?
    ORDER BY datetime(criado_em) DESC
    LIMIT 200
  `).bind(user.id).all();

  const jogos = result.results.map((jogo) => ({
    ...jogo,
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
  const texto = dezenasTexto(dezenas);
  const result = await env.DB.prepare(`
    INSERT INTO jogos (usuario_id, concurso, metodo, dezenas, dezenas_texto, observacao)
    VALUES (?, ?, ?, ?, ?, ?)
  `).bind(user.id, concurso, metodo, JSON.stringify(dezenas), texto, observacao).run();

  return json({
    ok: true,
    jogo: {
      id: result.meta.last_row_id,
      concurso,
      metodo,
      dezenas,
      dezenas_texto: texto,
      status: "salvo",
      observacao
    }
  }, 201);
}

async function updateJogo(request, user, env, id) {
  const body = await readJson(request);
  const status = String(body.status || "").trim();
  const observacao = body.observacao === undefined ? undefined : String(body.observacao || "").trim();
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
        atualizado_em = CURRENT_TIMESTAMP
    WHERE id = ? AND usuario_id = ?
  `).bind(status, observacao, id, user.id).run();

  return json({ ok: true });
}

async function deleteJogo(user, env, id) {
  await env.DB.prepare(
    "DELETE FROM jogos WHERE id = ? AND usuario_id = ?"
  ).bind(id, user.id).run();

  return json({ ok: true });
}

async function conferirDuasRodadas(user, env) {
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

    for (const rodada of RECENT_RESULTS.slice(0, 2)) {
      const acertos = rodada.dezenas.filter((dezena) => dezenas.has(dezena)).length;
      const dezenasSorteadas = dezenasTexto(rodada.dezenas);
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

  return json({
    ok: true,
    rodadas: RECENT_RESULTS.slice(0, 2).map((rodada) => ({
      concurso: rodada.concurso,
      data: rodada.data,
      dezenas_sorteadas: dezenasTexto(rodada.dezenas)
    })),
    jogos_conferidos: result.results.length,
    conferencias_novas: novas,
    conferencias_atualizadas: atualizadas,
    resumo
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
  }
};
