CREATE TABLE IF NOT EXISTS aprendizado_historico (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  concurso INTEGER NOT NULL,
  data_sorteio TEXT,
  modelo_chave TEXT NOT NULL,
  modelo_nome TEXT NOT NULL,
  versao_modelo TEXT NOT NULL,
  treino_ate INTEGER NOT NULL,
  quantidade_treino INTEGER NOT NULL,
  probabilidade_soma REAL NOT NULL,
  ranking_json TEXT NOT NULL,
  resultado_json TEXT NOT NULL,
  brier REAL NOT NULL,
  log_loss REAL NOT NULL,
  top15 INTEGER NOT NULL,
  top18 INTEGER NOT NULL,
  top19 INTEGER NOT NULL,
  top20 INTEGER NOT NULL,
  top21 INTEGER NOT NULL,
  hash_registro TEXT NOT NULL,
  criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(concurso, modelo_chave, versao_modelo)
);

CREATE INDEX IF NOT EXISTS idx_aprendizado_historico_concurso
ON aprendizado_historico (concurso DESC);
