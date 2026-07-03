"""
Gera os jogos fictícios do dia (um por método) para o próximo concurso
ainda não sorteado, e grava em dados/jogos_gerados.csv.

Uso:
    python3 gerar_jogos.py [concurso_alvo]

Se concurso_alvo não for informado, usa (último concurso registrado + 1).

Isto é um exercício estatístico. Nenhum dos métodos é uma recomendação
de aposta, e nenhum deles é reportado como "mais perto de acertar".
"""
import sys
from datetime import datetime, timezone, timedelta

import lotofacil_lib as lib

BRASILIA = timezone(timedelta(hours=-3))


def main():
    if len(sys.argv) > 1:
        concurso_alvo = int(sys.argv[1])
    else:
        ultimo = lib.ultimo_concurso_registrado()
        concurso_alvo = (ultimo + 1) if ultimo else 1

    data_geracao = datetime.now(BRASILIA).strftime("%d/%m/%Y")

    jogos = lib.gerar_todos_metodos(ate_concurso=concurso_alvo - 1)

    gerados = []
    for metodo, dezenas in jogos.items():
        if lib.jogo_ja_gerado(concurso_alvo, metodo):
            print(f"[skip] {metodo} já gerado para concurso {concurso_alvo}")
            continue
        lib.registrar_jogo(data_geracao, concurso_alvo, metodo, dezenas)
        gerados.append((metodo, sorted(dezenas)))
        print(f"[ok] {metodo} -> {'-'.join(f'{d:02d}' for d in sorted(dezenas))}")

    if not gerados:
        print(f"Nenhum jogo novo gerado (concurso {concurso_alvo} já tinha os 5 métodos).")
    else:
        print(f"\n{len(gerados)} jogo(s) gerado(s) para o concurso {concurso_alvo} (data: {data_geracao}).")


if __name__ == "__main__":
    main()
