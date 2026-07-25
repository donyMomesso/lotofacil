"""Fechamento reduzido de 21 dezenas em jogos de 15 para a Lotofácil.

O módulo não prevê resultados. Ele organiza uma carteira de jogos e mede, de
forma exata, a cobertura condicional: quais pontuações seriam obtidas caso as
15 dezenas sorteadas estivessem dentro da base informada.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

TOTAL_BASE = 21
DEZENAS_POR_JOGO = 15
TOTAL_CENARIOS_21 = math.comb(TOTAL_BASE, DEZENAS_POR_JOGO)

Jogo = Tuple[int, ...]


@dataclass(frozen=True)
class RelatorioCobertura:
    tamanho_base: int
    quantidade_jogos: int
    cenarios_testados: int
    garantia_minima: int
    distribuicao_melhor_acerto: dict[int, int]
    qtd_15: int
    qtd_14_mais: int
    qtd_13_mais: int
    qtd_12_mais: int
    pct_15: float
    pct_14_mais: float
    pct_13_mais: float
    pct_12_mais: float
    condicao: str


def normalizar_dezenas(dezenas: Iterable[int], tamanho: int, nome: str) -> Jogo:
    valores = tuple(sorted(int(d) for d in dezenas))
    if len(valores) != tamanho:
        raise ValueError(f"{nome} deve conter exatamente {tamanho} dezenas.")
    if len(set(valores)) != tamanho:
        raise ValueError(f"{nome} não pode conter dezenas repetidas.")
    if any(d < 1 or d > 25 for d in valores):
        raise ValueError(f"{nome} deve usar somente dezenas entre 01 e 25.")
    return valores


def validar_base(base: Iterable[int]) -> Jogo:
    return normalizar_dezenas(base, TOTAL_BASE, "A base")


def validar_jogo(jogo: Iterable[int], base: Sequence[int] | None = None) -> Jogo:
    normalizado = normalizar_dezenas(jogo, DEZENAS_POR_JOGO, "O jogo")
    if base is not None and not set(normalizado).issubset(set(base)):
        raise ValueError("Todo jogo deve ser formado somente por dezenas da base.")
    return normalizado


def _mascara(jogo: Sequence[int], indice_base: dict[int, int]) -> int:
    mascara = 0
    for dezena in jogo:
        mascara |= 1 << indice_base[dezena]
    return mascara


def _score_individual(jogo: Sequence[int]) -> float:
    """Score suave; serve só para desempate, nunca como garantia."""
    soma = sum(jogo)
    pares = sum(1 for d in jogo if d % 2 == 0)
    primos = sum(1 for d in jogo if d in {2, 3, 5, 7, 11, 13, 17, 19, 23})
    moldura = sum(1 for d in jogo if d in {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25})

    score = 0.0
    score += max(0.0, 20.0 - abs(soma - 195) * 0.8)
    score += max(0.0, 12.0 - abs(pares - 7.5) * 3.0)
    score += max(0.0, 8.0 - abs(primos - 5.5) * 2.0)
    score += max(0.0, 8.0 - abs(moldura - 9.5) * 1.5)
    return score


def gerar_fechamento(
    base: Iterable[int],
    quantidade: int = 120,
    seed: int = 21,
    shortlist: int = 96,
    amostra_cenarios: int = 4096,
) -> List[List[int]]:
    """Gera uma carteira diversificada por busca gulosa.

    A seleção prioriza distância entre jogos e ganho de cobertura 13+ e 14+
    sobre uma amostra reprodutível dos 54.264 cenários. A garantia final deve
    sempre ser obtida por :func:`avaliar_fechamento`, que testa todos os
    cenários sem amostragem.
    """
    base_norm = validar_base(base)
    if quantidade < 1 or quantidade > TOTAL_CENARIOS_21:
        raise ValueError(f"A quantidade deve ficar entre 1 e {TOTAL_CENARIOS_21}.")

    todos_jogos: List[Jogo] = list(itertools.combinations(base_norm, DEZENAS_POR_JOGO))
    if quantidade == TOTAL_CENARIOS_21:
        return [list(jogo) for jogo in todos_jogos]

    indice_base = {dezena: indice for indice, dezena in enumerate(base_norm)}
    mascaras = [_mascara(jogo, indice_base) for jogo in todos_jogos]
    scores = [_score_individual(jogo) for jogo in todos_jogos]

    rng = random.Random(seed)
    indices_cenarios = list(range(len(todos_jogos)))
    if amostra_cenarios < len(indices_cenarios):
        indices_cenarios = rng.sample(indices_cenarios, max(256, amostra_cenarios))
    mascaras_cenarios = [mascaras[i] for i in indices_cenarios]
    melhores_amostra = [0] * len(mascaras_cenarios)

    primeiro = max(range(len(todos_jogos)), key=lambda i: (scores[i], -i))
    selecionados = [primeiro]
    selecionados_set = {primeiro}
    maior_sobreposicao = [(mascaras[i] & mascaras[primeiro]).bit_count() for i in range(len(mascaras))]
    for pos, mascara_cenario in enumerate(mascaras_cenarios):
        melhores_amostra[pos] = (mascara_cenario & mascaras[primeiro]).bit_count()

    while len(selecionados) < quantidade:
        candidatos = [i for i in range(len(todos_jogos)) if i not in selecionados_set]
        candidatos.sort(key=lambda i: (maior_sobreposicao[i], -scores[i], i))
        candidatos = candidatos[: max(8, shortlist)]

        melhor_indice = None
        melhor_chave = None
        for i in candidatos:
            mascara = mascaras[i]
            ganho_14 = 0
            ganho_13 = 0
            soma_melhorias = 0
            for atual, mascara_cenario in zip(melhores_amostra, mascaras_cenarios):
                acertos = (mascara & mascara_cenario).bit_count()
                if acertos > atual:
                    soma_melhorias += acertos - atual
                    if atual < 14 <= acertos:
                        ganho_14 += 1
                    if atual < 13 <= acertos:
                        ganho_13 += 1
            chave = (ganho_14, ganho_13, soma_melhorias, -maior_sobreposicao[i], scores[i], -i)
            if melhor_chave is None or chave > melhor_chave:
                melhor_chave = chave
                melhor_indice = i

        assert melhor_indice is not None
        selecionados.append(melhor_indice)
        selecionados_set.add(melhor_indice)
        mascara_escolhida = mascaras[melhor_indice]

        for i, mascara in enumerate(mascaras):
            if i not in selecionados_set:
                sobreposicao = (mascara & mascara_escolhida).bit_count()
                if sobreposicao > maior_sobreposicao[i]:
                    maior_sobreposicao[i] = sobreposicao

        for pos, mascara_cenario in enumerate(mascaras_cenarios):
            acertos = (mascara_cenario & mascara_escolhida).bit_count()
            if acertos > melhores_amostra[pos]:
                melhores_amostra[pos] = acertos

    return [list(todos_jogos[i]) for i in selecionados]


def avaliar_fechamento(base: Iterable[int], jogos: Iterable[Iterable[int]]) -> RelatorioCobertura:
    """Testa exatamente todos os 54.264 cenários internos da base."""
    base_norm = validar_base(base)
    jogos_norm = sorted({validar_jogo(jogo, base_norm) for jogo in jogos})
    if not jogos_norm:
        raise ValueError("É necessário informar pelo menos um jogo.")

    cenarios = list(itertools.combinations(base_norm, DEZENAS_POR_JOGO))
    if len(jogos_norm) == TOTAL_CENARIOS_21 and set(jogos_norm) == set(cenarios):
        distribuicao = {15: TOTAL_CENARIOS_21}
        return RelatorioCobertura(
            tamanho_base=TOTAL_BASE,
            quantidade_jogos=TOTAL_CENARIOS_21,
            cenarios_testados=TOTAL_CENARIOS_21,
            garantia_minima=15,
            distribuicao_melhor_acerto=distribuicao,
            qtd_15=TOTAL_CENARIOS_21,
            qtd_14_mais=TOTAL_CENARIOS_21,
            qtd_13_mais=TOTAL_CENARIOS_21,
            qtd_12_mais=TOTAL_CENARIOS_21,
            pct_15=100.0,
            pct_14_mais=100.0,
            pct_13_mais=100.0,
            pct_12_mais=100.0,
            condicao="As 15 dezenas sorteadas devem estar dentro das 21 dezenas da base.",
        )

    indice_base = {dezena: indice for indice, dezena in enumerate(base_norm)}
    mascaras_jogos = [_mascara(jogo, indice_base) for jogo in jogos_norm]
    distribuicao: dict[int, int] = {}

    for cenario in cenarios:
        mascara_cenario = _mascara(cenario, indice_base)
        melhor = max((mascara_cenario & mascara_jogo).bit_count() for mascara_jogo in mascaras_jogos)
        distribuicao[melhor] = distribuicao.get(melhor, 0) + 1

    total = len(cenarios)

    def qtd_minimo(alvo: int) -> int:
        return sum(qtd for acertos, qtd in distribuicao.items() if acertos >= alvo)

    qtd_15 = qtd_minimo(15)
    qtd_14 = qtd_minimo(14)
    qtd_13 = qtd_minimo(13)
    qtd_12 = qtd_minimo(12)

    return RelatorioCobertura(
        tamanho_base=TOTAL_BASE,
        quantidade_jogos=len(jogos_norm),
        cenarios_testados=total,
        garantia_minima=min(distribuicao),
        distribuicao_melhor_acerto=dict(sorted(distribuicao.items())),
        qtd_15=qtd_15,
        qtd_14_mais=qtd_14,
        qtd_13_mais=qtd_13,
        qtd_12_mais=qtd_12,
        pct_15=round(100 * qtd_15 / total, 4),
        pct_14_mais=round(100 * qtd_14 / total, 4),
        pct_13_mais=round(100 * qtd_13 / total, 4),
        pct_12_mais=round(100 * qtd_12 / total, 4),
        condicao="As 15 dezenas sorteadas devem estar dentro das 21 dezenas da base.",
    )


def salvar_resultado(caminho: str | Path, base: Sequence[int], jogos: Sequence[Sequence[int]], relatorio: RelatorioCobertura) -> None:
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    payload = {"base": list(base), "jogos": [list(jogo) for jogo in jogos], "relatorio": asdict(relatorio)}
    destino.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _parse_base(texto: str) -> List[int]:
    partes = texto.replace("-", ",").replace(" ", ",").split(",")
    return [int(parte) for parte in partes if parte.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera e valida fechamento reduzido 21→15.")
    parser.add_argument("--base", required=True, help="21 dezenas separadas por vírgula, espaço ou hífen.")
    parser.add_argument("--jogos", type=int, default=120, help="Quantidade de jogos da carteira.")
    parser.add_argument("--seed", type=int, default=21, help="Semente para reprodução do resultado.")
    parser.add_argument("--saida", default="dados/fechamento_21.json", help="Arquivo JSON de saída.")
    args = parser.parse_args()

    base = validar_base(_parse_base(args.base))
    jogos = gerar_fechamento(base, quantidade=args.jogos, seed=args.seed)
    relatorio = avaliar_fechamento(base, jogos)
    salvar_resultado(args.saida, base, jogos, relatorio)

    print(f"Base: {'-'.join(f'{d:02d}' for d in base)}")
    print(f"Jogos: {relatorio.quantidade_jogos}")
    print(f"Cenários testados: {relatorio.cenarios_testados}")
    print(f"Garantia mínima condicional: {relatorio.garantia_minima} pontos")
    print(f"Cobertura 15: {relatorio.qtd_15} ({relatorio.pct_15:.4f}%)")
    print(f"Cobertura 14+: {relatorio.qtd_14_mais} ({relatorio.pct_14_mais:.4f}%)")
    print(f"Cobertura 13+: {relatorio.qtd_13_mais} ({relatorio.pct_13_mais:.4f}%)")
    print(f"Arquivo salvo em: {args.saida}")


if __name__ == "__main__":
    main()
