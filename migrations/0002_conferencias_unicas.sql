CREATE UNIQUE INDEX IF NOT EXISTS idx_conferencias_jogo_concurso
ON conferencias(jogo_id, concurso);
