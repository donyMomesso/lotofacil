CREATE TABLE IF NOT EXISTS aprendizado_campeoes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  versao_modelo TEXT NOT NULL,
  versao_governanca TEXT NOT NULL,
  modelo_chave TEXT NOT NULL,
  desde_concurso INTEGER NOT NULL,
  ultima_avaliacao_concurso INTEGER NOT NULL DEFAULT 0,
  atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(versao_modelo, versao_governanca)
);

CREATE TABLE IF NOT EXISTS aprendizado_decisoes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  versao_modelo TEXT NOT NULL,
  versao_governanca TEXT NOT NULL,
  concurso_ate INTEGER NOT NULL,
  campeao_atual TEXT NOT NULL,
  desafiante TEXT NOT NULL,
  decisao TEXT NOT NULL,
  promovido_modelo TEXT,
  decisao_json TEXT NOT NULL,
  hash_decisao TEXT NOT NULL,
  criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(versao_modelo, versao_governanca, concurso_ate, campeao_atual, desafiante)
);

CREATE INDEX IF NOT EXISTS idx_aprendizado_decisoes_concurso
ON aprendizado_decisoes (concurso_ate DESC, criado_em DESC);
