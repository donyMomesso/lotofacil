"""
Métodos de estudo M1–M9 — fonte única da verdade.

Cada função é uma hipótese estatística neutra. Nenhum método é avaliado
como preditor de 14/15 acertos. A esperança teórica permanece 9,0
(distribuição hipergeométrica: N=25, K=15, n=15).

v2.1: seed amarrada ao concurso_alvo, anti-overlap entre jogos e
perfis inspirados no lab (miolo/moldura, início 01/02).
"""
from __future__ import annotations

import itertools
import random
from collections import Counter
from typing import Sequence

TODAS_DEZENAS = list(range(1, 26))
ESPERANCA_TEORICA = 9.0

# Overlap máximo permitido entre dois jogos da carteira (15 dezenas).
# 11 = ainda parecidos; acima disso quase o mesmo bilhete.
MAX_OVERLAP = 11

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

NUM_CANDIDATOS_AVANCADOS = 1800
SOMA_AVANCADA_MIN = 185
SOMA_AVANCADA_MAX = 215
PARES_AVANCADO_MIN = 7
PARES_AVANCADO_MAX = 9
REPETICOES_MIN = 8
REPETICOES_MAX = 11
COBERTURA_PARES_RECENTES = 30
MIN_PARES_COBERTOS = 8

SOMA_TESE_V2_MIN = 180
SOMA_TESE_V2_MAX = 190
PARES_TESE_V2 = 7

MOLDURA = {1, 2, 3, 4, 5, 21, 22, 23, 24, 25}
MIOLO = set(range(6, 21))


def seed_para_concurso(concurso_alvo: int, seed_base: int | None = None) -> int:
    """Seed determinística e distinta por concurso (evita jogo idêntico todo dia)."""
    base = int(seed_base if seed_base is not None else 20260728)
    c = int(concurso_alvo or 0)
    # mistura linear congruente simples, estável entre Python runs
    return (base ^ (c * 1_000_003) ^ (c * c * 97) ^ 0x9E3779B9) & 0x7FFFFFFF


def _rng(rng: random.Random | None) -> random.Random:
    return rng if rng is not None else random.Random()


def frequencia_e_atraso(
    resultados: Sequence[set[int] | frozenset[int] | Sequence[int]],
) -> tuple[Counter, dict[int, int], int]:
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
    dezenas.sort(key=lambda d: (freq[d], r.random()), reverse=True)
    return set(dezenas[:15])


def metodo_mais_atrasadas(atraso: dict[int, int], rng: random.Random | None = None) -> set[int]:
    r = _rng(rng)
    dezenas = TODAS_DEZENAS[:]
    r.shuffle(dezenas)
    dezenas.sort(key=lambda d: (atraso[d], r.random()), reverse=True)
    return set(dezenas[:15])


def metodo_par_impar_balanceado(
    rng: random.Random | None = None,
    alvo_pares: int = 8,
    max_tentativas: int = 800,
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
    max_tentativas: int = 1200,
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


def metodo_miolo_moldura(
    freq: Counter,
    rng: random.Random | None = None,
    n_moldura: int = 6,
) -> set[int]:
    """Perfil lab: mistura moldura (1–5, 21–25) + miolo (6–20), com leve peso de frequência."""
    r = _rng(rng)
    n_moldura = max(4, min(8, n_moldura))
    n_miolo = 15 - n_moldura
    moldura_ord = sorted(MOLDURA, key=lambda d: (freq[d], r.random()), reverse=True)
    miolo_ord = sorted(MIOLO, key=lambda d: (freq[d], r.random()), reverse=True)
    # jitter: às vezes prioriza atraso na moldura
    if r.random() < 0.35:
        moldura_pool = list(MOLDURA)
        r.shuffle(moldura_pool)
        escolhidas = set(moldura_pool[:n_moldura])
    else:
        escolhidas = set(moldura_ord[:n_moldura])
    resto_miolo = [d for d in miolo_ord if d not in escolhidas]
    escolhidas.update(resto_miolo[:n_miolo])
    while len(escolhidas) < 15:
        d = r.choice(TODAS_DEZENAS)
        escolhidas.add(d)
    return set(list(escolhidas)[:15]) if len(escolhidas) > 15 else escolhidas


def metodo_inicio_01_02(
    freq: Counter,
    atraso: dict[int, int],
    rng: random.Random | None = None,
) -> set[int]:
    """Perfil lab: ancora em 01 e/ou 02 + complementos por frequência/atraso."""
    r = _rng(rng)
    base = {1, 2}
    candidatos = [d for d in TODAS_DEZENAS if d not in base]
    r.shuffle(candidatos)
    candidatos.sort(key=lambda d: (0.6 * freq[d] + 0.4 * atraso[d], r.random()), reverse=True)
    escolhidas = set(base)
    for d in candidatos:
        if len(escolhidas) >= 15:
            break
        escolhidas.add(d)
    return escolhidas


def _max_overlap_com(jogo: set[int], carteira: list[set[int]]) -> int:
    if not carteira:
        return 0
    return max(len(jogo & outro) for outro in carteira)


def _reescrever_com_diversidade(
    nome: str,
    atual: set[int],
    carteira: list[set[int]],
    resultados: list[set[int]],
    freq: Counter,
    atraso: dict[int, int],
    rng: random.Random,
    max_overlap: int = MAX_OVERLAP,
    tentativas: int = 400,
) -> set[int]:
    """Se overlap alto, tenta novo candidato do mesmo 'espírito' do método."""
    if _max_overlap_com(atual, carteira) <= max_overlap:
        return atual

    anterior = resultados[-1] if resultados else set()

    def gera() -> set[int]:
        if nome.startswith("M1"):
            return metodo_aleatorio_puro(rng)
        if nome.startswith("M2"):
            return metodo_mais_frequentes(freq, rng)
        if nome.startswith("M3"):
            return metodo_mais_atrasadas(atraso, rng)
        if nome.startswith("M4"):
            return metodo_par_impar_balanceado(rng)
        if nome.startswith("M5"):
            return metodo_soma_faixa_comum(rng)
        if nome.startswith("M6"):
            return metodo_filtros_combinados(resultados, rng)
        if nome.startswith("M7"):
            # lab miolo no slot de cobertura quando precisa diversificar
            if rng.random() < 0.5:
                return metodo_miolo_moldura(freq, rng)
            return metodo_cobertura_pares(resultados, rng)
        if nome.startswith("M8"):
            if rng.random() < 0.4:
                return metodo_inicio_01_02(freq, atraso, rng)
            return metodo_repeticao_controlada(resultados, rng)
        if nome.startswith("M9"):
            return metodo_tese_v2(atraso, rng)
        return metodo_aleatorio_puro(rng)

    melhor = atual
    melhor_ov = _max_overlap_com(atual, carteira)
    for _ in range(tentativas):
        cand = gera()
        if len(cand) != 15:
            continue
        ov = _max_overlap_com(cand, carteira)
        if ov < melhor_ov:
            melhor = cand
            melhor_ov = ov
            if ov <= max_overlap:
                return melhor
    return melhor


def aplicar_anti_overlap(
    jogos: dict[str, set[int]],
    resultados: list[set[int]],
    freq: Counter,
    atraso: dict[int, int],
    rng: random.Random,
    max_overlap: int = MAX_OVERLAP,
) -> dict[str, set[int]]:
    """Garante que a carteira não seja quase cópia entre métodos."""
    ordem = [m for m in METODOS if m in jogos]
    carteira: list[set[int]] = []
    saida: dict[str, set[int]] = {}
    for nome in ordem:
        jogo = set(jogos[nome])
        jogo = _reescrever_com_diversidade(
            nome, jogo, carteira, resultados, freq, atraso, rng, max_overlap=max_overlap
        )
        saida[nome] = jogo
        carteira.append(jogo)
    return saida


def gerar_todos_metodos(
    resultados: Sequence[set[int] | frozenset[int] | Sequence[int]],
    seed: int | None = None,
    concurso_alvo: int | None = None,
    max_overlap: int = MAX_OVERLAP,
) -> dict[str, set[int]]:
    """
    Gera um jogo de 15 dezenas por método.

    - seed efetiva muda com concurso_alvo (carteira distinta a cada concurso)
    - anti-overlap reduz bilhetes quase iguais
    - M7/M8 podem puxar perfis lab (miolo / início 01-02) na diversificação
    """
    if concurso_alvo is not None:
        seed_efetiva = seed_para_concurso(concurso_alvo, seed)
    else:
        seed_efetiva = seed if seed is not None else 20260728

    rng = random.Random(seed_efetiva)
    sets = [set(r) for r in resultados]
    freq, atraso, _ = frequencia_e_atraso(sets)

    # RNG derivados por método (mesmo seed de concurso → streams independentes)
    def sub(i: int) -> random.Random:
        return random.Random(seed_efetiva + i * 7919)

    bruto = {
        "M1_aleatorio_puro": metodo_aleatorio_puro(sub(1)),
        "M2_mais_frequentes": metodo_mais_frequentes(freq, sub(2)),
        "M3_mais_atrasadas": metodo_mais_atrasadas(atraso, sub(3)),
        "M4_par_impar_balanceado": metodo_par_impar_balanceado(sub(4)),
        "M5_soma_faixa_comum": metodo_soma_faixa_comum(sub(5)),
        "M6_filtros_combinados": metodo_filtros_combinados(sets, sub(6)),
        # Lab profiles entram como M7/M8 base (ainda passam por anti-overlap)
        "M7_cobertura_pares": metodo_miolo_moldura(freq, sub(7)),
        "M8_repeticao_controlada": metodo_inicio_01_02(freq, atraso, sub(8)),
        "M9_tese_v2": metodo_tese_v2(atraso, sub(9)),
    }

    # Uma passagem extra de cobertura/repetição clássica se lab ficou fraco em diversidade
    # (anti-overlap já pode trocar M7/M8 de volta para clássicos)
    return aplicar_anti_overlap(bruto, sets, freq, atraso, rng, max_overlap=max_overlap)


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


def metricas_diversidade(jogos: dict[str, set[int]]) -> dict:
    nomes = list(jogos.keys())
    pares = []
    for i, a in enumerate(nomes):
        for b in nomes[i + 1 :]:
            ov = len(set(jogos[a]) & set(jogos[b]))
            pares.append({"a": a, "b": b, "overlap": ov})
    max_ov = max((p["overlap"] for p in pares), default=0)
    media_ov = sum(p["overlap"] for p in pares) / len(pares) if pares else 0.0
    return {
        "pares": pares,
        "max_overlap": max_ov,
        "media_overlap": round(media_ov, 2),
        "ok_diversidade": max_ov <= MAX_OVERLAP,
    }
