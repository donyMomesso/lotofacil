"""
Métodos de estudo M1–M9 — fonte única da verdade.

Cada função é uma hipótese estatística neutra. Nenhum método é avaliado
como preditor de 14/15 acertos. A esperança teórica permanece 9,0
(distribuição hipergeométrica: N=25, K=15, n=15).
"""
from __future__ import annotations

import itertools
import random
from collections import Counter
from typing import Sequence

TODAS_DEZENAS = list(range(1, 26))
ESPERANCA_TEORICA = 9.0

METODOS = [
    "M1_aleatorio_puro",
    "M2_mais_frequentes",
    "M3_mais_atrasadas",
    "M4_par_impar_balanceado",
    "M5_soma_faixa_comum",
    "M6_filtros_combinados",
    "M7_cobertura_pares",
    "M8_repeticao_controlada",
    "M9_tese_v2",
]

NUM_CANDIDATOS_AVANCADOS = 1500
SOMA_AVANCADA_MIN = 185
SOMA_AVANCADA_MAX = 215
PARES_AVANCADO_MIN = 7
PARES_AVANCADO_MAX = 9
REPETICOES_MIN = 8
REPETICOES_MAX = 11
COBERTURA_PARES_RECENTES = 30
MIN_PARES_COBERTOS = 8

# Tese V2 (hipótese baseada em observação real limitada — validar via governança)
SOMA_TESE_V2_MIN = 180
SOMA_TESE_V2_MAX = 190
PARES_TESE_V2 = 7


def _rng(rng: random.Random | None) -> random.Random:
    return rng if rng is not None else random.Random()


def frequencia_e_atraso(
    resultados: Sequence[set[int] | frozenset[int] | Sequence[int]],
) -> tuple[Counter, dict[int, int], int]:
    """Frequência absoluta e atraso (concursos desde a última aparição)."""
    sets = [set(r) for r in resultados]
    freq: Counter = Counter()
    ultima: dict[int, int] = {}
    for idx, dezenas in enumerate(sets):
        for d in dezenas:
            freq[d] += 1
            ultima[d] = idx
    total = len(sets)
    atraso = {
        d: (total - 1 - ultima[d]) if d in ultima else total
        for d in TODAS_DEZENAS
    }
    for d in TODAS_DEZENAS:
        freq.setdefault(d, 0)
    return freq, atraso, total


def metodo_aleatorio_puro(rng: random.Random | None = None) -> set[int]:
    r = _rng(rng)
    return set(r.sample(TODAS_DEZENAS, 15))


def metodo_mais_frequentes(freq: Counter, rng: random.Random | None = None) -> set[int]:
    r = _rng(rng)
    dezenas = TODAS_DEZENAS[:]
    r.shuffle(dezenas)
    dezenas.sort(key=lambda d: freq[d], reverse=True)
    return set(dezenas[:15])


def metodo_mais_atrasadas(atraso: dict[int, int], rng: random.Random | None = None) -> set[int]:
    r = _rng(rng)
    dezenas = TODAS_DEZENAS[:]
    r.shuffle(dezenas)
    dezenas.sort(key=lambda d: atraso[d], reverse=True)
    return set(dezenas[:15])


def metodo_par_impar_balanceado(
    rng: random.Random | None = None,
    alvo_pares: int = 8,
    max_tentativas: int = 500,
) -> set[int]:
    r = _rng(rng)
    for _ in range(max_tentativas):
        candidato = r.sample(TODAS_DEZENAS, 15)
        if sum(1 for d in candidato if d % 2 == 0) == alvo_pares:
            return set(candidato)
    return metodo_aleatorio_puro(r)


def metodo_soma_faixa_comum(
    rng: random.Random | None = None,
    faixa_min: int = 180,
    faixa_max: int = 210,
    max_tentativas: int = 1000,
) -> set[int]:
    r = _rng(rng)
    for _ in range(max_tentativas):
        candidato = r.sample(TODAS_DEZENAS, 15)
        if faixa_min <= sum(candidato) <= faixa_max:
            return set(candidato)
    return metodo_aleatorio_puro(r)


def _pares_recentes(resultados: Sequence[set[int]], n: int = COBERTURA_PARES_RECENTES) -> set[tuple[int, int]]:
    pares: set[tuple[int, int]] = set()
    for resultado in resultados[-n:]:
        for a, b in itertools.combinations(sorted(resultado), 2):
            pares.add((a, b))
    return pares


def _contar_repeticoes(jogo: set[int], anterior: set[int]) -> int:
    return len(jogo & anterior)


def _cobertura_pares_adjacentes(jogo: set[int], pares_recentes: set[tuple[int, int]]) -> int:
    ordenado = sorted(jogo)
    return sum(
        1 for a, b in zip(ordenado, ordenado[1:])
        if (min(a, b), max(a, b)) in pares_recentes
    )


def _score_avancado(
    jogo: set[int],
    pares_recentes: set[tuple[int, int]],
    anterior: set[int],
) -> float:
    soma = sum(jogo)
    pares = sum(1 for d in jogo if d % 2 == 0)
    repeticoes = _contar_repeticoes(jogo, anterior)
    cobertura = _cobertura_pares_adjacentes(jogo, pares_recentes)
    score = 0.0
    if SOMA_AVANCADA_MIN <= soma <= SOMA_AVANCADA_MAX:
        score += 10
        score += 10 * (1 - abs(soma - 200) / 30)
    if PARES_AVANCADO_MIN <= pares <= PARES_AVANCADO_MAX:
        score += 8
    if REPETICOES_MIN <= repeticoes <= REPETICOES_MAX:
        score += 12
        score += (repeticoes - 7) * 1.5
    if cobertura >= MIN_PARES_COBERTOS:
        score += 15 + (cobertura - MIN_PARES_COBERTOS) * 2
    if soma < 170 or soma > 230:
        score -= 20
    if pares < 6 or pares > 10:
        score -= 10
    return max(0.0, score)


def _melhor_candidato_avancado(
    resultados: Sequence[set[int]],
    rng: random.Random | None = None,
    filtro=None,
    max_tentativas: int = NUM_CANDIDATOS_AVANCADOS,
) -> set[int]:
    r = _rng(rng)
    if not resultados:
        return metodo_aleatorio_puro(r)
    anterior = resultados[-1]
    pares_recentes = _pares_recentes(resultados)
    melhor: set[int] | None = None
    melhor_score = -1.0
    for _ in range(max_tentativas):
        candidato = set(r.sample(TODAS_DEZENAS, 15))
        if filtro and not filtro(candidato, anterior):
            continue
        score = _score_avancado(candidato, pares_recentes, anterior)
        if score > melhor_score:
            melhor = candidato
            melhor_score = score
    return melhor or metodo_aleatorio_puro(r)


def metodo_filtros_combinados(
    resultados: Sequence[set[int]],
    rng: random.Random | None = None,
) -> set[int]:
    def filtro(jogo: set[int], anterior: set[int]) -> bool:
        soma = sum(jogo)
        pares = sum(1 for d in jogo if d % 2 == 0)
        repeticoes = _contar_repeticoes(jogo, anterior)
        return (
            SOMA_AVANCADA_MIN <= soma <= SOMA_AVANCADA_MAX
            and PARES_AVANCADO_MIN <= pares <= PARES_AVANCADO_MAX
            and REPETICOES_MIN <= repeticoes <= REPETICOES_MAX
        )
    return _melhor_candidato_avancado(resultados, rng, filtro=filtro)


def metodo_cobertura_pares(
    resultados: Sequence[set[int]],
    rng: random.Random | None = None,
) -> set[int]:
    return _melhor_candidato_avancado(resultados, rng)


def metodo_repeticao_controlada(
    resultados: Sequence[set[int]],
    rng: random.Random | None = None,
) -> set[int]:
    def filtro(jogo: set[int], anterior: set[int]) -> bool:
        return 9 <= _contar_repeticoes(jogo, anterior) <= 11
    return _melhor_candidato_avancado(resultados, rng, filtro=filtro)


def metodo_tese_v2(
    atraso: dict[int, int],
    rng: random.Random | None = None,
) -> set[int]:
    """
    M9 — hipótese Tese V2 (soma 180–190, pares=7, favorece atrasadas).
    Amostra real ainda pequena: só promover via governança Champion×Challenger.
    """
    r = _rng(rng)
    ordenadas = sorted(TODAS_DEZENAS, key=lambda d: atraso[d], reverse=True)
    for _ in range(1000):
        candidato = r.sample(ordenadas, 15)
        soma = sum(candidato)
        pares = sum(1 for d in candidato if d % 2 == 0)
        if SOMA_TESE_V2_MIN <= soma <= SOMA_TESE_V2_MAX and pares == PARES_TESE_V2:
            return set(candidato)
    for _ in range(500):
        candidato = r.sample(ordenadas, 15)
        soma = sum(candidato)
        pares = sum(1 for d in candidato if d % 2 == 0)
        if SOMA_TESE_V2_MIN <= soma <= SOMA_TESE_V2_MAX and 6 <= pares <= 8:
            return set(candidato)
    return metodo_mais_atrasadas(atraso, r)


def gerar_todos_metodos(
    resultados: Sequence[set[int] | frozenset[int] | Sequence[int]],
    seed: int | None = None,
) -> dict[str, set[int]]:
    """Gera um jogo de 15 dezenas por método usando só o histórico informado."""
    rng = random.Random(seed)
    sets = [set(r) for r in resultados]
    freq, atraso, _ = frequencia_e_atraso(sets)
    return {
        "M1_aleatorio_puro": metodo_aleatorio_puro(rng),
        "M2_mais_frequentes": metodo_mais_frequentes(freq, rng),
        "M3_mais_atrasadas": metodo_mais_atrasadas(atraso, rng),
        "M4_par_impar_balanceado": metodo_par_impar_balanceado(rng),
        "M5_soma_faixa_comum": metodo_soma_faixa_comum(rng),
        "M6_filtros_combinados": metodo_filtros_combinados(sets, rng),
        "M7_cobertura_pares": metodo_cobertura_pares(sets, rng),
        "M8_repeticao_controlada": metodo_repeticao_controlada(sets, rng),
        "M9_tese_v2": metodo_tese_v2(atraso, rng),
    }


def resumo_jogo(dezenas: set[int] | Sequence[int]) -> dict:
    ds = sorted(set(int(d) for d in dezenas))
    pares = sum(1 for d in ds if d % 2 == 0)
    return {
        "dezenas": ds,
        "dezenas_str": "-".join(f"{d:02d}" for d in ds),
        "soma": sum(ds),
        "pares": pares,
        "impares": 15 - pares,
    }
