"""
Simulação retroativa (backtest) dos 5 métodos contra TODOS os concursos
reais já registrados.

Para cada concurso N (a partir do 2º concurso do histórico), monta os
5 jogos de estudo usando só os dados disponíveis ANTES de N (sem
"olhar o futuro"), confere contra o resultado real de N, e segue em
frente. Isso dá uma amostra muito maior (milhares de concursos) do que
esperar o dia a dia — é um exercício histórico, não uma previsão.

Os resultados vão em arquivos SEPARADOS dos dados "ao vivo"
(dados/jogos_gerados.csv e dados/conferencia.csv continuam sendo só
sobre os jogos gerados prospectivamente, dia a dia):

    dados/simulacao_metodos.csv       -> uma linha por (concurso, método)
    dados/estatisticas_simulacao.csv  -> desempenho agregado por método

Uso:
    python3 simular_backtest.py
"""
import csv
import os
import random
import statistics
from collections import Counter

import lotofacil_lib as lib

SIMULACAO_CSV = os.path.join(lib.DADOS_DIR, "simulacao_metodos.csv")
ESTATISTICAS_SIM_CSV = os.path.join(lib.DADOS_DIR, "estatisticas_simulacao.csv")


def main():
    resultados = lib.carregar_resultados()
    if len(resultados) < 2:
        print("Histórico insuficiente para simular (precisa de pelo menos 2 concursos).")
        return

    freq = {d: 0 for d in lib.TODAS_DEZENAS}
    ultima_aparicao = {}
    acertos_por_metodo = {m: [] for m in lib.METODOS}

    linhas_sim = []

    for idx, r in enumerate(resultados):
        concurso = r["concurso"]
        dezenas_reais = r["dezenas"]

        if idx >= 1:
            atraso = {}
            for d in lib.TODAS_DEZENAS:
                if d in ultima_aparicao:
                    atraso[d] = (idx - 1) - ultima_aparicao[d]
                else:
                    atraso[d] = idx

            rng = random.Random(concurso)
            jogos = {
                "M1_aleatorio_puro": lib.metodo_aleatorio_puro(rng),
                "M2_mais_frequentes": lib.metodo_mais_frequentes(rng, freq),
                "M3_mais_atrasadas": lib.metodo_mais_atrasadas(rng, atraso),
                "M4_par_impar_balanceado": lib.metodo_par_impar_balanceado(rng),
                "M5_soma_faixa_comum": lib.metodo_soma_faixa_comum(rng),
            }
            for metodo, dezenas in jogos.items():
                acertos = len(dezenas & dezenas_reais)
                acertos_por_metodo[metodo].append(acertos)
                linhas_sim.append({
                    "concurso": concurso,
                    "metodo": metodo,
                    "dezenas": "-".join(f"{d:02d}" for d in sorted(dezenas)),
                    "acertos": acertos,
                })

        for d in dezenas_reais:
            freq[d] += 1
            ultima_aparicao[d] = idx

        if idx % 500 == 0:
            print(f"[progresso] concurso {concurso} ({idx + 1}/{len(resultados)})")

    fieldnames_sim = ["concurso", "metodo", "dezenas", "acertos"]
    with open(SIMULACAO_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_sim)
        writer.writeheader()
        writer.writerows(linhas_sim)

    linhas_stats = []
    for metodo in lib.METODOS:
        acertos_lista = acertos_por_metodo[metodo]
        n = len(acertos_lista)
        dist = Counter(acertos_lista)
        media = statistics.mean(acertos_lista) if n else 0.0
        desvio = statistics.pstdev(acertos_lista) if n > 1 else 0.0
        linha = {
            "metodo": metodo,
            "total_concursos_simulados": n,
            "media_acertos": round(media, 4),
            "desvio_padrao_acertos": round(desvio, 4),
            "esperanca_teorica": lib.ESPERANCA_TEORICA,
            "diferenca_vs_esperanca": round(media - lib.ESPERANCA_TEORICA, 4),
            "min_acertos": min(acertos_lista) if n else "",
            "max_acertos": max(acertos_lista) if n else "",
            "pct_11_ou_mais": round(100 * sum(1 for a in acertos_lista if a >= 11) / n, 3) if n else 0.0,
            "pct_13_ou_mais": round(100 * sum(1 for a in acertos_lista if a >= 13) / n, 3) if n else 0.0,
            "pct_14_ou_mais": round(100 * sum(1 for a in acertos_lista if a >= 14) / n, 4) if n else 0.0,
            "pct_15": round(100 * sum(1 for a in acertos_lista if a == 15) / n, 5) if n else 0.0,
        }
        for k in range(16):
            linha[f"qtd_{k}_acertos"] = dist.get(k, 0)
        linhas_stats.append(linha)

    fieldnames_stats = list(linhas_stats[0].keys())
    with open(ESTATISTICAS_SIM_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_stats)
        writer.writeheader()
        writer.writerows(linhas_stats)

    print(f"\nSimulação concluída: {len(resultados) - 1} concursos backtested, "
          f"{len(linhas_sim)} jogos de estudo simulados no total.")
    print(f" - {SIMULACAO_CSV}")
    print(f" - {ESTATISTICAS_SIM_CSV}")
    print(f"\nResumo (esperança teórica = {lib.ESPERANCA_TEORICA}):")
    for l in linhas_stats:
        print(f"  {l['metodo']:<26} n={l['total_concursos_simulados']:<5} "
              f"média={l['media_acertos']:<8} desvio={l['desvio_padrao_acertos']:<8} "
              f"dif_vs_esperanca={l['diferenca_vs_esperanca']:+.4f}  "
              f"%13+={l['pct_13_ou_mais']}%  %15={l['pct_15']}%")


if __name__ == "__main__":
    main()
