#!/usr/bin/env python3
"""
Exporta o checkpoint operacional do Cérebro Python.

Pipeline:
  1) carrega histórico (CSV/JSON)
  2) valida (buracos, duplicados, dezenas) — se falhar, NÃO grava checkpoint
  3) gera checkpoint versionado com hash
  4) espelha em motor_python_v4/checkpoints/operacional.json

Uso:
  python scripts/validar_historico.py dados/resultados_lotofacil.csv
  python scripts/exportar_checkpoint_cerebro.py
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "motor_python_v4"))
sys.path.insert(0, str(BASE_DIR / "scripts"))

from cerebro import Cerebro  # noqa: E402
from engine import Concurso  # noqa: E402
from validar_historico import carregar as carregar_rows, validar  # noqa: E402


def carregar_historico_csv(caminho: Path) -> list[Concurso]:
    concursos: list[Concurso] = []
    with caminho.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            dezenas = [int(row[f"b{i:02d}"]) for i in range(1, 16)]
            concursos.append(Concurso.criar(int(row["concurso"]), dezenas, row.get("data")))
    return concursos


def carregar_historico(caminho: Path) -> list[Concurso]:
    if caminho.suffix.lower() == ".json":
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        if isinstance(dados, dict):
            dados = dados.get("resultados", dados.get("concursos", []))
        return [
            Concurso.criar(
                int(x["concurso"]),
                x["dezenas"] if not isinstance(x["dezenas"], str) else [
                    int(p) for p in x["dezenas"].replace("-", " ").split()
                ],
                x.get("data"),
            )
            for x in dados
        ]
    return carregar_historico_csv(caminho)


def main() -> int:
    parser = argparse.ArgumentParser(description="Exporta checkpoint do Cérebro Python")
    parser.add_argument(
        "--historico",
        default=str(BASE_DIR / "dados" / "resultados_lotofacil.csv"),
        help="CSV ou JSON com histórico real",
    )
    parser.add_argument(
        "--saida",
        default=str(BASE_DIR / "dados" / "checkpoint_cerebro.json"),
    )
    parser.add_argument(
        "--espelho",
        default=str(BASE_DIR / "motor_python_v4" / "checkpoints" / "operacional.json"),
        help="Cópia para assets / bridge do Worker",
    )
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--concurso-alvo", type=int, default=None)
    parser.add_argument("--fechamento", action="store_true")
    parser.add_argument("--base", type=int, default=18)
    parser.add_argument("--jogos", type=int, default=30)
    parser.add_argument(
        "--pular-validacao",
        action="store_true",
        help="NÃO recomendado — só para debug",
    )
    args = parser.parse_args()

    historico_path = Path(args.historico)
    if not historico_path.exists():
        print(json.dumps({"ok": False, "erro": f"Histórico não encontrado: {historico_path}"}, ensure_ascii=False))
        return 1

    if not args.pular_validacao:
        try:
            rows = carregar_rows(historico_path)
            rel = validar(rows)
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"ok": False, "erro": f"Falha na validação: {exc}"}, ensure_ascii=False))
            return 1
        if not rel["ok"]:
            print(json.dumps({"ok": False, "erro": "Histórico inválido — checkpoint NÃO gerado", "validacao": rel}, ensure_ascii=False, indent=2))
            return 1

    historico = carregar_historico(historico_path)
    if not historico:
        print(json.dumps({"ok": False, "erro": "Histórico vazio"}, ensure_ascii=False))
        return 1

    cerebro = Cerebro(historico, seed=args.seed or 20260728)
    payload = cerebro.salvar_checkpoint(
        args.saida,
        concurso_alvo=args.concurso_alvo,
        seed=args.seed,
        incluir_fechamento=args.fechamento,
        tamanho_base=args.base,
        quantidade_fechamento=args.jogos,
    )

    if not payload.get("checkpoint_hash") or not payload.get("cerebro_version"):
        print(json.dumps({"ok": False, "erro": "Checkpoint sem hash ou versão — abortado"}, ensure_ascii=False))
        return 1

    espelho = Path(args.espelho)
    espelho.parent.mkdir(parents=True, exist_ok=True)
    espelho.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    resumo = {
        "ok": True,
        "cerebro_version": payload["cerebro_version"],
        "ultimo_concurso": payload["ultimo_concurso"],
        "concurso_alvo": payload["concurso_alvo"],
        "total_concursos": payload["total_concursos"],
        "metodos": list(payload["jogos_estudo"].keys()),
        "checkpoint_hash": payload["checkpoint_hash"],
        "saida": str(args.saida),
        "espelho": str(espelho),
        "validacao": "ok" if not args.pular_validacao else "pulada",
    }
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
