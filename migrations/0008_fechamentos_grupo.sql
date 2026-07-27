CREATE TABLE IF NOT EXISTS fechamentos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario_id INTEGER NOT NULL,
  concurso INTEGER NOT NULL,
  tamanho_grupo INTEGER NOT NULL,
  dezenas TEXT NOT NULL,
  dezenas_texto TEXT NOT NULL,
  jogos TEXT NOT NULL,
  quantidade_jogos INTEGER NOT NULL,
  criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fechamento_conferencias (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fechamento_id INTEGER NOT NULL,
  concurso INTEGER NOT NULL,
  dezenas_sorteadas TEXT NOT NULL,
  dezenas_acertadas_grupo TEXT NOT NULL,
  acertos_grupo INTEGER NOT NULL,
  melhor_acerto_jogos INTEGER NOT NULL,
  garantia_14_ativada INTEGER NOT NULL DEFAULT 0,
  conferido_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (fechamento_id) REFERENCES fechamentos(id) ON DELETE CASCADE,
  UNIQUE (fechamento_id, concurso)
);

CREATE INDEX IF NOT EXISTS idx_fechamentos_usuario
  ON fechamentos(usuario_id, concurso DESC);

CREATE INDEX IF NOT EXISTS idx_fechamento_conferencias_fechamento
  ON fechamento_conferencias(fechamento_id, concurso DESC);
