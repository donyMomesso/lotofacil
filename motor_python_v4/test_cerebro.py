"""Testes da fachada Cerebro."""
from __future__ import annotations

import random

from cerebro import CEREBRO_VERSION, Cerebro, saude
from engine import Concurso
from metodos import METODOS


def _historico(n: int = 40, seed: int = 5) -> list[Concurso]:
    rng = random.Random(seed)
    out = []
    for i in range(1, n + 1):
        dezenas = sorted(rng.sample(range(1, 26), 15))
        out.append(Concurso.criar(i, dezenas, f"2020-01-{i:02d}" if i <= 28 else None))
    return out


def test_saude():
    info = saude()
    assert info["status"] == "ok"
    assert info["source_of_truth"] == "python"
    assert info["cerebro_version"] == CEREBRO_VERSION
    assert len(info["metodos"]) == 9


def test_cerebro_metodos():
    c = Cerebro(_historico(), seed=42)
    jogos = c.gerar_metodos()
    assert set(jogos.keys()) == set(METODOS)
    for nome, info in jogos.items():
        assert len(info["dezenas"]) == 15, nome
        assert info["soma"] == sum(info["dezenas"])


def test_checkpoint_operacional():
    c = Cerebro(_historico(50), seed=7)
    ck = c.checkpoint_operacional(concurso_alvo=51)
    assert ck["ok"] is True
    assert ck["source_of_truth"] == "python"
    assert ck["concurso_alvo"] == 51
    assert ck["ultimo_concurso"] == 50
    assert "checkpoint_hash" in ck
    assert len(ck["jogos_estudo"]) == 9
    assert "aviso" in ck


def test_checkpoint_com_fechamento():
    c = Cerebro(_historico(35), seed=3)
    ck = c.checkpoint_operacional(incluir_fechamento=True, tamanho_base=16, quantidade_fechamento=5)
    assert "fechamento_estudo" in ck
    fe = ck["fechamento_estudo"]
    assert len(fe["base"]) == 16
    assert len(fe["jogos"]) <= 5
    assert fe["cobertura_nominal_pct"] >= 0


def test_pontuar_e_fechamento():
    c = Cerebro(_historico(30), seed=1)
    ranking, componentes = c.pontuar_dezenas()
    assert len(ranking) == 25
    assert len(componentes) == 25
    geracao = c.gerar_fechamento(tamanho_base=16, quantidade=8)
    assert len(geracao.base) == 16
    assert len(geracao.jogos) <= 8
