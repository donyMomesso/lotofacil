CREATE TABLE IF NOT EXISTS resultados (
  concurso INTEGER PRIMARY KEY,
  data_sorteio TEXT NOT NULL,
  dezenas TEXT NOT NULL,
  dezenas_texto TEXT NOT NULL,
  criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jogos_sistema (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  concurso INTEGER NOT NULL,
  metodo TEXT NOT NULL,
  dezenas TEXT NOT NULL,
  dezenas_texto TEXT NOT NULL,
  soma INTEGER NOT NULL,
  pares INTEGER NOT NULL,
  impares INTEGER NOT NULL,
  criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(concurso, metodo)
);

CREATE INDEX IF NOT EXISTS idx_jogos_sistema_concurso
ON jogos_sistema(concurso);
