"""
Estudo educativo: apostas estendidas (16 a 20 dezenas na Lotofácil).

Isto é matemática pura de combinatória — não depende de nenhum resultado
real, não simula sorteios e não recomenda comprar essas apostas. Mostra
apenas três fatos que sempre andam juntos quando se aumenta a quantidade
de dezenas por aposta:

  1. quantas combinações de 15 dezenas cada aposta cobre (C(n,15));
  2. quanto isso custa (Caixa cobra por cada combinação de 15 embutida);
  3. qual passa a ser o número esperado de dezenas certas dentre as `n`
     escolhidas (E[T] = n * 15/25), e a chance de bater 11+, 13+ ou 15
     dessas dezenas com o sorteio real (distribuição hipergeométrica).

O ponto pedagógico: a média esperada sobe conforme n sobe, mas o custo
sobe na mesma proporção matemática (ambos vêm da mesma combinatória).
Não existe, aqui, uma forma de aumentar a média por real investido —
isso é literalmente o mesmo eixo custo/cobertura de sempre, só que
explícito em reais.

Uso:
    python3 simular_apostas_estendidas.py
"""
import csv
import os
from math import comb

import lotofacil_lib as lib

PRECO_APOSTA_SIMPLES = 3.50
SAIDA_CSV = os.path.join(lib.DADOS_DIR, "apostas_estendidas.csv")


def prob_t_ou_mais(n, t_min):
    """P(T >= t_min), onde T = nº de dezenas, dentre as `n` escolhidas,
    que coincidem com as 15 sorteadas. Hipergeométrica: N=25, K=15, amostra=n."""
    total = comb(25, n)
    acc = 0.0
    for t in range(t_min, min(15, n) + 1):
        if n - t < 0 or n - t > 10:
            continue
        acc += comb(15, t) * comb(10, n - t) / total
    return acc


def calcular():
    linhas = []
    for n in range(15, 21):
        combinacoes = comb(n, 15)
        custo = combinacoes * PRECO_APOSTA_SIMPLES
        media_esperada = n * 15 / 25
        linhas.append({
            "dezenas_na_aposta": n,
            "combinacoes_15_embutidas": combinacoes,
            "custo_reais": round(custo, 2),
            "media_acertos_esperada": round(media_esperada, 2),
            "pct_11_ou_mais": round(100 * prob_t_ou_mais(n, 11), 4),
            "pct_13_ou_mais": round(100 * prob_t_ou_mais(n, 13), 4),
            "pct_15": round(100 * prob_t_ou_mais(n, 15), 6),
            "custo_por_ponto_percentual_de_11mais": (
                round(custo / (100 * prob_t_ou_mais(n, 11)), 2) if prob_t_ou_mais(n, 11) > 0 else None
            ),
        })
    return linhas


def salvar(linhas):
    os.makedirs(lib.DADOS_DIR, exist_ok=True)
    fieldnames = list(linhas[0].keys())
    with open(SAIDA_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(linhas)


def main():
    linhas = calcular()
    salvar(linhas)
    print(f"Apostas estendidas calculadas e salvas em: {SAIDA_CSV}")
    print()
    print(f"{'n':>3} {'combinações':>13} {'custo (R$)':>13} {'média esp.':>11} {'%11+':>8} {'%13+':>8} {'%15':>10}")
    for l in linhas:
        print(f"{l['dezenas_na_aposta']:>3} {l['combinacoes_15_embutidas']:>13,} "
              f"{l['custo_reais']:>13,.2f} {l['media_acertos_esperada']:>11.2f} "
              f"{l['pct_11_ou_mais']:>7.2f}% {l['pct_13_ou_mais']:>7.4f}% {l['pct_15']:>9.6f}%")


if __name__ == "__main__":
    main()
