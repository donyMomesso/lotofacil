"""
Métodos avançados M6, M7 e M8 para o Laboratório Lotofácil.

O módulo pode ser executado diretamente pelo terminal ou importado por outros
scripts. Ele usa o histórico oficial em dados/resultados_lotofacil.csv por meio
da função carregar_resultados() de lotofacil_lib.py.

Importante: estes métodos são hipóteses estatísticas educacionais. Eles não
alteram a probabilidade matemática de um jogo simples da Lotofácil.
"""
from __future__ import annotations

import random
from itertools import combinations
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from lotofacil_lib import carregar_resultados


TODAS_DEZENAS = list(range(1, 26))
NUM_JOGOS_GERAR = 1500
TOP_JOGOS_SELECIONAR = 5
TOTAL_PARES_POSSIVEIS = 300
PARES_POR_JOGO = 105

SOMA_MIN = 185
SOMA_MAX = 215
SOMA_ALVO = 200
PARES_MIN = 7
PARES_MAX = 9
REPETICOES_MIN = 8
REPETICOES_MAX = 11
COBERTURA_PAIRES_RECENTES = 30
MIN_PARES_COBERTOS = 8

Jogo = List[int]
Resultados = List[List[int]]
Par = Tuple[int, int]


def dezenas_do_resultado(resultado) -> Jogo:
    """Aceita resultado completo (dict) ou lista de dezenas e retorna dezenas ordenadas."""
    if isinstance(resultado, dict):
        return sorted(resultado["dezenas"])
    return sorted(resultado)


def carregar_resultados_dezenas(ate_concurso: Optional[int] = None) -> Resultados:
    """Carrega o histórico como lista de listas de dezenas em ordem crescente."""
    resultados = carregar_resultados()
    if ate_concurso is not None:
        resultados = [r for r in resultados if r["concurso"] <= ate_concurso]
    return [dezenas_do_resultado(r) for r in resultados]


def gerar_jogo_aleatorio(rng: random.Random) -> Jogo:
    """Gera um jogo simples com 15 dezenas únicas."""
    return sorted(rng.sample(TODAS_DEZENAS, 15))


def calcular_soma(jogo: Sequence[int]) -> int:
    """Calcula a soma das dezenas do jogo."""
    return sum(jogo)


def contar_pares(jogo: Sequence[int]) -> int:
    """Conta quantas dezenas pares existem no jogo."""
    return sum(1 for dezena in jogo if dezena % 2 == 0)


def contar_repeticoes(jogo: Sequence[int], resultado_anterior: Sequence[int]) -> int:
    """Conta quantas dezenas do jogo repetem o concurso anterior."""
    return len(set(jogo) & set(resultado_anterior))


def calcular_pares_recentes(
    resultados: Resultados,
    n_concursos: int = COBERTURA_PAIRES_RECENTES,
) -> Set[Par]:
    """Retorna todos os pares que apareceram juntos nos últimos concursos."""
    pares: Set[Par] = set()
    for resultado in resultados[-n_concursos:]:
        for a, b in combinations(dezenas_do_resultado(resultado), 2):
            pares.add((a, b))
        if len(pares) == TOTAL_PARES_POSSIVEIS:
            break
    return pares


def contar_cobertura_pares(jogo: Sequence[int], pares_recentes: Set[Par]) -> int:
    """Conta quantos pares recentes estão cobertos pelo jogo candidato."""
    if len(pares_recentes) == TOTAL_PARES_POSSIVEIS:
        return PARES_POR_JOGO
    return sum(1 for par in combinations(sorted(jogo), 2) if par in pares_recentes)


def calcular_score(
    jogo: Sequence[int],
    pares_recentes: Set[Par],
    resultado_anterior: Sequence[int],
) -> float:
    """
    Calcula um score composto para ranquear jogos.

    O score valoriza soma próxima de 200, equilíbrio par/ímpar, repetição
    controlada do concurso anterior e cobertura de pares recentes. Também aplica
    penalidades quando soma e pares ficam em zonas muito extremas.
    """
    soma = calcular_soma(jogo)
    pares = contar_pares(jogo)
    repeticoes = contar_repeticoes(jogo, resultado_anterior)
    cobertura = contar_cobertura_pares(jogo, pares_recentes)
    score = 0.0

    distancia_soma = abs(soma - SOMA_ALVO)
    score += max(0.0, 20.0 * (1 - distancia_soma / 45))
    if SOMA_MIN <= soma <= SOMA_MAX:
        score += 10.0

    if PARES_MIN <= pares <= PARES_MAX:
        score += 10.0
    else:
        score -= abs(pares - 8) * 2.5

    if REPETICOES_MIN <= repeticoes <= REPETICOES_MAX:
        score += 14.0
        score += max(0, repeticoes - 8) * 1.5
    else:
        score -= abs(repeticoes - 9.5) * 2.0

    if cobertura >= MIN_PARES_COBERTOS:
        score += 12.0 + (cobertura - MIN_PARES_COBERTOS) * 0.25
    else:
        score -= (MIN_PARES_COBERTOS - cobertura) * 0.5

    if soma < 170 or soma > 230:
        score -= 25.0
    if pares < 6 or pares > 10:
        score -= 12.0

    return score


def selecionar_top_jogos(
    candidatos: Iterable[Jogo],
    pares_recentes: Set[Par],
    resultado_anterior: Sequence[int],
    limite: int = TOP_JOGOS_SELECIONAR,
) -> List[Jogo]:
    """Remove duplicados, ranqueia por score e retorna os melhores jogos."""
    vistos = set()
    ranqueados = []

    for jogo in candidatos:
        chave = tuple(sorted(jogo))
        if chave in vistos:
            continue
        vistos.add(chave)
        score = calcular_score(jogo, pares_recentes, resultado_anterior)
        ranqueados.append((score, list(chave)))

    ranqueados.sort(key=lambda item: item[0], reverse=True)
    return [jogo for _, jogo in ranqueados[:limite]]


def completar_top_jogos(
    jogos: List[Jogo],
    rng: random.Random,
    pares_recentes: Set[Par],
    resultado_anterior: Sequence[int],
    filtro: Optional[Callable[[Jogo], bool]] = None,
) -> List[Jogo]:
    """Garante que cada método retorne exatamente cinco jogos."""
    candidatos = list(jogos)
    tentativas = 0
    while len(candidatos) < TOP_JOGOS_SELECIONAR and tentativas < NUM_JOGOS_GERAR * 3:
        tentativas += 1
        jogo = gerar_jogo_aleatorio(rng)
        if filtro is None or filtro(jogo):
            candidatos.append(jogo)

    if len(candidatos) < TOP_JOGOS_SELECIONAR:
        candidatos.extend(gerar_jogo_aleatorio(rng) for _ in range(TOP_JOGOS_SELECIONAR))

    return selecionar_top_jogos(
        candidatos,
        pares_recentes,
        resultado_anterior,
        limite=TOP_JOGOS_SELECIONAR,
    )


def metodo_m6_filtros_combinados(
    resultados: Resultados,
    rng: Optional[random.Random] = None,
) -> List[Jogo]:
    """
    M6: gera 1500 jogos e filtra por soma, pares e repetições simultaneamente.

    Critérios:
    - soma entre 185 e 215;
    - 7 a 9 dezenas pares;
    - 8 a 11 dezenas repetidas do concurso anterior.
    """
    rng = rng or random.Random()
    resultado_anterior = dezenas_do_resultado(resultados[-1]) if resultados else []
    pares_recentes = calcular_pares_recentes(resultados)

    def filtro(jogo: Jogo) -> bool:
        return (
            SOMA_MIN <= calcular_soma(jogo) <= SOMA_MAX
            and PARES_MIN <= contar_pares(jogo) <= PARES_MAX
            and REPETICOES_MIN <= contar_repeticoes(jogo, resultado_anterior) <= REPETICOES_MAX
        )

    candidatos = [
        jogo
        for jogo in (gerar_jogo_aleatorio(rng) for _ in range(NUM_JOGOS_GERAR))
        if filtro(jogo)
    ]
    top = selecionar_top_jogos(candidatos, pares_recentes, resultado_anterior)
    return completar_top_jogos(top, rng, pares_recentes, resultado_anterior, filtro)


def metodo_m7_cobertura_pares(
    resultados: Resultados,
    rng: Optional[random.Random] = None,
) -> List[Jogo]:
    """M7: gera 1500 jogos e ranqueia pela cobertura de pares recentes."""
    rng = rng or random.Random()
    resultado_anterior = dezenas_do_resultado(resultados[-1]) if resultados else []
    pares_recentes = calcular_pares_recentes(resultados)
    candidatos = [gerar_jogo_aleatorio(rng) for _ in range(NUM_JOGOS_GERAR)]
    return selecionar_top_jogos(candidatos, pares_recentes, resultado_anterior)


def metodo_m8_repeticao_controlada(
    resultados: Resultados,
    rng: Optional[random.Random] = None,
) -> List[Jogo]:
    """M8: gera 1500 jogos e mantém apenas os com 9, 10 ou 11 repetições."""
    rng = rng or random.Random()
    resultado_anterior = dezenas_do_resultado(resultados[-1]) if resultados else []
    pares_recentes = calcular_pares_recentes(resultados)

    def filtro(jogo: Jogo) -> bool:
        repeticoes = contar_repeticoes(jogo, resultado_anterior)
        return repeticoes in {9, 10, 11}

    candidatos = [
        jogo
        for jogo in (gerar_jogo_aleatorio(rng) for _ in range(NUM_JOGOS_GERAR))
        if filtro(jogo)
    ]
    top = selecionar_top_jogos(candidatos, pares_recentes, resultado_anterior)
    return completar_top_jogos(top, rng, pares_recentes, resultado_anterior, filtro)


def gerar_jogos_avancados(
    seed: Optional[int] = None,
    ate_concurso: Optional[int] = None,
) -> Dict[str, List[Jogo]]:
    """Gera os jogos avançados M6, M7 e M8, com cinco jogos por método."""
    resultados = carregar_resultados_dezenas(ate_concurso=ate_concurso)
    rng = random.Random(seed)
    return {
        "M6_filtros_combinados": metodo_m6_filtros_combinados(resultados, rng),
        "M7_cobertura_pares": metodo_m7_cobertura_pares(resultados, rng),
        "M8_repeticao_controlada": metodo_m8_repeticao_controlada(resultados, rng),
    }


def formatar_jogo(jogo: Sequence[int]) -> str:
    """Formata dezenas no padrão 01-02-03."""
    return "-".join(f"{dezena:02d}" for dezena in sorted(jogo))


if __name__ == "__main__":
    jogos_por_metodo = gerar_jogos_avancados()
    for metodo, jogos in jogos_por_metodo.items():
        print(f"\n=== {metodo} ===")
        for indice, jogo in enumerate(jogos, start=1):
            print(f"Jogo {indice}: {formatar_jogo(jogo)}")
