"""
Backtest retroativo dos 8 metodos estatisticos da Lotofacil.

Para cada concurso N, o script gera 5 jogos por metodo usando somente o
historico disponivel ate N-1. O resultado real de N so e usado depois, na etapa
de conferencia, evitando data leakage.

Arquivos gerados:
    dados/simulacao_metodos.csv
    dados/estatisticas_simulacao.csv
"""
import csv
import os
import random
import statistics
from collections import Counter

from gerar_jogos_avancados import (
    metodo_m6_filtros_combinados,
    metodo_m7_cobertura_pares,
    metodo_m8_repeticao_controlada,
)
import lotofacil_lib as lib


SIMULACAO_CSV = os.path.join(lib.DADOS_DIR, "simulacao_metodos.csv")
ESTATISTICAS_SIM_CSV = os.path.join(lib.DADOS_DIR, "estatisticas_simulacao.csv")
JOGOS_POR_METODO = 5

METODOS_BASICOS = [
    "M1_aleatorio_puro",
    "M2_mais_frequentes",
    "M3_mais_atrasadas",
    "M4_par_impar_balanceado",
    "M5_soma_faixa_comum",
]

METODOS_AVANCADOS = {
    "M6_filtros_combinados": metodo_m6_filtros_combinados,
    "M7_cobertura_pares": metodo_m7_cobertura_pares,
    "M8_repeticao_controlada": metodo_m8_repeticao_controlada,
}


def filtrar_historico_anterior(resultados, concurso):
    """
    Retorna somente concursos anteriores ao concurso em teste.

    Mantem o formato original retornado por lotofacil_lib.carregar_resultados():
    dicionarios com pelo menos as chaves "concurso" e "dezenas".
    """
    return [r for r in resultados if r["concurso"] < concurso]


def gerar_jogos_basicos(concurso):
    """
    Gera 5 jogos para cada metodo basico.

    Cada variacao usa uma seed propria e a biblioteca recebe ate_concurso como
    concurso-1, preservando a regra de nao usar o resultado atual.
    """
    jogos_por_metodo = {metodo: [] for metodo in METODOS_BASICOS}
    for jogo_idx in range(1, JOGOS_POR_METODO + 1):
        seed = concurso * 100 + jogo_idx
        jogos = lib.gerar_todos_metodos(seed=seed, ate_concurso=concurso - 1)
        for metodo in METODOS_BASICOS:
            jogos_por_metodo[metodo].append(sorted(jogos[metodo]))
    return jogos_por_metodo


def gerar_jogos_avancados(historico_anterior, concurso):
    """
    Gera 5 jogos para M6, M7 e M8 usando apenas o historico anterior.

    Os metodos avancados recebem o historico no formato completo de dicionarios.
    """
    jogos_por_metodo = {}
    for offset, (metodo, gerador) in enumerate(METODOS_AVANCADOS.items(), start=6):
        rng = random.Random(concurso * 1000 + offset)
        jogos_por_metodo[metodo] = gerador(historico_anterior, rng)
    return jogos_por_metodo


def registrar_simulacoes(linhas_sim, acertos_por_metodo, concurso, dezenas_reais, jogos_por_metodo):
    """Confere cada jogo e registra uma linha no CSV de simulacao."""
    for metodo, jogos in jogos_por_metodo.items():
        for jogo_idx, dezenas in enumerate(jogos, start=1):
            dezenas_ordenadas = sorted(dezenas)
            acertos = len(set(dezenas_ordenadas) & dezenas_reais)
            acertos_por_metodo[metodo].append(acertos)
            linhas_sim.append({
                "concurso": concurso,
                "metodo": metodo,
                "jogo_idx": jogo_idx,
                "dezenas": "-".join(f"{d:02d}" for d in dezenas_ordenadas),
                "acertos": acertos,
            })


def calcular_estatisticas(metodo, acertos_lista):
    """Calcula estatisticas completas para um metodo."""
    n = len(acertos_lista)
    dist = Counter(acertos_lista)
    media = statistics.mean(acertos_lista) if n else 0.0
    desvio = statistics.pstdev(acertos_lista) if n > 1 else 0.0

    linha = {
        "metodo": metodo,
        "total_jogos_simulados": n,
        "total_concursos_simulados": round(n / JOGOS_POR_METODO, 2) if n else 0,
        "jogos_por_concurso": JOGOS_POR_METODO,
        "media_acertos": round(media, 4),
        "desvio_padrao_acertos": round(desvio, 4),
        "esperanca_teorica": lib.ESPERANCA_TEORICA,
        "diferenca_vs_esperanca": round(media - lib.ESPERANCA_TEORICA, 4),
        "min_acertos": min(acertos_lista) if n else "",
        "max_acertos": max(acertos_lista) if n else "",
        "pct_11_ou_mais": round(100 * sum(1 for a in acertos_lista if a >= 11) / n, 3) if n else 0.0,
        "pct_12_ou_mais": round(100 * sum(1 for a in acertos_lista if a >= 12) / n, 3) if n else 0.0,
        "pct_13_ou_mais": round(100 * sum(1 for a in acertos_lista if a >= 13) / n, 3) if n else 0.0,
        "pct_14_ou_mais": round(100 * sum(1 for a in acertos_lista if a >= 14) / n, 4) if n else 0.0,
        "pct_15": round(100 * sum(1 for a in acertos_lista if a == 15) / n, 5) if n else 0.0,
    }

    for acertos in range(16):
        linha[f"qtd_{acertos}_acertos"] = dist.get(acertos, 0)

    return linha


def main():
    resultados = lib.carregar_resultados()
    if len(resultados) < 2:
        print("Historico insuficiente para simular.")
        return

    metodos = METODOS_BASICOS + list(METODOS_AVANCADOS.keys())
    acertos_por_metodo = {metodo: [] for metodo in metodos}
    linhas_sim = []

    for idx, resultado in enumerate(resultados):
        concurso = resultado["concurso"]
        dezenas_reais = resultado["dezenas"]

        if idx == 0:
            continue

        historico_anterior = filtrar_historico_anterior(resultados, concurso)
        jogos_basicos = gerar_jogos_basicos(concurso)
        jogos_avancados = gerar_jogos_avancados(historico_anterior, concurso)
        jogos_por_metodo = {**jogos_basicos, **jogos_avancados}

        registrar_simulacoes(
            linhas_sim,
            acertos_por_metodo,
            concurso,
            dezenas_reais,
            jogos_por_metodo,
        )

        if idx % 500 == 0:
            print(f"[progresso] concurso {concurso} ({idx + 1}/{len(resultados)})")

    with open(SIMULACAO_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["concurso", "metodo", "jogo_idx", "dezenas", "acertos"])
        writer.writeheader()
        writer.writerows(linhas_sim)

    linhas_stats = [
        calcular_estatisticas(metodo, acertos_por_metodo[metodo])
        for metodo in metodos
    ]

    with open(ESTATISTICAS_SIM_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(linhas_stats[0].keys()))
        writer.writeheader()
        writer.writerows(linhas_stats)

    print(
        f"Backtest concluido: {len(resultados) - 1} concursos, "
        f"{len(linhas_sim)} jogos simulados."
    )
    print(f"Arquivos atualizados: {SIMULACAO_CSV} e {ESTATISTICAS_SIM_CSV}")


if __name__ == "__main__":
    main()
