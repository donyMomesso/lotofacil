"""
Estudo educativo: exemplos ilustrativos de combinações que passam pelos
4 filtros combinados (par/impar 8/7, soma 180-210, sem sequencia de 6+,
max 1 linha vazia), e o backtest de cada exemplo fixo contra TODO o
historico real da Lotofacil.

Isto NAO gera jogos para apostar. O objetivo e mostrar, com exemplos
concretos, que mesmo uma combinacao "bem filtrada" tem media de acertos
igual a esperanca teorica (9,0) quando testada contra milhares de
sorteios reais -- reforcando que filtro nao cria vantagem preditiva.

Uso:
    python3 estudo_desdobramento_filtros.py [n_exemplos] [seed]
"""
import csv
import os
import sys

import lotofacil_lib as lib

SAIDA_CSV = os.path.join(lib.DADOS_DIR, "exemplos_filtrados_backtest.csv")


def main():
    n_exemplos = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42

    exemplos = lib.gerar_exemplos_filtrados(n_exemplos=n_exemplos, seed=seed)
    if not exemplos:
        print("Nenhum exemplo gerado (filtro combinado pode estar rejeitando tudo).")
        return

    resultados = lib.backtest_combinacoes_fixas(exemplos)

    os.makedirs(lib.DADOS_DIR, exist_ok=True)
    fieldnames = list(resultados[0].keys())
    with open(SAIDA_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados)

    print(f"Exemplos e backtest salvos em: {SAIDA_CSV}")
    print(f"Esperança teórica de referência: {lib.ESPERANCA_TEORICA}")
    print()
    for r in resultados:
        print(f"Exemplo {r['exemplo']}: {r['dezenas']}")
        print(f"  Testado contra {r['total_concursos_testados']} concursos reais -> "
              f"média {r['media_acertos']} (dif. vs. esperança: {r['diferenca_vs_esperanca']:+.4f}), "
              f"desvio {r['desvio_padrao_acertos']}, máx. observado {r['max_acertos_observado']}, "
              f"11+ em {r['pct_11_ou_mais']}% dos concursos, 13+ em {r['pct_13_ou_mais']}%, "
              f"15 acertos {r['qtd_15_acertos']}x")


if __name__ == "__main__":
    main()
