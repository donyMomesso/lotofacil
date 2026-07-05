CREATE TABLE IF NOT EXISTS execucoes_ciclo (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  iniciado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finalizado_em TEXT,
  status TEXT NOT NULL DEFAULT 'rodando',
  novos_concursos TEXT NOT NULL DEFAULT '[]',
  conferencias INTEGER NOT NULL DEFAULT 0,
  jogos_descartados INTEGER NOT NULL DEFAULT 0,
  sessoes_expiradas INTEGER NOT NULL DEFAULT 0,
  proximo_concurso INTEGER,
  jogos_gerados INTEGER NOT NULL DEFAULT 0,
  erro TEXT
);

CREATE INDEX IF NOT EXISTS idx_execucoes_ciclo_iniciado
ON execucoes_ciclo(iniciado_em DESC);
