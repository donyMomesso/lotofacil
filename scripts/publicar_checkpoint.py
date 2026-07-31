#!/usr/bin/env python3
"""
Pipeline completo do Cérebro Python:

  1) sincroniza CSV com a API da Caixa
  2) valida histórico (sem buracos/duplicados)
  3) exporta checkpoint operacional com hash
  4) espelha em motor_python_v4/checkpoints/operacional.json

Uso (na raiz do repo):
  python scripts/publicar_checkpoint.py
  python scripts/publicar_checkpoint.py --pular-sync   # se CSV já estiver ok

Depois:
  git add dados/resultados_lotofacil.csv dados/checkpoint_cerebro.json motor_python_v4/checkpoints/operacional.json
  git commit -m "chore: checkpoint operacional alinhado"
  git push origin main
  npx wrangler deploy
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS = BASE_DIR / "scripts"


def run(cmd: list[str]) -> int:
    print(">>", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=str(BASE_DIR))
    return int(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Publica checkpoint operacional 100%")
    parser.add_argument("--pular-sync", action="store_true")
    parser.add_argument("--pular-validacao", action="store_true")
    parser.add_argument("--max-novos", type=int, default=40)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    py = sys.executable

    if not args.pular_sync:
        rc = run([py, str(SCRIPTS / "sincronizar_historico.py"), "--max-novos", str(args.max_novos)])
        if rc != 0:
            print(json.dumps({"ok": False, "etapa": "sync", "erro": "falha ao sincronizar histórico"}, ensure_ascii=False))
            return rc

    if not args.pular_validacao:
        rc = run([py, str(SCRIPTS / "validar_historico.py"), str(BASE_DIR / "dados" / "resultados_lotofacil.csv")])
        if rc != 0:
            print(json.dumps({"ok": False, "etapa": "validacao", "erro": "histórico inválido"}, ensure_ascii=False))
            return rc

    export_cmd = [py, str(SCRIPTS / "exportar_checkpoint_cerebro.py")]
    if args.seed is not None:
        export_cmd.extend(["--seed", str(args.seed)])
    if args.pular_validacao:
        export_cmd.append("--pular-validacao")
    rc = run(export_cmd)
    if rc != 0:
        print(json.dumps({"ok": False, "etapa": "export", "erro": "falha ao exportar checkpoint"}, ensure_ascii=False))
        return rc

    espelho = BASE_DIR / "motor_python_v4" / "checkpoints" / "operacional.json"
    if not espelho.exists():
        print(json.dumps({"ok": False, "erro": f"espelho não gerado: {espelho}"}, ensure_ascii=False))
        return 1

    try:
        payload = json.loads(espelho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(json.dumps({"ok": False, "erro": f"JSON inválido no espelho: {exc}"}, ensure_ascii=False))
        return 1

    print(json.dumps({
        "ok": True,
        "etapa": "concluido",
        "ultimo_concurso": payload.get("ultimo_concurso"),
        "concurso_alvo": payload.get("concurso_alvo"),
        "cerebro_version": payload.get("cerebro_version"),
        "checkpoint_hash": payload.get("checkpoint_hash"),
        "espelho": str(espelho),
        "proximos_passos": [
            "git checkout main && git pull origin main",
            "git add dados/resultados_lotofacil.csv dados/checkpoint_cerebro.json motor_python_v4/checkpoints/operacional.json",
            'git commit -m "chore: checkpoint operacional alinhado"',
            "git push origin main",
            "npx wrangler deploy",
            "abrir https://loto.grupopappi.com.br/api/sistema/gate",
        ],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
