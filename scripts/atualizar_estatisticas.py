"""
Recalcula as estatísticas agregadas a partir do histórico atual:
  - dados/frequencia_dezenas.csv  (frequência e atraso de cada dezena)
  - dados/estatisticas_metodos.csv (desempenho comparado de cada método)

Uso:
    python3 atualizar_estatisticas.py
"""
import lotofacil_lib as lib


def main():
    lib.salvar_frequencia_dezenas()
    lib.salvar_estatisticas_metodos()

    print("Estatísticas atualizadas.")
    print(f" - {lib.FREQUENCIA_CSV}")
    print(f" - {lib.ESTATISTICAS_CSV}")

    linhas = lib.calcular_estatisticas_metodos()
    if linhas and any(l["total_jogos_conferidos"] for l in linhas):
        print(f"\nResumo (esperança teórica de acertos = {lib.ESPERANCA_TEORICA}):")
        for l in linhas:
            print(f"  {l['metodo']:<26} n={l['total_jogos_conferidos']:<4} "
                  f"média={l['media_acertos']:<6} desvio={l['desvio_padrao_acertos']}")


if __name__ == "__main__":
    main()
