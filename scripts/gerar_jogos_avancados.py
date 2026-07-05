"""
Gera os métodos avançados M6, M7 e M8 para a Lotofácil.

Este script usa a lógica central de `lotofacil_lib.py`, a mesma usada pelo
ciclo diário local. No site online, a versão equivalente roda em `worker.js`.
"""
import random

import lotofacil_lib as lib


METODOS_AVANCADOS = {
    "M6_filtros_combinados": lib.metodo_filtros_combinados,
    "M7_cobertura_pares": lib.metodo_cobertura_pares,
    "M8_repeticao_controlada": lib.metodo_repeticao_controlada,
}


def gerar_jogos_avancados(seed=None, ate_concurso=None):
    rng = random.Random(seed)
    resultados = lib._resultados_como_sets(ate_concurso)
    return {
        metodo: gerador(rng, resultados)
        for metodo, gerador in METODOS_AVANCADOS.items()
    }


if __name__ == "__main__":
    ultimo = lib.ultimo_concurso_registrado()
    jogos = gerar_jogos_avancados(seed=(ultimo or 0) + 1, ate_concurso=ultimo)
    for metodo, dezenas in jogos.items():
        dezenas_str = "-".join(f"{d:02d}" for d in sorted(dezenas))
        print(f"{metodo}: {dezenas_str}")
