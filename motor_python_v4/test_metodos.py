"""Testes do núcleo unificado de métodos."""
from __future__ import annotations

import random

from metodos import (
    METODOS,
    ESPERANCA_TEORICA,
    frequencia_e_atraso,
    gerar_todos_metodos,
    metodo_aleatorio_puro,
    metodo_mais_atrasadas,
    metodo_mais_frequentes,
    metodo_par_impar_balanceado,
    metodo_soma_faixa_comum,
    metodo_tese_v2,
    resumo_jogo,
)


def _hist_fake(n: int = 40, seed: int = 1) -> list[set[int]]:
    rng = random.Random(seed)
    return [set(rng.sample(range(1, 26), 15)) for _ in range(n)]


def test_esperanca_teorica():
    assert ESPERANCA_TEORICA == 9.0


def test_metodos_lista_completa():
    assert len(METODOS) == 9
    assert "M9_tese_v2" in METODOS


def test_aleatorio_valido():
    jogo = metodo_aleatorio_puro(random.Random(42))
    assert len(jogo) == 15
    assert all(1 <= d <= 25 for d in jogo)


def test_frequencia_atraso():
    hist = _hist_fake(20)
    freq, atraso, total = frequencia_e_atraso(hist)
    assert total == 20
    assert len(freq) == 25
    assert len(atraso) == 25
    assert all(v >= 0 for v in atraso.values())


def test_mais_frequentes_e_atrasadas():
    hist = _hist_fake(30)
    freq, atraso, _ = frequencia_e_atraso(hist)
    j2 = metodo_mais_frequentes(freq, random.Random(7))
    j3 = metodo_mais_atrasadas(atraso, random.Random(7))
    assert len(j2) == 15 and len(j3) == 15


def test_par_impar_e_soma():
    j4 = metodo_par_impar_balanceado(random.Random(3), alvo_pares=8)
    assert sum(1 for d in j4 if d % 2 == 0) == 8
    j5 = metodo_soma_faixa_comum(random.Random(3), 180, 210)
    assert 180 <= sum(j5) <= 210


def test_tese_v2_estrutura():
    hist = _hist_fake(50)
    _, atraso, _ = frequencia_e_atraso(hist)
    j9 = metodo_tese_v2(atraso, random.Random(11))
    assert len(j9) == 15
    # Preferência de soma; fallback pode sair da faixa
    assert all(1 <= d <= 25 for d in j9)


def test_gerar_todos_metodos():
    hist = _hist_fake(60)
    jogos = gerar_todos_metodos(hist, seed=99)
    assert set(jogos.keys()) == set(METODOS)
    for nome, dezenas in jogos.items():
        assert len(dezenas) == 15, nome
        r = resumo_jogo(dezenas)
        assert r["soma"] == sum(dezenas)
        assert r["pares"] + r["impares"] == 15


def test_reprodutibilidade_seed():
    hist = _hist_fake(25, seed=2)
    a = gerar_todos_metodos(hist, seed=12345)
    b = gerar_todos_metodos(hist, seed=12345)
    assert a == b
