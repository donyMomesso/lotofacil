"""
Confere os jogos que tinham como alvo um concurso já sorteado, e grava
o resultado (nº de acertos) em dados/conferencia.csv.

Uso:
    python3 conferir_jogos.py <concurso>

O concurso precisa já estar registrado em dados/resultados_lotofacil.csv
(ver registrar_resultado.py).
"""
import sys

import lotofacil_lib as lib


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 conferir_jogos.py <concurso>")
        sys.exit(1)

    concurso = int(sys.argv[1])
    resultados = {r["concurso"]: r for r in lib.carregar_resultados()}
    if concurso not in resultados:
        print(f"Concurso {concurso} ainda não está registrado em resultados_lotofacil.csv. "
              f"Registre o resultado real primeiro.")
        sys.exit(1)

    dezenas_sorteadas = resultados[concurso]["dezenas"]
    data_sorteio = resultados[concurso]["data"]

    jogos = [j for j in lib.carregar_jogos() if j["concurso_alvo"] == concurso]
    if not jogos:
        print(f"Nenhum jogo gerado tinha o concurso {concurso} como alvo.")
        return

    conferidos = 0
    for j in jogos:
        acertos = lib.registrar_conferencia(
            concurso, data_sorteio, j["metodo"], j["dezenas_set"], dezenas_sorteadas
        )
        if acertos is not None:
            print(f"[ok] {j['metodo']}: {acertos} acerto(s) no concurso {concurso}")
            conferidos += 1
        else:
            print(f"[skip] {j['metodo']} já tinha sido conferido para o concurso {concurso}")

    print(f"\n{conferidos} conferência(s) nova(s) registrada(s) para o concurso {concurso}.")


if __name__ == "__main__":
    main()
