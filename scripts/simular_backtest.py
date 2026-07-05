"""
Simulacao retroativa (backtest) dos metodos oficiais contra todos os concursos.

Para cada concurso N, o script gera jogos usando apenas os dados disponiveis
ate o concurso N-1. Isso evita data leakage: o resultado real de N nunca entra
na geracao dos jogos que serao conferidos contra ele.

Saidas:
    dados/simulacao_metodos.csv       -> uma linha por jogo simulado
    dados/estatisticas_simulacao.csv  -> desempenho agregado por metodo
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

JOGOS_POR_METODO = 5


def resultados_dezenas_ate(resultados, ate_concurso):
    """Converte o historico em listas de dezenas ate o concurso informado."""
    return [
        sorted(r["dezenas"])
        for r in resultados
        if r["concurso"] <= ate_concurso
    ]


def gerar_jogos_basicos(concurso):
    """
    Gera 5 jogos para cada metodo basico.

    Cada rodada usa uma seed diferente, mas sempre considera apenas dados ate
    concurso-1 dentro de lotofacil_lib.gerar_todos_metodos().
    """
    jogos_por_metodo = {metodo: [] for metodo in METODOS_BASICOS}
    for jogo_idx in range(1, JOGOS_POR_METODO + 1):
        seed = concurso * 100 + jogo_idx
        jogos = lib.gerar_todos_metodos(seed=seed, ate_concurso=concurso - 1)
        for metodo in METODOS_BASICOS:
            jogos_por_metodo[metodo].append(sorted(jogos[metodo]))
    return jogos_por_metodo


def gerar_jogos_avancados_para_concurso(resultados_anteriores, concurso):
    """
    Gera 5 jogos para M6, M7 e M8 usando somente resultados anteriores.

    As funcoes avancadas recebem explicitamente o historico anterior, portanto
    nao acessam o resultado do concurso que esta sendo testado.
    """
    return {
        metodo: gerador(
            resultados_anteriores,
            random.Random(concurso * 1000 + offset),
        )
        for offset, (metodo, gerador) in enumerate(METODOS_AVANCADOS.items(), start=6)
    }


def registrar_linhas_simulacao(linhas_sim, acertos_por_metodo, concurso, dezenas_reais, jogos_por_metodo):
    """Confere jogos contra o resultado real e adiciona linhas ao CSV final."""
    for metodo, jogos in jogos_por_metodo.items():
        for jogo_idx, dezenas in enumerate(jogos, start=1):
            dezenas_set = set(dezenas)
            acertos = len(dezenas_set & dezenas_reais)
            acertos_por_metodo[metodo].append(acertos)
            linhas_sim.append({
                "concurso": concurso,
                "metodo": metodo,
                "jogo_idx": jogo_idx,
                "dezenas": "-".join(f"{d:02d}" for d in sorted(dezenas)),
                "acertos": acertos,
            })


def calcular_linha_estatistica(metodo, acertos_lista):
    """Calcula estatisticas agregadas de um metodo."""
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

    for k in range(16):
        linha[f"qtd_{k}_acertos"] = dist.get(k, 0)

    return linha


def main():
    resultados = lib.carregar_resultados()
    if len(resultados) < 2:
        print("Historico insuficiente para simular (precisa de pelo menos 2 concursos).")
        return

    metodos = METODOS_BASICOS + list(METODOS_AVANCADOS.keys())
    acertos_por_metodo = {metodo: [] for metodo in metodos}
    linhas_sim = []

    for idx, resultado in enumerate(resultados):
        concurso = resultado["concurso"]
        dezenas_reais = resultado["dezenas"]

        # O primeiro concurso nao tem historico anterior suficiente para teste.
        if idx >= 1:
            resultados_anteriores = resultados_dezenas_ate(resultados, concurso - 1)

            jogos_basicos = gerar_jogos_basicos(concurso)
            jogos_avancados = gerar_jogos_avancados_para_concurso(
                resultados_anteriores,
                concurso,
            )
            jogos_por_metodo = {**jogos_basicos, **jogos_avancados}

            registrar_linhas_simulacao(
                linhas_sim,
                acertos_por_metodo,
                concurso,
                dezenas_reais,
                jogos_por_metodo,
            )

        if idx % 500 == 0:
            print(f"[progresso] concurso {concurso} ({idx + 1}/{len(resultados)})")

    fieldnames_sim = ["concurso", "metodo", "jogo_idx", "dezenas", "acertos"]
    with open(SIMULACAO_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_sim)
        writer.writeheader()
        writer.writerows(linhas_sim)

    linhas_stats = [
        calcular_linha_estatistica(metodo, acertos_por_metodo[metodo])
        for metodo in metodos
    ]

    fieldnames_stats = list(linhas_stats[0].keys())
    with open(ESTATISTICAS_SIM_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_stats)
        writer.writeheader()
        writer.writerows(linhas_stats)

    print(
        f"\nSimulacao concluida: {len(resultados) - 1} concursos backtested, "
        f"{len(linhas_sim)} jogos simulados no total."
    )
    print(f" - {SIMULACAO_CSV}")
    print(f" - {ESTATISTICAS_SIM_CSV}")
    print(f"\nResumo (esperanca teorica = {lib.ESPERANCA_TEORICA}):")
    for linha in linhas_stats:
        print(
            f"  {linha['metodo']:<28} "
            f"jogos={linha['total_jogos_simulados']:<6} "
            f"media={linha['media_acertos']:<8} "
            f"desvio={linha['desvio_padrao_acertos']:<8} "
            f"11+={linha['pct_11_ou_mais']}% "
            f"13+={linha['pct_13_ou_mais']}%"
        )


if __name__ == "__main__":
    main()
