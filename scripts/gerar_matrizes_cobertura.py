"""
gerar_matrizes_cobertura.py
=============================
Gera e verifica matrizes de cobertura reduzidas (covering designs) para o
fechamento com garantia de 14 pontos, para grupos de 16 a 20 dezenas -
substituindo a logica anterior (lotofacil_lib.desdobramento_total), que usava
itertools.combinations para gerar TODAS as C(v,15) combinacoes (16, 136, 816,
3.876 e 15.504 jogos para v=16..20). Isso e matematicamente correto para uma
"aposta estendida" (onde a Caixa cobra por todas as combinacoes de uma vez),
mas e um exagero enorme para um fechamento comum, onde o jogador compra varios
bilhetes separados de 15 dezenas e aceita uma garantia MENOR (14 em vez de 15
pontos) em troca de MUITO menos jogos.

Matematica do problema
----------------------
Jogar 15 das v dezenas do grupo equivale a EXCLUIR (v-15) delas. O mesmo vale
para "o sorteio, se caisse inteiro dentro do grupo" - tambem exclui (v-15)
dezenas do grupo. Dado um jogo G (exclui o conjunto excl(G)) e um sorteio
hipotetico D (exclui excl(D)), o numero de acertos e:

    acertos(G, D) = v - |excl(G) uniao excl(D)|

Como |A uniao B| = |A| + |B| - |A intersecao B| e |excl(G)| = |excl(D)| = v-15:

    acertos(G, D) = v - 2*(v-15) + |excl(G) intersecao excl(D)|
                  = 15 - (v-15) + |excl(G) intersecao excl(D)|

Para garantir acertos(G, D) >= 14 precisamos de:

    |excl(G) intersecao excl(D)| >= (v - 15) - (15 - 14) + ...

(a derivacao completa esta em `intersecao_minima()` abaixo). Isso transforma o
problema em: escolher o MENOR numero de conjuntos de exclusao (jogos) tal que
TODO conjunto de exclusao possivel (sorteio hipotetico) tenha intersecao
suficiente com pelo menos um deles. Isso e resolvido por um algoritmo guloso
(greedy set cover) seguido de poda de jogos redundantes, e o resultado final e
VERIFICADO por forca bruta contra TODAS as C(v, v-15) possibilidades - nao e
um numero de tabela "confiavel de memoria", e provado por computacao.

Uso:
    python gerar_matrizes_cobertura.py

Gera dados/matrizes_cobertura.json com, para cada tamanho de grupo (16 a 20):
    - garantia: 14
    - jogos: quantidade de jogos na matriz reduzida (verificada)
    - matriz_posicoes: lista de jogos, cada um como lista de 15 posicoes
      (indices 0-based dentro do grupo de v dezenas escolhido pelo usuario -
      posicao 0 = a 1a dezena escolhida, em ordem crescente, etc.)
    - total_possibilidades_cobertas: quantos sorteios hipoteticos (C(v,15))
      foram checados na verificacao
    - verificado: sempre True (o script aborta se a verificacao falhar)
"""
import itertools
import json
import os
import time

DADOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados")
SAIDA_JSON = os.path.join(DADOS_DIR, "matrizes_cobertura.json")

TAMANHO_JOGO = 15
GARANTIA = 14
TAMANHOS_GRUPO = [16, 17, 18, 19, 20]


def intersecao_minima(v, k=TAMANHO_JOGO, garantia=GARANTIA):
    """
    Intersecao minima necessaria entre dois conjuntos de exclusao (tamanho
    v-k cada) para que os respectivos jogos de k dezenas tenham pelo menos
    `garantia` acertos entre si.

    acertos(G,D) = v - |excl(G) U excl(D)| = v - (2*(v-k) - |intersecao|)
    acertos(G,D) >= garantia  <=>  |intersecao| >= garantia - v + 2*(v-k)
                                 <=> |intersecao| >= garantia + v - 2*k
    """
    return garantia + v - 2 * k


def construir_mascaras_exclusao(v, e):
    """Todas as C(v,e) combinacoes de exclusao, como mascaras de bits (int)."""
    combos = list(itertools.combinations(range(v), e))
    masks = []
    for combo in combos:
        m = 0
        for x in combo:
            m |= 1 << x
        masks.append(m)
    return combos, masks


def construir_coberturas(masks, limite_intersecao):
    """
    Para cada candidato i, monta um bitmask (Python int, um bit por indice j)
    indicando quais D's ele cobre (intersecao de exclusoes >= limite).
    Usa inteiros Python puros (sem numpy) - cada mascara tem no maximo 20 bits,
    entao bit_count() em (mask_i & mask_j) e uma operacao muito barata; a
    relacao e simetrica, entao cada par so precisa ser calculado uma vez.
    """
    n = len(masks)
    coberturas = [1 << i for i in range(n)]  # cada candidato sempre cobre a si mesmo
    for i in range(n):
        mi = masks[i]
        for j in range(i + 1, n):
            if (mi & masks[j]).bit_count() >= limite_intersecao:
                coberturas[i] |= 1 << j
                coberturas[j] |= 1 << i
    return coberturas


def greedy_set_cover(coberturas, n):
    total_mask = (1 << n) - 1
    coberto = 0
    escolhidos = []
    disponiveis = set(range(n))
    while coberto != total_mask:
        faltando = total_mask & ~coberto
        melhor_i, melhor_ganho = -1, -1
        for i in disponiveis:
            ganho = (coberturas[i] & faltando).bit_count()
            if ganho > melhor_ganho:
                melhor_ganho, melhor_i = ganho, i
        escolhidos.append(melhor_i)
        disponiveis.discard(melhor_i)
        coberto |= coberturas[melhor_i]
    return escolhidos


def podar_redundantes(escolhidos, coberturas, n):
    """Remove jogos cuja ausencia nao quebra a cobertura total (minimo local)."""
    total_mask = (1 << n) - 1
    atual = list(escolhidos)
    melhorou = True
    while melhorou:
        melhorou = False
        for i in list(atual):
            resto = [x for x in atual if x != i]
            cobertura_resto = 0
            for x in resto:
                cobertura_resto |= coberturas[x]
                if cobertura_resto == total_mask:
                    break
            if cobertura_resto == total_mask:
                atual = resto
                melhorou = True
    return atual


def verificar_cobertura_completa(escolhidos, coberturas, n):
    """Prova, por forca bruta, que TODOS os n sorteios hipoteticos sao cobertos."""
    total_mask = (1 << n) - 1
    cobertura_final = 0
    for i in escolhidos:
        cobertura_final |= coberturas[i]
    return cobertura_final == total_mask


def gerar_matriz_para_grupo(v):
    e = v - TAMANHO_JOGO
    limite = intersecao_minima(v)
    print(f"\n=== Grupo v={v} | exclusao={e} | garantia={GARANTIA} | intersecao minima necessaria={limite} ===")

    combos, masks = construir_mascaras_exclusao(v, e)
    n = len(combos)
    print(f"Total de sorteios hipoteticos possiveis (C({v},{e})): {n}")

    coberturas = construir_coberturas(masks, limite)
    escolhidos = greedy_set_cover(coberturas, n)
    print(f"Greedy inicial: {len(escolhidos)} jogo(s)")

    escolhidos = podar_redundantes(escolhidos, coberturas, n)
    print(f"Apos poda de redundantes: {len(escolhidos)} jogo(s)")

    ok = verificar_cobertura_completa(escolhidos, coberturas, n)
    if not ok:
        raise RuntimeError(f"FALHA na verificacao de cobertura para v={v}! Nao pode ser publicado.")
    print(f"Verificacao exaustiva: OK - todos os {n} sorteios hipoteticos cobertos com garantia >= {GARANTIA}.")

    matriz_posicoes = []
    universo = set(range(v))
    for i in escolhidos:
        excl = set(combos[i])
        jogo = sorted(universo - excl)
        assert len(jogo) == TAMANHO_JOGO
        matriz_posicoes.append(jogo)

    reducao_pct = 100 * (1 - len(matriz_posicoes) / (n if n else 1))
    print(f"Jogos full C({v},{TAMANHO_JOGO}) = {n}  ->  matriz reduzida = {len(matriz_posicoes)}  "
          f"(reducao de {reducao_pct:.1f}%)")

    return {
        "tamanho_grupo": v,
        "garantia": GARANTIA,
        "jogos": len(matriz_posicoes),
        "matriz_posicoes": matriz_posicoes,
        "total_possibilidades_cobertas": n,
        "jogos_full_combinacoes": n,
        "verificado": True,
    }


def main():
    resultado = {}
    for v in TAMANHOS_GRUPO:
        resultado[str(v)] = gerar_matriz_para_grupo(v)

    os.makedirs(DADOS_DIR, exist_ok=True)
    with open(SAIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\nMatrizes gravadas em {SAIDA_JSON}")
    print("\nResumo final:")
    for v in TAMANHOS_GRUPO:
        r = resultado[str(v)]
        print(f"  v={v}: {r['jogos']} jogo(s) (garantia {r['garantia']}) "
              f"vs. {r['jogos_full_combinacoes']} na combinacao total")


if __name__ == "__main__":
    main()
