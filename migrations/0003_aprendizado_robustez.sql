CREATE TABLE IF NOT EXISTS aprendizado_resumos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  modelo_chave TEXT NOT NULL,
  versao_modelo TEXT NOT NULL,
  amostras INTEGER NOT NULL,
  ultimo_concurso INTEGER NOT NULL,
  resumo_json TEXT NOT NULL,
  hash_resumo TEXT NOT NULL,
  atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(modelo_chave, versao_modelo, amostras, ultimo_concurso)
);

CREATE INDEX IF NOT EXISTS idx_aprendizado_resumos_versao
ON aprendizado_resumos (versao_modelo, atualizado_em DESC);
