#!/usr/bin/env python3
"""
Valida histórico de Lotofácil (CSV ou JSON) antes do checkpoint Python.

Regras:
  - concurso inteiro > 0
  - exatamente 15 dezenas únicas em 1..25
  - sem duplicar concurso
  - sequência sem buracos (min..max contínuo)
  - se --exigir-contiguo: lista ordenada sem gaps

Uso:
  python scripts/validar_historico.py dados/resultados_lotofacil.csv
  python scripts/validar_historico.py --json dados/historico_d1.json

Exit 0 se ok; exit 1 se inválido (não gera checkpoint em cima de lixo).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def parse_dezenas(raw) -> list[int]:
    if isinstance(raw, list):
        return [int(x) for x in raw]
    if isinstance(raw, str):
        parts = raw.replace("-", " ").replace(",", " ").split()
        return [int(p) for p in parts if p.strip()]
    raise ValueError("dezenas inválidas")


def carregar(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("resultados") or data.get("concursos") or []
        rows = []
        for x in data:
            rows.append(
                {
                    "concurso": int(x["concurso"]),
                    "data": str(x.get("data") or x.get("data_sorteio") or ""),
                    "dezenas": parse_dezenas(x["dezenas"]),
                }
            )
        return rows

    rows = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for row in reader:
            if "b01" in fieldnames or any(k.startswith("b") for k in fieldnames):
                dezenas = [int(row[f"b{i:02d}"]) for i in range(1, 16)]
            else:
                dezenas = parse_dezenas(row.get("dezenas") or row.get("dezenas_texto") or "")
            rows.append(
                {
                    "concurso": int(row["concurso"]),
                    "data": str(row.get("data") or row.get("data_sorteio") or ""),
                    "dezenas": dezenas,
                }
            )
    return rows


def validar(rows: list[dict]) -> dict:
    erros: list[str] = []
    avisos: list[str] = []

    if not rows:
        return {"ok": False, "erros": ["histórico vazio"], "avisos": [], "total": 0}

    by_conc: dict[int, list[dict]] = {}
    for r in rows:
        c = r["concurso"]
        by_conc.setdefault(c, []).append(r)

    dups = sorted(c for c, lst in by_conc.items() if len(lst) > 1)
    if dups:
        erros.append(f"concursos duplicados: {dups[:20]}{'…' if len(dups) > 20 else ''}")

    for r in rows:
        c = r["concurso"]
        d = r["dezenas"]
        if c <= 0:
            erros.append(f"concurso inválido: {c}")
        if len(d) != 15:
            erros.append(f"#{c}: esperado 15 dezenas, veio {len(d)}")
            continue
        if len(set(d)) != 15:
            erros.append(f"#{c}: dezenas repetidas")
        if any(x < 1 or x > 25 for x in d):
            erros.append(f"#{c}: dezena fora de 1..25")

    concursos = sorted(by_conc.keys())
    if concursos:
        minimo, maximo = concursos[0], concursos[-1]
        esperado = set(range(minimo, maximo + 1))
        faltando = sorted(esperado - set(concursos))
        if faltando:
            erros.append(
                f"buracos na sequência {minimo}..{maximo}: "
                f"{faltando[:30]}{'…' if len(faltando) > 30 else ''} "
                f"({len(faltando)} ausentes)"
            )

    # inconsistência: mesmo concurso com dezenas diferentes
    for c, lst in by_conc.items():
        if len(lst) < 2:
            continue
        signatures = {tuple(sorted(x["dezenas"])) for x in lst}
        if len(signatures) > 1:
            erros.append(f"#{c}: registros duplicados com dezenas diferentes")

    return {
        "ok": len(erros) == 0,
        "erros": erros,
        "avisos": avisos,
        "total": len(rows),
        "unicos": len(by_conc),
        "min_concurso": concursos[0] if concursos else None,
        "max_concurso": concursos[-1] if concursos else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida histórico Lotofácil")
    parser.add_argument("arquivo", nargs="?", default="dados/resultados_lotofacil.csv")
    parser.add_argument("--json", dest="as_json", action="store_true", help="força leitura JSON")
    args = parser.parse_args()
    path = Path(args.arquivo)
    if not path.exists():
        print(json.dumps({"ok": False, "erros": [f"arquivo não encontrado: {path}"]}, ensure_ascii=False, indent=2))
        return 1

    try:
        rows = carregar(path)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "erros": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1

    relatorio = validar(rows)
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    return 0 if relatorio["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
