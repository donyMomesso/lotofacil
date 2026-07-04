"""
Estudo educativo: tabela de "sequência" e "salto" das dezenas.

Para cada trinca de números consecutivos (01-02-03, 02-03-04, ..., 23-24-25),
calcula, sobre o histórico real:
  - "sequência": em quantos concursos as 3 dezenas da trinca saíram JUNTAS
    no mesmo sorteio;
  - "salto": em quantos concursos NENHUMA das 3 dezenas da trinca saiu.

Isto é o mesmo tipo de tabela que aparece em vários sites de estatística
de loteria. O ponto pedagógico do laboratório aqui é comparar cada valor
observado com o valor teórico fixo (hipergeométrico) que qualquer trinca
de 3 dezenas específicas deveria ter, para mostrar que a variação entre
trincas é ruído amostral, não sinal de "trinca quente" ou "atrasada".

Uso:
    python3 tabela_sequencias.py
"""
import csv
import os
from math import comb

import lotofacil_lib as lib

SAIDA_CSV = os.path.join(lib.DADOS_DIR, "sequencias_saltos.csv")

# Valores teoricos fixos: probabilidade de uma trinca especifica de 3
# dezenas sair inteira (sequencia) ou nenhuma delas sair (salto) em um
# sorteio de 15 dentre 25.
SEQ_TEORICA_PCT = round(comb(22, 12) / comb(25, 15) * 100, 4)
SALTO_TEORICA_PCT = round(comb(22, 15) / comb(25, 15) * 100, 4)


def calcular():
    resultados = lib.carregar_resultados()
    total = len(resultados)
    linhas = []
    for s in range(1, 24):
        trinca = {s, s + 1, s + 2}
        seq_count = sum(1 for r in resultados if trinca.issubset(r["dezenas"]))
        salto_count = sum(1 for r in resultados if trinca.isdisjoint(r["dezenas"]))
        linhas.append({
            "trinca": f"{s:02d},{s+1:02d},{s+2:02d}",
            "sequencia_qtd": seq_count,
            "sequencia_pct": round(100 * seq_count / total, 2) if total else 0.0,
            "salto_qtd": salto_count,
            "salto_pct": round(100 * salto_count / total, 2) if total else 0.0,
            "total_concursos": total,
            "sequencia_teorica_pct": SEQ_TEORICA_PCT,
            "salto_teorico_pct": SALTO_TEORICA_PCT,
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
    print(f"Tabela de sequência/salto salva em: {SAIDA_CSV}")
    print(f"Teórico sequência (trinca específica junta): {SEQ_TEORICA_PCT}%")
    print(f"Teórico salto (trinca específica ausente): {SALTO_TEORICA_PCT}%")
    print()
    print(f"{'trinca':>10} {'seq n':>7} {'seq %':>7} {'salto n':>8} {'salto %':>8}")
    for l in linhas:
        print(f"{l['trinca']:>10} {l['sequencia_qtd']:>7} {l['sequencia_pct']:>6.2f}% "
              f"{l['salto_qtd']:>8} {l['salto_pct']:>7.2f}%")


if __name__ == "__main__":
    main()
