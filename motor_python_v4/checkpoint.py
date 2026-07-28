from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_core import build_report


def load_draws(path: str | Path) -> list[dict]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("resultados", payload.get("concursos", payload.get("draws", [])))
    if not isinstance(payload, list):
        raise ValueError("O histórico precisa ser uma lista ou conter resultados/concursos/draws.")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera checkpoint histórico educativo a cada 5 concursos.")
    parser.add_argument("historico")
    parser.add_argument("--saida", default="checkpoints/latest.json")
    parser.add_argument("--min-training", type=int, default=30)
    args = parser.parse_args()
    report = build_report(load_draws(args.historico), min_training=args.min_training)
    output = Path(args.saida)
    output.parent.mkdir(parents=True, exist_ok=True)
    existing = None
    if output.exists():
        try:
            existing = json.loads(output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = None
    old_index = (existing or {}).get("latest_checkpoint", {}).get("index") if isinstance((existing or {}).get("latest_checkpoint"), dict) else None
    new_index = (report.get("latest_checkpoint") or {}).get("index")
    if old_index == new_index and old_index is not None:
        print(json.dumps({"status": "sem_novo_bloco_de_5", "checkpoint_index": new_index}, ensure_ascii=False))
        return 0
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "brain_version": report["brain_version"],
        "evaluated_contests": report["evaluated_contests"],
        "completed_checkpoint_contests": report["completed_checkpoint_contests"],
        "pending_until_next_checkpoint": report["pending_until_next_checkpoint"],
        "report_hash": report["report_hash"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
