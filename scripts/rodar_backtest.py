"""
Executa o backtest completo da Lotofacil e valida os CSVs gerados.

Uso:
    python scripts/rodar_backtest.py
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
    """Conta linhas de dados de um CSV, desconsiderando o cabecalho."""
    with open(caminho, encoding="utf-8") as arquivo:
        return sum(1 for _ in csv.DictReader(arquivo))


def validar_arquivo(caminho, nome):
    """Garante que um arquivo CSV existe e tem pelo menos uma linha de dados."""
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"{nome} nao foi gerado: {caminho}")

    total_linhas = contar_linhas_csv(caminho)
    if total_linhas <= 0:
        raise RuntimeError(f"{nome} foi gerado, mas esta vazio: {caminho}")

    return total_linhas


def obter_total_concursos_simulados():
    """
    Lê o CSV agregado e retorna a quantidade de concursos simulados.

    Todos os metodos devem ter o mesmo total de concursos; usamos o maior valor
    encontrado para evitar falha por pequenas diferencas de formatacao.
    """
    with open(ESTATISTICAS_CSV, encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))

    if not linhas:
        return 0

    return int(max(float(linha.get("total_concursos_simulados", 0) or 0) for linha in linhas))


def main():
    """Executa o backtest completo e imprime um resumo de validacao."""
    try:
        print("Iniciando backtest completo M1-M8...")
        executar_backtest()

        total_jogos = validar_arquivo(SIMULACAO_CSV, "dados/simulacao_metodos.csv")
        total_metodos = validar_arquivo(ESTATISTICAS_CSV, "dados/estatisticas_simulacao.csv")
        total_concursos = obter_total_concursos_simulados()

        print("\nBacktest executado com sucesso.")
        print(f"Concursos simulados: {total_concursos}")
        print(f"Jogos simulados no total: {total_jogos}")
        print(f"Metodos no resumo estatistico: {total_metodos}")
        print(f"CSV atualizado: {SIMULACAO_CSV}")
        print(f"CSV atualizado: {ESTATISTICAS_CSV}")
    except Exception as erro:
        print("\nFalha ao executar o backtest.", file=sys.stderr)
        print(str(erro), file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
