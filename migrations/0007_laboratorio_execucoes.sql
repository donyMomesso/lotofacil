CREATE TABLE IF NOT EXISTS laboratorio_execucoes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  concurso INTEGER NOT NULL UNIQUE,
  quantidade INTEGER NOT NULL,
  seed INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'aguardando_resultado',
  criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  conferido_em TEXT,
  resumo_json TEXT,
  estrategias_json TEXT,
  melhor_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_laboratorio_execucoes_status
ON laboratorio_execucoes(status, concurso);
