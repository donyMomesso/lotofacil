-- Rastreabilidade: provar no D1 qual cérebro/checkpoint gerou cada jogo do sistema.
ALTER TABLE jogos_sistema ADD COLUMN origem TEXT;
ALTER TABLE jogos_sistema ADD COLUMN cerebro_version TEXT;
ALTER TABLE jogos_sistema ADD COLUMN checkpoint_hash TEXT;
ALTER TABLE jogos_sistema ADD COLUMN audit_brain_version TEXT;
ALTER TABLE jogos_sistema ADD COLUMN source_of_truth TEXT;
ALTER TABLE jogos_sistema ADD COLUMN checkpoint_generated_at TEXT;

CREATE TABLE IF NOT EXISTS checkpoint_ingest (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  concurso INTEGER NOT NULL,
  origem TEXT NOT NULL,
  cerebro_version TEXT,
  checkpoint_hash TEXT,
  audit_brain_version TEXT,
  source_of_truth TEXT,
  checkpoint_generated_at TEXT,
  metodos_json TEXT,
  jogos_count INTEGER NOT NULL DEFAULT 0,
  ingestido_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_jogos_sistema_hash
ON jogos_sistema(checkpoint_hash);

CREATE INDEX IF NOT EXISTS idx_checkpoint_ingest_concurso
ON checkpoint_ingest(concurso DESC, ingestido_em DESC);
