"""
Executa o backtest completo M1-M8 e valida os CSVs gerados.

Uso:
    python scripts/executar_backtest_completo.py
"""
import csv
import os
import sys
import traceback

import lotofacil_lib as lib
from simular_backtest import main as executar_backtest


SIMULACAO_CSV = os.path.join(lib.DADOS_DIR, "simulacao_metodos.csv")
ESTATISTICAS_CSV = os.path.join(lib.DADOS_DIR, "estatisticas_simulacao.csv")


def contar_linhas_csv(caminho):
    """Conta as linhas de dados de um CSV, ignorando o cabecalho."""
    with open(caminho, encoding="utf-8") as arquivo:
        return sum(1 for _ in csv.DictReader(arquivo))


def validar_csv(caminho, nome):
    """Valida se o CSV existe e contem dados."""
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"{nome} nao foi encontrado em: {caminho}")

    total_linhas = contar_linhas_csv(caminho)
    if total_linhas <= 0:
        raise RuntimeError(f"{nome} foi gerado, mas nao possui linhas de dados.")

    return total_linhas


def obter_concursos_simulados():
    """Le o CSV estatistico e retorna a quantidade de concursos simulados."""
    with open(ESTATISTICAS_CSV, encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))

    if not linhas:
        raise RuntimeError("O CSV de estatisticas esta vazio.")

    return int(max(float(linha.get("total_concursos_simulados", 0) or 0) for linha in linhas))


def main():
    """Executa o backtest completo, valida os arquivos e imprime um resumo."""
    try:
        print("Iniciando execucao do backtest completo M1-M8...")
        print("Gerando simulacao retroativa. Isso pode levar alguns minutos.")

        executar_backtest()

        print("\nValidando arquivos gerados...")
        total_jogos = validar_csv(SIMULACAO_CSV, "dados/simulacao_metodos.csv")
        total_metodos = validar_csv(ESTATISTICAS_CSV, "dados/estatisticas_simulacao.csv")
        total_concursos = obter_concursos_simulados()

        print("\nBacktest completo executado com sucesso.")
        print(f"Concursos simulados: {total_concursos}")
        print(f"Total de jogos gerados: {total_jogos}")
        print(f"Metodos no resumo estatistico: {total_metodos}")
        print(f"CSV atualizado: {SIMULACAO_CSV}")
        print(f"CSV atualizado: {ESTATISTICAS_CSV}")
    except Exception as erro:
        print("\nErro ao executar o backtest completo.", file=sys.stderr)
        print(str(erro), file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
