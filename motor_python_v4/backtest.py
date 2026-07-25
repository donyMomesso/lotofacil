from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean

from engine import MemoriaAdaptativa, MotorLotofacil, carregar_historico_json


def executar(caminho: str, inicio: int, base: int, jogos: int) -> dict:
    historico = carregar_historico_json(caminho)
    resultados = []
    memoria = MemoriaAdaptativa()

    for i in range(max(inicio, 30), len(historico)):
        treino = historico[:i]
        alvo = historico[i]
        motor = MotorLotofacil(treino, memoria, seed=alvo.concurso)
        geracao = motor.gerar(base, jogos)
        registro = motor.registrar_desempenho(geracao, alvo.dezenas)
        registro["concurso"] = alvo.concurso
        resultados.append(registro)
        motor.recalibrar_pesos()

    distribuicao = Counter(x["melhor_acerto"] for x in resultados)
    return {
        "concursos_testados": len(resultados),
        "media_acertos_base": round(mean(x["acertos_base"] for x in resultados), 4) if resultados else 0,
        "bases_com_15": sum(x["acertos_base"] == 15 for x in resultados),
        "bases_com_14_ou_mais": sum(x["acertos_base"] >= 14 for x in resultados),
        "melhor_jogo_distribuicao": dict(sorted(distribuicao.items())),
        "pesos_finais": memoria.pesos.__dict__,
        "resultados": resultados,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("historico")
    p.add_argument("--inicio", type=int, default=30)
    p.add_argument("--base", type=int, default=18)
    p.add_argument("--jogos", type=int, default=120)
    p.add_argument("--saida", default="relatorio_backtest.json")
    a = p.parse_args()
    resumo = executar(a.historico, a.inicio, a.base, a.jogos)
    Path(a.saida).write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in resumo.items() if k != "resultados"}, ensure_ascii=False, indent=2))
