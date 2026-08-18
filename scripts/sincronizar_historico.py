#!/usr/bin/env python3
"""
Sincroniza dados/resultados_lotofacil.csv com a API oficial da Caixa
(e fallback heroku) até o último concurso disponível.

Uso:
  python scripts/sincronizar_historico.py
  python scripts/sincronizar_historico.py --ate 3749
  python scripts/sincronizar_historico.py --max-novos 30
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "dados" / "resultados_lotofacil.csv"

CAIXA = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
HEROKU = "https://loteriascaixa-api.herokuapp.com/api/lotofacil"

FIELDNAMES = ["concurso", "data"] + [f"b{i:02d}" for i in range(1, 16)]


def http_json(url: str, timeout: float = 25.0) -> dict | None:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "LotofacilLab/1.0 (+checkpoint-sync)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace").strip()
            if not raw:
                return None
            return json.loads(raw)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ValueError):
        return None


def parse_resultado(data: dict | None) -> dict | None:
    if not data:
        return None
    concurso = data.get("numero") or data.get("concurso") or data.get("numeroConcurso")
    if not concurso:
        return None
    concurso = int(concurso)
    data_str = str(
        data.get("dataApuracao") or data.get("data") or data.get("dataSorteio") or ""
    ).strip()
    raw = (
        data.get("listaDezenas")
        or data.get("dezenas")
        or data.get("dezenasSorteadasOrdemSorteio")
        or []
    )
    dezenas = sorted({int(x) for x in raw})
    if len(dezenas) != 15 or any(d < 1 or d > 25 for d in dezenas):
        return None
    return {"concurso": concurso, "data": data_str, "dezenas": dezenas}


def buscar_concurso(n: int) -> dict | None:
    for base in (CAIXA, HEROKU):
        parsed = parse_resultado(http_json(f"{base}/{n}"))
        if parsed and parsed["concurso"] == n:
            return parsed
    return None


def buscar_ultimo() -> dict | None:
    melhor: dict | None = None
    for url in (CAIXA, f"{HEROKU}/latest"):
        parsed = parse_resultado(http_json(url))
        if parsed and (melhor is None or parsed["concurso"] > melhor["concurso"]):
            melhor = parsed
    return melhor


def carregar_csv(path: Path) -> dict[int, dict]:
    if not path.exists():
        return {}
    by: dict[int, dict] = {}
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                c = int(row["concurso"])
            except (KeyError, ValueError):
                continue
            dezenas = []
            if all(f"b{i:02d}" in row for i in range(1, 16)):
                dezenas = [int(row[f"b{i:02d}"]) for i in range(1, 16)]
            by[c] = {"concurso": c, "data": row.get("data") or "", "dezenas": dezenas}
    return by


def gravar_csv(path: Path, by: dict[int, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [by[k] for k in sorted(by.keys())]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for r in rows:
            line = {"concurso": r["concurso"], "data": r.get("data") or ""}
            dez = sorted(int(x) for x in r["dezenas"])
            for i, d in enumerate(dez, start=1):
                line[f"b{i:02d}"] = d
            writer.writerow(line)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza histórico Lotofácil com a Caixa")
    parser.add_argument("--csv", default=str(CSV_PATH))
    parser.add_argument("--ate", type=int, default=None, help="Concurso máximo (default: último da API)")
    parser.add_argument("--max-novos", type=int, default=40, help="Limite de concursos novos por execução")
    parser.add_argument("--sleep", type=float, default=0.15, help="Pausa entre requests")
    args = parser.parse_args()

    path = Path(args.csv)
    by = carregar_csv(path)
    max_local = max(by.keys()) if by else 0

    ultimo = buscar_ultimo()
    if not ultimo:
        print(json.dumps({"ok": False, "erro": "Não foi possível obter o último concurso das APIs"}, ensure_ascii=False))
        return 1

    alvo = int(args.ate) if args.ate else int(ultimo["concurso"])
    inicio = max_local + 1 if max_local else max(1, alvo - args.max_novos + 1)
    if inicio > alvo:
        print(json.dumps({
            "ok": True,
            "mensagem": "CSV já está atualizado",
            "max_local": max_local,
            "ultimo_api": ultimo["concurso"],
            "total": len(by),
        }, ensure_ascii=False, indent=2))
        return 0

    adicionados = []
    falhas = []
    for n in range(inicio, alvo + 1):
        if len(adicionados) >= args.max_novos:
            break
        if n in by and len(by[n].get("dezenas") or []) == 15:
            continue
        res = buscar_concurso(n)
        if not res:
            falhas.append(n)
            time.sleep(args.sleep)
            continue
        by[n] = res
        adicionados.append(n)
        time.sleep(args.sleep)

    gravar_csv(path, by)
    max_final = max(by.keys()) if by else 0

    # buracos
    conc = sorted(by.keys())
    buracos = []
    if conc:
        esperado = set(range(conc[0], conc[-1] + 1))
        buracos = sorted(esperado - set(conc))

    print(json.dumps({
        "ok": len(falhas) == 0 and len(buracos) == 0,
        "csv": str(path),
        "max_antes": max_local,
        "max_depois": max_final,
        "ultimo_api": ultimo["concurso"],
        "adicionados": adicionados,
        "falhas": falhas,
        "buracos": buracos[:30],
        "total": len(by),
        "concurso_alvo_checkpoint": max_final + 1 if max_final else None,
    }, ensure_ascii=False, indent=2))
    return 0 if not falhas else 1


if __name__ == "__main__":
    raise SystemExit(main())
