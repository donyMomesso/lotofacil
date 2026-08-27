CREATE TABLE IF NOT EXISTS jogos_sistema_conferencia (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  concurso INTEGER NOT NULL,
  metodo TEXT NOT NULL,
  dezenas_jogo TEXT NOT NULL,
  dezenas_sorteadas TEXT NOT NULL,
  acertos INTEGER NOT NULL,
  conferido_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(concurso, metodo)
);

CREATE INDEX IF NOT EXISTS idx_jsc_concurso
ON jogos_sistema_conferencia (concurso DESC);
