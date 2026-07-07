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

const OUTER_RING = new Set([1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25]);

function origemMetodo(metodo) {
  const raw = String(metodo || "").trim();
  if (/^Sistema\s+M[1-8]\b/i.test(raw)) {
    return raw.match(/^Sistema\s+M[1-8]/i)[0].replace(/\s+/, " ");
  }
  if (/^Painel IA Direto/i.test(raw)) return "IA Direto";
  if (/^Painel Manual/i.test(raw)) return "Manual";
  if (/^Painel/i.test(raw)) return raw.replace(/^Painel\s*/i, "") || "Painel";
  return raw || "Painel";
}

function statsDezenasTexto(texto) {
  const dezenas = normalizeDezenas(texto).slice(0, 15);
  const soma = dezenas.reduce((acc, dezena) => acc + dezena, 0);
  const pares = dezenas.filter((dezena) => dezena % 2 === 0).length;
  const moldura = dezenas.filter((dezena) => OUTER_RING.has(dezena)).length;

  return {
    soma,
    pares,
    impares: dezenas.length - pares,
    moldura,
    miolo: dezenas.length - moldura
  };
}

function media(valores) {
  return valores.length
    ? valores.reduce((acc, valor) => acc + valor, 0) / valores.length
    : 0;
}

function desvioPadraoPopulacional(valores) {
  if (!valores.length) return 0;
  const m = media(valores);
  return Math.sqrt(media(valores.map((valor) => (valor - m) ** 2)));
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

async function resultStats(env, limit = 50) {
  await seedInitialResults(env);
  const latest = await latestResult(env);
  const total = await env.DB.prepare("SELECT COUNT(*) AS total FROM resultados").first();
  const recentes = await env.DB.prepare(`
    SELECT concurso, data_sorteio, dezenas, dezenas_texto
    FROM resultados
    ORDER BY concurso DESC
    LIMIT ?
  `).bind(limit).all();

  return {
    total_concursos: total.total || 0,
    ultimo_resultado: latest,
    resultados_recentes: recentes.results.map((row) => ({
      concurso: row.concurso,
      data: row.data_sorteio,
      dezenas: JSON.parse(row.dezenas),
      dezenas_texto: row.dezenas_texto
    }))
  };
}

async function numberStats(env) {
  const rows = await env.DB.prepare(`
    SELECT concurso, dezenas
    FROM resultados
    ORDER BY concurso DESC
  `).all();
  const freq = new Map(Array.from({ length: 25 }, (_, index) => [index + 1, 0]));
  const atraso = new Map(Array.from({ length: 25 }, (_, index) => [index + 1, rows.results.length]));
  const seen = new Set();

  rows.results.forEach((row, idx) => {
    const dezenas = JSON.parse(row.dezenas);
    for (const dezena of dezenas) {
      freq.set(dezena, (freq.get(dezena) || 0) + 1);
      if (!seen.has(dezena)) {
        atraso.set(dezena, idx);
        seen.add(dezena);
      }
    }
  });

  const total = rows.results.length;
  return Array.from({ length: 25 }, (_, index) => {
    const dezena = index + 1;
    return {
      dezena,
      dezena_texto: String(dezena).padStart(2, "0"),
      frequencia: freq.get(dezena) || 0,
      frequencia_pct: total ? Number(((freq.get(dezena) || 0) * 100 / total).toFixed(2)) : 0,
      atraso: atraso.get(dezena) || 0
    };
  });
}

async function latestCycle(env) {
  const row = await env.DB.prepare(`
    SELECT id, iniciado_em, finalizado_em, status, novos_concursos, conferencias,
           jogos_descartados, sessoes_expiradas, proximo_concurso, jogos_gerados, erro
    FROM execucoes_ciclo
    ORDER BY datetime(iniciado_em) DESC
    LIMIT 1
  `).first();

  if (!row) {
    return null;
  }

  return {
    ...row,
    novos_concursos: JSON.parse(row.novos_concursos || "[]")
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

function seededRandom(seed) {
  let state = seed % 2147483647;
  if (state <= 0) state += 2147483646;
  return () => {
    state = state * 16807 % 2147483647;
    return (state - 1) / 2147483646;
  };
}

function sampleNumbers(randomFn, size = 15) {
  const numbers = Array.from({ length: 25 }, (_, index) => index + 1);
  for (let i = numbers.length - 1; i > 0; i -= 1) {
    const j = Math.floor(randomFn() * (i + 1));
    [numbers[i], numbers[j]] = [numbers[j], numbers[i]];
  }
  return numbers.slice(0, size).sort((a, b) => a - b);
}

function pairKey(a, b) {
  return `${Math.min(a, b)}-${Math.max(a, b)}`;
}

function recentPairs(results, limit = 30) {
  const pairs = new Set();
  for (const result of results.slice(0, limit)) {
    const dezenas = result.dezenas.slice().sort((a, b) => a - b);
    for (let i = 0; i < dezenas.length; i += 1) {
      for (let j = i + 1; j < dezenas.length; j += 1) {
        pairs.add(pairKey(dezenas[i], dezenas[j]));
      }
    }
  }
  return pairs;
}

function repeatedCount(dezenas, previousResult) {
  const previous = new Set(previousResult || []);
  return dezenas.filter((dezena) => previous.has(dezena)).length;
}

function adjacentPairCoverage(dezenas, pairs) {
  let total = 0;
  for (let i = 1; i < dezenas.length; i += 1) {
    if (pairs.has(pairKey(dezenas[i - 1], dezenas[i]))) {
      total += 1;
    }
  }
  return total;
}

function advancedScore(dezenas, pairs, previousResult) {
  const { soma, pares } = scoreSet(dezenas);
  const repeticoes = repeatedCount(dezenas, previousResult);
  const cobertura = adjacentPairCoverage(dezenas, pairs);
  let score = 0;

  if (soma >= 185 && soma <= 215) {
    score += 10;
    score += 10 * (1 - Math.abs(soma - 200) / 30);
  }
  if (pares >= 7 && pares <= 9) score += 8;
  if (repeticoes >= 8 && repeticoes <= 11) {
    score += 12;
    score += (repeticoes - 7) * 1.5;
  }
  if (cobertura >= 8) score += 15 + (cobertura - 8) * 2;
  if (soma < 170 || soma > 230) score -= 20;
  if (pares < 6 || pares > 10) score -= 10;

  return Math.max(0, score);
}

function bestAdvancedGame(results, concurso, salt, filterFn = null) {
  const previousResult = results[0]?.dezenas || [];
  const pairs = recentPairs(results);
  const randomFn = seededRandom(concurso * 1009 + salt * 7919);
  let best = null;
  let bestScore = -1;

  for (let i = 0; i < 1500; i += 1) {
    const candidate = sampleNumbers(randomFn);
    const repeticoes = repeatedCount(candidate, previousResult);
    const stats = scoreSet(candidate);

    if (filterFn && !filterFn(candidate, stats, repeticoes)) {
      continue;
    }

    const score = advancedScore(candidate, pairs, previousResult);
    if (score > bestScore) {
      best = candidate;
      bestScore = score;
    }
  }

  return best || sampleNumbers(randomFn);
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
    { metodo: "M5_soma_faixa_comum", dezenas: makeSumRange() },
    {
      metodo: "M6_filtros_combinados",
      dezenas: bestAdvancedGame(results, concurso, 6, (candidate, stats, repeticoes) => (
        stats.soma >= 185 && stats.soma <= 215
        && stats.pares >= 7 && stats.pares <= 9
        && repeticoes >= 8 && repeticoes <= 11
      ))
    },
    { metodo: "M7_cobertura_pares", dezenas: bestAdvancedGame(results, concurso, 7) },
    {
      metodo: "M8_repeticao_controlada",
      dezenas: bestAdvancedGame(results, concurso, 8, (candidate, stats, repeticoes) => repeticoes >= 9 && repeticoes <= 11)
    }
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

async function cleanupExpiredSessions(env) {
  const result = await env.DB.prepare(
    "DELETE FROM sessoes WHERE datetime(expira_em) <= datetime('now')"
  ).run();

  return result.meta.changes || 0;
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
             conferencias.dezenas_jogadas,
             conferencias.dezenas_sorteadas,
             conferencias.dezenas_acertadas,
             conferencias.acertos,
             conferencias.metodo,
             conferencias.conferido_em
      FROM conferencias
      JOIN jogos ON jogos.id = conferencias.jogo_id
      WHERE jogos.usuario_id = ? AND conferencias.jogo_id IN (${placeholders})
      ORDER BY conferencias.concurso ASC
    `).bind(user.id, ...ids).all();
    const byGame = new Map(jogos.map((jogo) => [jogo.id, jogo]));

    for (const conferencia of confResult.results) {
      const jogo = byGame.get(conferencia.jogo_id);

      if (jogo) {
        const rodada = jogo.conferencias.length + 1;
        const descartadoAposRodada = !jogo.manter_salvo && rodada >= Number(jogo.descartar_apos_rodadas || 2);
        jogo.conferencias.push({
          rodada,
          concurso: conferencia.concurso,
          dezenas_jogadas: conferencia.dezenas_jogadas || jogo.dezenas_texto,
          dezenas_sorteadas: conferencia.dezenas_sorteadas,
          dezenas_acertadas: conferencia.dezenas_acertadas || "",
          acertos: conferencia.acertos,
          metodo: conferencia.metodo || jogo.metodo,
          retencao: descartadoAposRodada ? "descartado" : "mantido",
          conferido_em: conferencia.conferido_em
        });
      }
    }

    for (const jogo of jogos) {
      jogo.conferencias.sort((a, b) => b.concurso - a.concurso);
    }
  }

  return json({
    ok: true,
    jogos,
    indicadores_rodada: await indicadoresRodada(user.id, env),
    aprendizado_origens: await aprendizadoOrigens(user.id, env)
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

async function indicadoresRodada(userId, env) {
  const latest = await env.DB.prepare(`
    SELECT MAX(conferencias.concurso) AS concurso
    FROM conferencias
    JOIN jogos ON jogos.id = conferencias.jogo_id
    WHERE jogos.usuario_id = ?
  `).bind(userId).first();

  if (!latest || !latest.concurso) {
    return null;
  }

  const rows = await env.DB.prepare(`
    SELECT conferencias.concurso,
           conferencias.acertos,
           conferencias.dezenas_jogadas,
           conferencias.dezenas_sorteadas,
           conferencias.dezenas_acertadas,
           COALESCE(conferencias.metodo, jogos.metodo, 'Painel') AS metodo,
           jogos.id AS jogo_id,
           jogos.status
    FROM conferencias
    JOIN jogos ON jogos.id = conferencias.jogo_id
    WHERE jogos.usuario_id = ? AND conferencias.concurso = ?
    ORDER BY conferencias.acertos DESC, jogos.id ASC
  `).bind(userId, latest.concurso).all();

  if (!rows.results.length) {
    return null;
  }

  const total = rows.results.reduce((acc, row) => acc + Number(row.acertos || 0), 0);
  const media = total / rows.results.length;
  const best = rows.results[0];
  const origemStats = new Map();

  for (const row of rows.results) {
    const metodo = row.metodo || "Painel";
    const current = origemStats.get(metodo) || { metodo, total: 0, jogos: 0, max: 0 };
    current.total += Number(row.acertos || 0);
    current.jogos += 1;
    current.max = Math.max(current.max, Number(row.acertos || 0));
    origemStats.set(metodo, current);
  }

  const melhorOrigem = [...origemStats.values()]
    .map((item) => ({ ...item, media: item.total / item.jogos }))
    .sort((a, b) => b.media - a.media || b.max - a.max || a.metodo.localeCompare(b.metodo))[0];

  return {
    concurso: latest.concurso,
    total_jogos: rows.results.length,
    media_acertos: Number(media.toFixed(2)),
    melhor_jogo: {
      jogo_id: best.jogo_id,
      metodo: best.metodo,
      acertos: best.acertos,
      dezenas_jogadas: best.dezenas_jogadas,
      dezenas_sorteadas: best.dezenas_sorteadas,
      dezenas_acertadas: best.dezenas_acertadas,
      status: best.status
    },
    melhor_origem: melhorOrigem
      ? {
          metodo: melhorOrigem.metodo,
          media_acertos: Number(melhorOrigem.media.toFixed(2)),
          melhor_acerto: melhorOrigem.max,
          total_jogos: melhorOrigem.jogos
        }
      : null
  };
}

function calcularCombinacaoRecomendada(ranking, pesos, totalJogos = 10) {
  const maxOrigens = 5;
  const maxPorOrigem = Math.ceil(totalJogos * 0.4);
  const candidatosBase = ranking.filter((item) => !item.penalizado && item.jogos >= 5);
  const candidatos = (candidatosBase.length ? candidatosBase : ranking)
    .slice(0, maxOrigens)
    .map((item) => {
      const peso = Number(pesos[item.origem] || 0);
      const bonusTendencia = item.tendencia > 0 ? Math.min(item.tendencia * 0.04, 0.08) : 0;
      const bonusEstabilidade = item.estabilidade <= 1.2 ? 0.06 : item.estabilidade <= 1.6 ? 0.03 : 0;
      const penalizacao = item.penalizado ? 0.45 : 1;
      const prioridade = Math.max(0.03, (peso + bonusTendencia + bonusEstabilidade) * penalizacao);

      return { item, prioridade };
    });

  if (!candidatos.length) {
    return null;
  }

  const totalPrioridade = candidatos.reduce((acc, atual) => acc + atual.prioridade, 0) || 1;
  let alocados = candidatos.map((atual) => {
    const bruto = (atual.prioridade / totalPrioridade) * totalJogos;
    return {
      item: atual.item,
      quantidade: Math.max(1, Math.min(maxPorOrigem, Math.floor(bruto))),
      resto: bruto - Math.floor(bruto)
    };
  });

  while (alocados.reduce((acc, atual) => acc + atual.quantidade, 0) > totalJogos) {
    const alvo = alocados
      .filter((atual) => atual.quantidade > 1)
      .sort((a, b) => a.resto - b.resto || a.item.score - b.item.score)[0];
    if (!alvo) break;
    alvo.quantidade -= 1;
  }

  while (alocados.reduce((acc, atual) => acc + atual.quantidade, 0) < totalJogos) {
    const alvo = alocados
      .filter((atual) => atual.quantidade < maxPorOrigem)
      .sort((a, b) => b.resto - a.resto || b.item.score - a.item.score)[0] || alocados[0];
    alvo.quantidade += 1;
  }

  alocados = alocados
    .filter((atual) => atual.quantidade > 0)
    .sort((a, b) => b.quantidade - a.quantidade || b.item.score - a.item.score);

  const itens = alocados.map(({ item, quantidade }) => {
    const motivos = [];
    if (item.freq_13_mais >= 1) motivos.push(`${item.freq_13_mais}% com 13+`);
    if (item.freq_12_mais >= 18) motivos.push(`${item.freq_12_mais}% com 12+`);
    if (item.freq_11_mais >= 10) motivos.push(`${item.freq_11_mais}% com 11+`);
    if (item.estabilidade <= 1.5) motivos.push(`estabilidade ${item.estabilidade}`);
    if (item.tendencia > 0.25) motivos.push(`tendencia ${item.tendencia_label}`);
    if (item.penalizado) motivos.push("abaixo do minimo util de 11+");

    return {
      origem: item.origem,
      quantidade,
      peso: Number((pesos[item.origem] || 0).toFixed(4)),
      media_acertos: item.media_acertos,
      alvo_minimo: "11+",
      faixa_ideal: "13-14",
      estabilidade: item.estabilidade,
      tendencia: item.tendencia,
      tendencia_label: item.tendencia_label,
      confianca: item.confianca,
      justificativa: motivos.slice(0, 3).join(" · ") || "mantido para diversificar os perfis"
    };
  });

  return {
    total_jogos: itens.reduce((acc, item) => acc + item.quantidade, 0),
    max_origens: maxOrigens,
    regra: "Distribuicao com limite de concentracao, minimo util 11+ e prioridade para perfis com sinais de 13+.",
    itens
  };
}

async function aprendizadoOrigens(userId, env) {
  const janelaConcursos = 60;
  const meiaVidaConcursos = 18;
  const minimoConfiavel = 5;
  const latest = await env.DB.prepare(`
    SELECT MAX(conferencias.concurso) AS concurso
    FROM conferencias
    JOIN jogos ON jogos.id = conferencias.jogo_id
    WHERE jogos.usuario_id = ?
  `).bind(userId).first();

  if (!latest || !latest.concurso) {
    return null;
  }

  const concursoMinimo = Math.max(1, Number(latest.concurso) - janelaConcursos + 1);
  const result = await env.DB.prepare(`
    SELECT conferencias.concurso,
           conferencias.acertos,
           conferencias.dezenas_jogadas,
           COALESCE(conferencias.metodo, jogos.metodo, 'Painel') AS metodo
    FROM conferencias
    JOIN jogos ON jogos.id = conferencias.jogo_id
    WHERE jogos.usuario_id = ? AND conferencias.concurso >= ?
    ORDER BY conferencias.concurso DESC, conferencias.id DESC
    LIMIT 500
  `).bind(userId, concursoMinimo).all();

  if (!result.results.length) {
    return null;
  }

  const grupos = new Map();

  for (const row of result.results) {
    const origem = origemMetodo(row.metodo);
    const grupo = grupos.get(origem) || {
      origem,
      acertos: [],
      soma: [],
      pares: [],
      impares: [],
      moldura: [],
      miolo: [],
      pesos: [],
      recentes: [],
      anteriores: []
    };
    const acertos = Number(row.acertos || 0);
    const distancia = Math.max(0, Number(latest.concurso) - Number(row.concurso || latest.concurso));
    const pesoTemporal = Math.pow(0.5, distancia / meiaVidaConcursos);
    grupo.acertos.push(acertos);
    grupo.pesos.push(pesoTemporal);
    if (distancia < Math.ceil(janelaConcursos / 2)) grupo.recentes.push(acertos);
    else grupo.anteriores.push(acertos);

    if (row.dezenas_jogadas) {
      try {
        const stats = statsDezenasTexto(row.dezenas_jogadas);
        grupo.soma.push({ valor: stats.soma, peso: pesoTemporal });
        grupo.pares.push({ valor: stats.pares, peso: pesoTemporal });
        grupo.impares.push({ valor: stats.impares, peso: pesoTemporal });
        grupo.moldura.push({ valor: stats.moldura, peso: pesoTemporal });
        grupo.miolo.push({ valor: stats.miolo, peso: pesoTemporal });
      } catch {}
    }

    grupos.set(origem, grupo);
  }

  const mediaPonderada = (valores, pesos) => {
    const totalPeso = pesos.reduce((acc, peso) => acc + peso, 0) || 1;
    return valores.reduce((acc, valor, idx) => acc + (valor * pesos[idx]), 0) / totalPeso;
  };
  const mediaPonderadaObjetos = (itens) => {
    const totalPeso = itens.reduce((acc, item) => acc + item.peso, 0) || 1;
    return itens.reduce((acc, item) => acc + (item.valor * item.peso), 0) / totalPeso;
  };
  const desvioPonderado = (valores, pesos, m) => {
    const totalPeso = pesos.reduce((acc, peso) => acc + peso, 0) || 1;
    return Math.sqrt(valores.reduce((acc, valor, idx) => acc + (((valor - m) ** 2) * pesos[idx]), 0) / totalPeso);
  };

  const ranking = [...grupos.values()].map((grupo) => {
    const jogos = grupo.acertos.length;
    const mediaAcertos = mediaPonderada(grupo.acertos, grupo.pesos);
    const desvio = desvioPonderado(grupo.acertos, grupo.pesos, mediaAcertos);
    const pesoTotal = grupo.pesos.reduce((acc, peso) => acc + peso, 0) || 1;
    const freq11 = grupo.acertos.reduce((acc, valor, idx) => acc + (valor >= 11 ? grupo.pesos[idx] : 0), 0) / pesoTotal;
    const freq12 = grupo.acertos.reduce((acc, valor, idx) => acc + (valor >= 12 ? grupo.pesos[idx] : 0), 0) / pesoTotal;
    const freq13 = grupo.acertos.reduce((acc, valor, idx) => acc + (valor >= 13 ? grupo.pesos[idx] : 0), 0) / pesoTotal;
    const freq14 = grupo.acertos.reduce((acc, valor, idx) => acc + (valor >= 14 ? grupo.pesos[idx] : 0), 0) / pesoTotal;
    const mediaRecente = grupo.recentes.length ? media(grupo.recentes) : mediaAcertos;
    const mediaAnterior = grupo.anteriores.length ? media(grupo.anteriores) : mediaRecente;
    const tendencia = mediaRecente - mediaAnterior;
    const penalizacao11 = freq11 < 0.18 ? (0.18 - freq11) * 5.0 : 0;
    const bonusIdeal = (freq13 * 6.0) + (freq14 * 10.0);
    const penalizacaoAmostra = jogos < minimoConfiavel ? (minimoConfiavel - jogos) * 0.18 : 0;
    const scoreBase = (freq11 * 4.0) + (freq12 * 5.5) + bonusIdeal - (desvio * 0.25) + (tendencia * 0.55);
    const score = scoreBase - penalizacao11 - penalizacaoAmostra;
    const tendenciaLabel = tendencia > 0.25 ? "subindo" : tendencia < -0.25 ? "caindo" : "estavel";

    return {
      origem: grupo.origem,
      jogos,
      media_acertos: Number(mediaAcertos.toFixed(2)),
      freq_11_mais: Number((freq11 * 100).toFixed(1)),
      freq_12_mais: Number((freq12 * 100).toFixed(1)),
      freq_13_mais: Number((freq13 * 100).toFixed(1)),
      freq_14_mais: Number((freq14 * 100).toFixed(1)),
      alvo_minimo: "11+",
      faixa_ideal: "13-14",
      estabilidade: Number(desvio.toFixed(2)),
      soma_media: grupo.soma.length ? Number(mediaPonderadaObjetos(grupo.soma).toFixed(1)) : null,
      pares_media: grupo.pares.length ? Number(mediaPonderadaObjetos(grupo.pares).toFixed(1)) : null,
      impares_media: grupo.impares.length ? Number(mediaPonderadaObjetos(grupo.impares).toFixed(1)) : null,
      moldura_media: grupo.moldura.length ? Number(mediaPonderadaObjetos(grupo.moldura).toFixed(1)) : null,
      miolo_media: grupo.miolo.length ? Number(mediaPonderadaObjetos(grupo.miolo).toFixed(1)) : null,
      tendencia: Number(tendencia.toFixed(2)),
      tendencia_label: tendenciaLabel,
      confianca: jogos >= 20 ? "alta" : jogos >= minimoConfiavel ? "media" : "baixa",
      penalizado: freq11 < 0.18 || jogos < minimoConfiavel,
      score: Number(score.toFixed(4))
    };
  }).sort((a, b) => b.score - a.score || b.media_acertos - a.media_acertos || a.estabilidade - b.estabilidade);

  const scoresPositivos = ranking.map((item) => {
    const base = Math.max(item.score, 0.08);
    const fatorConfianca = item.confianca === "alta" ? 1 : item.confianca === "media" ? 0.75 : 0.35;
    const fatorPenalizacao = item.penalizado ? 0.45 : 1;
    return base * fatorConfianca * fatorPenalizacao;
  });
  const totalScores = scoresPositivos.reduce((acc, valor) => acc + valor, 0) || 1;
  const pesos = Object.fromEntries(ranking.map((item, idx) => [
    item.origem,
    Number((scoresPositivos[idx] / totalScores).toFixed(4))
  ]));
  const confiaveis = ranking.filter((item) => item.jogos >= minimoConfiavel);
  const baseConfiavel = confiaveis.length ? confiaveis : ranking;
  const maisEstavel = baseConfiavel.slice().sort((a, b) => a.estabilidade - b.estabilidade || b.media_acertos - a.media_acertos)[0];
  const melhorMedia = baseConfiavel.slice().sort((a, b) => b.freq_13_mais - a.freq_13_mais || b.freq_12_mais - a.freq_12_mais || b.freq_11_mais - a.freq_11_mais)[0];
  const priorizar = baseConfiavel.slice().sort((a, b) => b.score - a.score || b.tendencia - a.tendencia)[0];
  const evitar = ranking.slice().reverse().find((item) => item.penalizado) || ranking[ranking.length - 1];
  const recomendacaoPerfis = [priorizar?.origem, maisEstavel?.origem, melhorMedia?.origem]
    .filter(Boolean)
    .filter((origem, idx, arr) => arr.indexOf(origem) === idx);
  const combinacaoRecomendada = calcularCombinacaoRecomendada(ranking, pesos, 10);

  return {
    janela_concursos: janelaConcursos,
    ultimo_concurso: latest.concurso,
    meia_vida_concursos: meiaVidaConcursos,
    minimo_confiavel: minimoConfiavel,
    alvo_minimo: "11+",
    faixa_ideal: "13-14",
    total_conferencias: result.results.length,
    ranking,
    pesos,
    mais_estavel: maisEstavel ? maisEstavel.origem : null,
    melhor_media: melhorMedia ? melhorMedia.origem : null,
    sugestao_priorizar: priorizar ? priorizar.origem : null,
    evitar: evitar ? evitar.origem : null,
    recomendacao_perfis: recomendacaoPerfis,
    combinacao_recomendada: combinacaoRecomendada
  };
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
  await env.DB.prepare(`
    UPDATE jogos
    SET status = 'cancelado', atualizado_em = CURRENT_TIMESTAMP
    WHERE id IN (${placeholders})
  `).bind(...ids).run();
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
    SELECT id, dezenas, dezenas_texto, metodo
    FROM jogos
    WHERE usuario_id = ? AND status IN ('salvo', 'jogado', 'conferido')
    ORDER BY datetime(criado_em) DESC
    LIMIT 200
  `).bind(user.id).all();
  let novas = 0;
  let atualizadas = 0;
  const resumo = [];

  for (const jogo of result.results) {
      const dezenasJogo = JSON.parse(jogo.dezenas);
      const dezenas = new Set(dezenasJogo);

      for (const rodada of rodadas) {
      const acertadas = rodada.dezenas.filter((dezena) => dezenas.has(dezena)).sort((a, b) => a - b);
      const acertos = acertadas.length;
      const dezenasSorteadas = rodada.dezenas_texto;
      const insert = await env.DB.prepare(`
        INSERT OR IGNORE INTO conferencias (
          jogo_id, concurso, dezenas_jogadas, dezenas_sorteadas,
          dezenas_acertadas, acertos, metodo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `).bind(
        jogo.id,
        rodada.concurso,
        jogo.dezenas_texto || dezenasTexto(dezenasJogo),
        dezenasSorteadas,
        dezenasTexto(acertadas),
        acertos,
        jogo.metodo
      ).run();

      if (insert.meta.changes) {
        novas += 1;
      } else {
        await env.DB.prepare(`
          UPDATE conferencias
          SET dezenas_jogadas = ?,
              dezenas_sorteadas = ?,
              dezenas_acertadas = ?,
              acertos = ?,
              metodo = ?,
              conferido_em = CURRENT_TIMESTAMP
          WHERE jogo_id = ? AND concurso = ?
        `).bind(
          jogo.dezenas_texto || dezenasTexto(dezenasJogo),
          dezenasSorteadas,
          dezenasTexto(acertadas),
          acertos,
          jogo.metodo,
          jogo.id,
          rodada.concurso
        ).run();
        atualizadas += 1;
      }

      resumo.push({
        jogo_id: jogo.id,
        concurso: rodada.concurso,
        dezenas_jogadas: jogo.dezenas_texto || dezenasTexto(dezenasJogo),
        dezenas_sorteadas: dezenasSorteadas,
        dezenas_acertadas: dezenasTexto(acertadas),
        metodo: jogo.metodo,
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

async function salvarConferencia(env, jogo, resultado) {
  const dezenasJogo = JSON.parse(jogo.dezenas);
  const dezenas = new Set(dezenasJogo);
  const resultadoDezenas = Array.isArray(resultado.dezenas)
    ? resultado.dezenas
    : JSON.parse(resultado.dezenas);
  const dezenasSorteadas = resultado.dezenas_texto || dezenasTexto(resultadoDezenas);
  const acertadas = resultadoDezenas.filter((dezena) => dezenas.has(dezena)).sort((a, b) => a - b);
  const acertos = acertadas.length;
  const dezenasJogadas = jogo.dezenas_texto || dezenasTexto(dezenasJogo);
  const dezenasAcertadas = dezenasTexto(acertadas);
  const insert = await env.DB.prepare(`
    INSERT OR IGNORE INTO conferencias (
      jogo_id, concurso, dezenas_jogadas, dezenas_sorteadas,
      dezenas_acertadas, acertos, metodo
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).bind(
    jogo.id,
    resultado.concurso,
    dezenasJogadas,
    dezenasSorteadas,
    dezenasAcertadas,
    acertos,
    jogo.metodo
  ).run();

  if (!insert.meta.changes) {
    await env.DB.prepare(`
      UPDATE conferencias
      SET dezenas_jogadas = ?,
          dezenas_sorteadas = ?,
          dezenas_acertadas = ?,
          acertos = ?,
          metodo = ?,
          conferido_em = CURRENT_TIMESTAMP
      WHERE jogo_id = ? AND concurso = ?
    `).bind(
      dezenasJogadas,
      dezenasSorteadas,
      dezenasAcertadas,
      acertos,
      jogo.metodo,
      jogo.id,
      resultado.concurso
    ).run();
  }

  return {
    nova: Boolean(insert.meta.changes),
    jogo_id: jogo.id,
    concurso: resultado.concurso,
    dezenas_jogadas: dezenasJogadas,
    dezenas_sorteadas: dezenasSorteadas,
    dezenas_acertadas: dezenasAcertadas,
    metodo: jogo.metodo,
    acertos
  };
}

async function conferirPendencias(env, userId = null) {
  await seedInitialResults(env);
  const userFilter = userId ? "AND usuario_id = ?" : "";
  const pageSize = 500;
  let lastId = 0;
  let novas = 0;
  let atualizadas = 0;
  let jogosAvaliados = 0;
  const resumo = [];

  while (true) {
    const params = userId ? [userId, lastId, pageSize] : [lastId, pageSize];
    const jogosResult = await env.DB.prepare(`
      SELECT id, usuario_id, concurso, metodo, dezenas, dezenas_texto, manter_salvo, descartar_apos_rodadas
      FROM jogos
      WHERE status IN ('salvo', 'jogado', 'conferido')
        ${userFilter}
        AND id > ?
      ORDER BY id ASC
      LIMIT ?
    `).bind(...params).all();

    if (!jogosResult.results.length) {
      break;
    }

    for (const jogo of jogosResult.results) {
      lastId = Math.max(lastId, jogo.id);
      jogosAvaliados += 1;
      const conferidas = await env.DB.prepare(`
        SELECT COUNT(*) AS total
        FROM conferencias
        WHERE jogo_id = ?
      `).bind(jogo.id).first();
      const limite = jogo.manter_salvo ? 50 : Number(jogo.descartar_apos_rodadas || 2);
      const restantes = Math.max(0, limite - Number(conferidas.total || 0));

      if (!restantes) {
        continue;
      }

      const resultados = await env.DB.prepare(`
        SELECT resultados.concurso, resultados.data_sorteio, resultados.dezenas, resultados.dezenas_texto
        FROM resultados
        LEFT JOIN conferencias
          ON conferencias.jogo_id = ? AND conferencias.concurso = resultados.concurso
        WHERE conferencias.id IS NULL
          AND (? IS NULL OR resultados.concurso >= ?)
        ORDER BY resultados.concurso ASC
        LIMIT ?
      `).bind(jogo.id, jogo.concurso, jogo.concurso, restantes).all();

      for (const resultado of resultados.results) {
        const conferencia = await salvarConferencia(env, jogo, resultado);

        if (conferencia.nova) {
          novas += 1;
        } else {
          atualizadas += 1;
        }

        resumo.push(conferencia);
      }
    }

    if (jogosResult.results.length < pageSize) {
      break;
    }
  }

  if (resumo.length) {
    const ids = [...new Set(resumo.map((item) => item.jogo_id))];
    const placeholders = ids.map(() => "?").join(",");
    await env.DB.prepare(`
      UPDATE jogos
      SET status = 'conferido', atualizado_em = CURRENT_TIMESTAMP
      WHERE id IN (${placeholders})
    `).bind(...ids).run();
  }

  const descartados = await cleanupExpiredGames(env, userId);

  return {
    ok: true,
    jogos_avaliados: jogosAvaliados,
    jogos_conferidos: new Set(resumo.map((item) => item.jogo_id)).size,
    conferencias_novas: novas,
    conferencias_atualizadas: atualizadas,
    jogos_descartados: descartados,
    resumo
  };
}

async function conferirResultadoParaJogos(env, resultado) {
  const jogos = await env.DB.prepare(`
    SELECT jogos.id, jogos.metodo, jogos.dezenas, jogos.dezenas_texto
    FROM jogos
    LEFT JOIN conferencias
      ON conferencias.jogo_id = jogos.id AND conferencias.concurso = ?
    WHERE jogos.status IN ('salvo', 'jogado', 'conferido')
      AND conferencias.id IS NULL
      AND (jogos.concurso IS NULL OR jogos.concurso <= ?)
  `).bind(resultado.concurso, resultado.concurso).all();
  let conferidos = 0;

  for (const jogo of jogos.results) {
    await salvarConferencia(env, jogo, resultado);
    conferidos += 1;
  }

  if (conferidos) {
    await env.DB.prepare(`
      UPDATE jogos
      SET status = 'conferido', atualizado_em = CURRENT_TIMESTAMP
      WHERE status IN ('salvo', 'jogado', 'conferido')
        AND (concurso IS NULL OR concurso <= ?)
    `).bind(resultado.concurso).run();
    await cleanupExpiredGames(env);
  }

  return conferidos;
}

async function runAutoCycle(env) {
  const started = await env.DB.prepare(
    "INSERT INTO execucoes_ciclo (status) VALUES ('rodando')"
  ).run();
  const cycleId = started.meta.last_row_id;

  try {
  const sessoesExpiradas = await cleanupExpiredSessions(env);
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

  const pendentes = await conferirPendencias(env);
  conferencias += pendentes.conferencias_novas + pendentes.conferencias_atualizadas;

  const currentLatest = await latestResult(env);
  const proximoConcurso = currentLatest ? currentLatest.concurso + 1 : 1;
  const jogosGerados = await generateNextContestGames(env, proximoConcurso);

  const payload = {
    ok: true,
    novos_concursos: novos.map((resultado) => resultado.concurso),
    conferencias,
    jogos_descartados: pendentes.jogos_descartados,
    sessoes_expiradas: sessoesExpiradas,
    proximo_concurso: proximoConcurso,
    jogos_gerados: jogosGerados.length
  };

  await env.DB.prepare(`
    UPDATE execucoes_ciclo
    SET finalizado_em = CURRENT_TIMESTAMP,
        status = 'ok',
        novos_concursos = ?,
        conferencias = ?,
        jogos_descartados = ?,
        sessoes_expiradas = ?,
        proximo_concurso = ?,
        jogos_gerados = ?
    WHERE id = ?
  `).bind(
    JSON.stringify(payload.novos_concursos),
    payload.conferencias,
    payload.jogos_descartados,
    payload.sessoes_expiradas,
    payload.proximo_concurso,
    payload.jogos_gerados,
    cycleId
  ).run();

  return payload;
  } catch (err) {
    await env.DB.prepare(`
      UPDATE execucoes_ciclo
      SET finalizado_em = CURRENT_TIMESTAMP,
          status = 'erro',
          erro = ?
      WHERE id = ?
    `).bind(String(err.stack || err.message || err), cycleId).run();
    throw err;
  }
}

async function systemStatus(env) {
  const latest = await latestResult(env);
  const proximoConcurso = latest ? latest.concurso + 1 : 1;
  await generateNextContestGames(env, proximoConcurso);
  const stats = await resultStats(env, 50);
  const frequencia = await numberStats(env);
  const ultimoCiclo = await latestCycle(env);
  const generated = await env.DB.prepare(`
    SELECT concurso, metodo, dezenas, dezenas_texto, soma, pares, impares
    FROM jogos_sistema
    WHERE concurso = ?
    ORDER BY metodo
  `).bind(proximoConcurso).all();
  const conferidor = latest
    ? await env.DB.prepare(`
        SELECT concurso, metodo, dezenas, dezenas_texto, soma, pares, impares
        FROM jogos_sistema
        WHERE concurso = ?
        ORDER BY metodo
      `).bind(latest.concurso).all()
    : { results: [] };

  return json({
    ok: true,
    total_concursos: stats.total_concursos,
    ultimo_resultado: latest,
    proximo_concurso: proximoConcurso,
    resultados_recentes: stats.resultados_recentes,
    frequencia_dezenas: frequencia,
    ultimo_ciclo: ultimoCiclo,
    jogos_gerados: generated.results.map((jogo) => ({
      ...jogo,
      dezenas: JSON.parse(jogo.dezenas)
    })),
    jogos_conferidor: conferidor.results.map((jogo) => ({
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

  if (path === "/api/resultados/status" && method === "GET") {
    const stats = await resultStats(env, 50);
    return json({
      ok: true,
      ...stats,
      frequencia_dezenas: await numberStats(env)
    });
  }

  if (path === "/api/ciclo/status" && method === "GET") {
    return json({ ok: true, ultimo_ciclo: await latestCycle(env) });
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

  if (path === "/api/jogos/conferir-pendentes" && method === "POST") {
    return json(await conferirPendencias(env, user.id));
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

function assetRequest(request, url, pathname) {
  const assetUrl = new URL(request.url);
  assetUrl.pathname = pathname;
  assetUrl.search = url.search;

  return new Request(assetUrl.toString(), {
    method: "GET",
    headers: request.headers
  });
}

const PANEL_ROUTES = {
  "/": "/index.html",
  "/index": "/index.html",
  "/painel": "/painel_jogos_v2.html",
  "/painel.html": "/painel_jogos_v2.html",
  "/painel_avancado": "/painel_jogos_v2.html",
  "/painel_avancado.html": "/painel_jogos_v2.html",
  "/painel_jogos": "/painel_jogos_v2.html",
  "/painel_jogos.html": "/painel_jogos_v2.html",
  "/painel_jogos_v2": "/painel_jogos_v2.html",
  "/painel_jogos_v2.html": "/painel_jogos_v2.html",
  "/painel_mobile": "/painel_jogos_v2.html",
  "/painel_mobile.html": "/painel_jogos_v2.html",
  "/painel-educativo": "/painel-educativo.html",
  "/painel-exportacao": "/painel-exportacao.html",
  "/usuario": "/usuario.html"
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    try {
      if (url.pathname.startsWith("/api/")) {
        return await handleApi(request, env, url);
      }

      if (PANEL_ROUTES[url.pathname]) {
        return env.ASSETS.fetch(assetRequest(request, url, PANEL_ROUTES[url.pathname]));
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
