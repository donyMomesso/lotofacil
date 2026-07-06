"""
gerar_jogos_inteligente.py
===========================
Meta-metodo: gera jogos combinando os 8 metodos (M1-M8), mas decide QUAIS
metodos usar e QUANTOS jogos por metodo com base no desempenho real
observado no backtest completo (dados/estatisticas_simulacao.csv, para a
janela "geral", ou dados/simulacao_metodos.csv, para janelas recentes de
100/200/500 concursos).

A geracao das dezenas em si reaproveita exatamente a mesma logica ja usada
por scripts/gerar_jogos.py (lib.gerar_todos_metodos para M1-M5,
gerar_jogos_avancados() para M6-M8) - este script so adiciona uma camada de
selecao/ponderacao por cima, sem reinventar nenhum metodo.

IMPORTANTE - mesma regra do resto do laboratorio (ver
reports/analise_comparativa_metodos.md, secao de conclusoes): a Lotofacil e
um sorteio independente, e a esperanca teorica de 9,0 acertos e identica
para qualquer metodo. A ponderacao aqui reflete apenas o encaixe de cada
metodo com o historico JA sorteado - nao e garantia nem indicio confiavel
de desempenho nos proximos concursos. Isto e um exercicio estatistico de
alocacao, nao uma estrategia vencedora.

Modos disponiveis:
    todos      - 1 jogo por metodo, todos os 8 (equivalente ao gerar_jogos.py)
    ponderado  - distribui --total jogos entre os 8 metodos, proporcional
                 ao indicador escolhido (--criterio) na janela escolhida (--janela)
    top        - seleciona os --n metodos com melhor indicador e distribui
                 --total jogos so entre eles
    hibrido    - combina os 3 melhores metodos da janela (peso principal,
                 baseado no --criterio) com 2 metodos sorteados entre os
                 restantes (peso menor, so para manter diversidade) - ver
                 montar_hibrido() para os percentuais exatos

Janelas disponiveis (--janela):
    geral   - todo o historico do backtest (dados/estatisticas_simulacao.csv)
    recent  - atalho para os ultimos 100 concursos (dados/simulacao_metodos.csv)
    <numero>- ultimos N concursos, ex.: 100, 200, 500

Uso:
    python gerar_jogos_inteligente.py [concurso_alvo] --modo=ponderado --total=8 --janela=geral
    python gerar_jogos_inteligente.py [concurso_alvo] --modo=top --n=3 --criterio=pct_11 --total=6 --janela=200
    python gerar_jogos_inteligente.py [concurso_alvo] --modo=hibrido --total=10 --janela=recent
    python gerar_jogos_inteligente.py [concurso_alvo] --modo=todos

Grava em dados/jogos_inteligente.csv (arquivo proprio, separado de
dados/jogos_gerados.csv, para nao interferir na conferencia diaria de
producao nem nas estatisticas oficiais dos 8 metodos).
"""
import argparse
import csv
import os
import random
import statistics
import sys
from datetime import datetime, timezone, timedelta

import lotofacil_lib as lib
from gerar_jogos_avancados import gerar_jogos_avancados

BRASILIA = timezone(timedelta(hours=-3))

METODOS_AVANCADOS = {
    "M6_filtros_combinados",
    "M7_cobertura_pares",
    "M8_repeticao_controlada",
}

SIMULACAO_CSV = os.path.join(lib.DADOS_DIR, "simulacao_metodos.csv")
ESTATISTICAS_SIM_CSV = os.path.join(lib.DADOS_DIR, "estatisticas_simulacao.csv")
SAIDA_CSV = os.path.join(lib.DADOS_DIR, "jogos_inteligente.csv")

# Valor bruto de cada indicador, para exibir como "score" (sempre no sentido
# natural da metrica - ex.: desvio padrao aparece como desvio, nao invertido).
VALOR_BRUTO = {
    "pct_11": lambda s: float(s["pct_11_ou_mais"]),
    "pct_13": lambda s: float(s["pct_13_ou_mais"]),
    "estabilidade": lambda s: float(s["desvio_padrao_acertos"]),
}

# Para pct_11/pct_13, maior e melhor. Para estabilidade, menor desvio padrao
# e melhor - por isso essa e a unica metrica "invertida" nos rankings.
CRITERIO_MENOR_E_MELHOR = {"estabilidade"}


def _valor_ranking(criterio, stats_metodo):
    """Valor usado para ordenar metodos do melhor para o pior, independente
    da metrica escolhida (inverte o sinal so para estabilidade)."""
    valor = VALOR_BRUTO[criterio](stats_metodo)
    return -valor if criterio in CRITERIO_MENOR_E_MELHOR else valor


CRITERIOS = list(VALOR_BRUTO)


def carregar_stats_geral():
    """Le dados/estatisticas_simulacao.csv (backtest completo, todo o historico real)."""
    if not os.path.exists(ESTATISTICAS_SIM_CSV):
        raise FileNotFoundError(
            f"{ESTATISTICAS_SIM_CSV} nao encontrado. Rode executar_backtest_completo.py primeiro."
        )
    with open(ESTATISTICAS_SIM_CSV, encoding="utf-8") as f:
        return {r["metodo"]: r for r in csv.DictReader(f)}


def carregar_stats_janela(n_concursos):
    """Recalcula media/desvio/pct_11/pct_13 usando so os ultimos n_concursos
    concursos do backtest (dados/simulacao_metodos.csv), do mesmo jeito que
    reports/analise_comparativa_metodos.md fez para 100/200/500 concursos."""
    if not os.path.exists(SIMULACAO_CSV):
        raise FileNotFoundError(
            f"{SIMULACAO_CSV} nao encontrado. Rode executar_backtest_completo.py primeiro."
        )
    with open(SIMULACAO_CSV, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    for r in linhas:
        r["concurso"] = int(r["concurso"])
        r["acertos"] = int(r["acertos"])

    max_concurso = max(r["concurso"] for r in linhas)
    limite = max_concurso - n_concursos + 1
    linhas = [r for r in linhas if r["concurso"] >= limite]

    por_metodo = {}
    for metodo in lib.METODOS:
        acertos = [r["acertos"] for r in linhas if r["metodo"] == metodo]
        if not acertos:
            continue
        n = len(acertos)
        desvio = statistics.pstdev(acertos) if n > 1 else 0.0
        pct11 = 100 * sum(1 for a in acertos if a >= 11) / n
        pct13 = 100 * sum(1 for a in acertos if a >= 13) / n
        por_metodo[metodo] = {
            "metodo": metodo,
            "media_acertos": round(statistics.mean(acertos), 4),
            "desvio_padrao_acertos": round(desvio, 4),
            "pct_11_ou_mais": round(pct11, 3),
            "pct_13_ou_mais": round(pct13, 3),
        }
    return por_metodo


JANELA_RECENT_CONCURSOS = 100


def obter_stats(janela):
    """janela = 'geral', 'recent' (atalho para os ultimos 100 concursos) ou
    numero de concursos (ex.: '100', '200', '500').
    Retorna (stats_por_metodo, descricao_para_exibir)."""
    if janela == "geral":
        return carregar_stats_geral(), "geral - todo o historico do backtest (estatisticas_simulacao.csv)"
    if janela == "recent":
        stats = carregar_stats_janela(JANELA_RECENT_CONCURSOS)
        return stats, f"recent -> ultimos {JANELA_RECENT_CONCURSOS} concursos (atalho automatico)"
    n = int(janela)
    return carregar_stats_janela(n), f"ultimos {n} concursos (simulacao_metodos.csv)"


def calcular_pesos(stats, criterio):
    """Normaliza o indicador escolhido em pesos que somam 1.0.
    Usa um piso minimo (0.0001) para que nenhum metodo fique com peso zero
    mesmo se o indicador dele for 0 na janela escolhida."""
    scores = {m: max(_valor_ranking(criterio, s), 0.0001) for m, s in stats.items()}
    total = sum(scores.values())
    return {m: v / total for m, v in scores.items()}


def selecionar_top(stats, n, criterio):
    """Retorna os n metodos com melhor _valor_ranking (do melhor para o pior)."""
    ranking = sorted(stats.keys(), key=lambda m: _valor_ranking(criterio, stats[m]), reverse=True)
    return ranking[:n]


def melhor_e_pior(metodos, stats, criterio):
    """Retorna (melhor_metodo, score_melhor, pior_metodo, score_pior) usando
    o valor bruto (nao invertido) do indicador, para exibicao no resumo final."""
    valores = {m: VALOR_BRUTO[criterio](stats[m]) for m in metodos}
    ordenados = sorted(metodos, key=lambda m: _valor_ranking(criterio, stats[m]), reverse=True)
    melhor, pior = ordenados[0], ordenados[-1]
    return melhor, valores[melhor], pior, valores[pior]


def montar_hibrido(stats, criterio, concurso_alvo, n_top=3, n_diversidade=2, peso_diversidade=0.3):
    """Modo hibrido: combina os n_top melhores metodos da janela (peso
    principal, 1 - peso_diversidade) com n_diversidade metodos sorteados
    entre os restantes (peso menor, dividido igualmente), para nao
    concentrar 100% dos jogos so nos "melhores" do backtest - o proprio
    laboratorio ja concluiu que a diferenca entre eles e pequena demais
    para justificar isso (ver reports/analise_comparativa_metodos.md).

    O sorteio dos metodos de diversidade usa uma seed derivada do concurso
    alvo, entao e reproduzivel (mesma janela + mesmo concurso = mesmo
    resultado), mas muda de concurso para concurso.
    """
    top = selecionar_top(stats, n_top, criterio)
    restantes = [m for m in stats if m not in top]
    rng_diversidade = random.Random(f"hibrido-{concurso_alvo}")
    diversidade = rng_diversidade.sample(restantes, min(n_diversidade, len(restantes)))

    pesos_top = calcular_pesos({m: stats[m] for m in top}, criterio)
    pesos = {m: v * (1 - peso_diversidade) for m, v in pesos_top.items()}
    if diversidade:
        fatia = peso_diversidade / len(diversidade)
        for m in diversidade:
            pesos[m] = fatia
    return pesos, top, diversidade


def distribuir_jogos(pesos, total):
    """Aloca 'total' jogos entre os metodos de 'pesos', proporcional ao peso
    de cada um. Usa o metodo do maior resto (largest remainder) para que a
    soma final seja exatamente 'total' mesmo com arredondamento."""
    metodos = list(pesos.keys())
    brutos = {m: pesos[m] * total for m in metodos}
    base = {m: int(brutos[m]) for m in metodos}
    restante = total - sum(base.values())
    ordem_resto = sorted(metodos, key=lambda m: brutos[m] - base[m], reverse=True)
    for m in ordem_resto[:restante]:
        base[m] += 1
    return base


def gerar_k_jogos_para_metodo(metodo, k, ate_concurso, seed_base):
    """Gera k jogos reais para um metodo, reaproveitando a mesma logica de
    scripts/gerar_jogos.py - nao reinventa a geracao de dezenas."""
    jogos = []
    if metodo in METODOS_AVANCADOS:
        # cada chamada a gerar_jogos_avancados ja retorna ate 5 candidatos
        # rankeados; chama de novo (com seed diferente) so se precisar de mais
        tentativa = 0
        while len(jogos) < k and tentativa < 10:
            resultado = gerar_jogos_avancados(seed=seed_base + tentativa, ate_concurso=ate_concurso)
            jogos.extend(resultado[metodo])
            tentativa += 1
        jogos = jogos[:k]
    else:
        for i in range(k):
            todos = lib.gerar_todos_metodos(seed=seed_base + i, ate_concurso=ate_concurso)
            jogos.append(todos[metodo])
    return jogos


SAIDA_CSV_FIELDNAMES = [
    "data_geracao", "concurso_alvo", "metodo", "dezenas",
    "soma", "pares", "impares", "modo", "janela", "criterio", "peso", "score",
]


def _ensure_saida_csv():
    if not os.path.exists(SAIDA_CSV):
        with open(SAIDA_CSV, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=SAIDA_CSV_FIELDNAMES).writeheader()


def _jogo_ja_gravado(concurso_alvo, metodo, dezenas_str):
    if not os.path.exists(SAIDA_CSV):
        return False
    with open(SAIDA_CSV, encoding="utf-8") as f:
        return any(
            row["concurso_alvo"] == str(concurso_alvo)
            and row["metodo"] == metodo
            and row["dezenas"] == dezenas_str
            for row in csv.DictReader(f)
        )


def gravar_jogo(data_geracao, concurso_alvo, metodo, dezenas, modo, janela, criterio, peso, score):
    _ensure_saida_csv()
    dezenas_sorted = sorted(dezenas)
    dezenas_str = "-".join(f"{d:02d}" for d in dezenas_sorted)
    if _jogo_ja_gravado(concurso_alvo, metodo, dezenas_str):
        return False
    pares = sum(1 for d in dezenas_sorted if d % 2 == 0)
    with open(SAIDA_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SAIDA_CSV_FIELDNAMES)
        writer.writerow({
            "data_geracao": data_geracao,
            "concurso_alvo": concurso_alvo,
            "metodo": metodo,
            "dezenas": dezenas_str,
            "soma": sum(dezenas_sorted),
            "pares": pares,
            "impares": 15 - pares,
            "modo": modo,
            "janela": janela,
            "criterio": criterio,
            "peso": round(peso, 4),
            "score": round(score, 4),
        })
    return True


LIMITE_JOGOS_POR_METODO_TOP = 5  # mesmo teto usado pelos metodos avancados (TOP_JOGOS_SELECIONAR)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("concurso_alvo", nargs="?", type=int, default=None)
    parser.add_argument("--modo", choices=["todos", "ponderado", "top", "hibrido"], default="ponderado")
    parser.add_argument("--janela", default="geral", help="'geral', 'recent' (ultimos 100) ou numero de concursos (ex.: 100, 200, 500)")
    parser.add_argument("--criterio", choices=CRITERIOS, default="pct_11")
    parser.add_argument("--total", type=int, default=8, help="total de jogos a gerar (modos ponderado/top/hibrido)")
    parser.add_argument("--n", type=int, default=3, help="quantidade de metodos a priorizar no modo top")
    args = parser.parse_args()

    concurso_alvo = args.concurso_alvo
    if concurso_alvo is None:
        ultimo = lib.ultimo_concurso_registrado()
        concurso_alvo = (ultimo + 1) if ultimo else 1

    # Validacao: no modo "top", pedir muitos jogos para poucos metodos so gera
    # candidatos repetidos (metodos deterministicos como M2/M3 nem produzem
    # jogos diferentes entre si). Avisa e limita automaticamente.
    if args.modo == "top":
        limite_total = args.n * LIMITE_JOGOS_POR_METODO_TOP
        if args.total > limite_total:
            print(
                f"[aviso] --total={args.total} e alto demais para --n={args.n} metodo(s) no modo 'top' "
                f"(acima de {LIMITE_JOGOS_POR_METODO_TOP} jogos por metodo tende a repetir candidatos, "
                f"e metodos deterministicos como M2/M3 nem chegam a variar). "
                f"Limitando --total para {limite_total}."
            )
            args.total = limite_total

    stats, descricao_janela = obter_stats(args.janela)

    if args.modo == "todos":
        alocacao = {m: 1 for m in lib.METODOS}
        pesos_exibicao = {m: 1 / len(lib.METODOS) for m in lib.METODOS}
        considerados = lib.METODOS
    elif args.modo == "top":
        considerados = selecionar_top(stats, args.n, args.criterio)
        pesos_exibicao = calcular_pesos({m: stats[m] for m in considerados}, args.criterio)
        alocacao = distribuir_jogos(pesos_exibicao, args.total)
    elif args.modo == "hibrido":
        pesos_exibicao, top_metodos, diversidade_metodos = montar_hibrido(stats, args.criterio, concurso_alvo)
        considerados = top_metodos + diversidade_metodos
        alocacao = distribuir_jogos(pesos_exibicao, args.total)
    else:  # ponderado
        considerados = list(stats)
        pesos_exibicao = calcular_pesos(stats, args.criterio)
        alocacao = distribuir_jogos(pesos_exibicao, args.total)

    print(f"Concurso alvo: {concurso_alvo}")
    print(f"Modo: {args.modo} | Criterio: {args.criterio}")
    print(f"Janela usada: {descricao_janela}")
    if args.modo == "hibrido":
        print(f"  -> top (peso principal): {', '.join(top_metodos)}")
        print(f"  -> diversidade (peso menor, sorteado): {', '.join(diversidade_metodos)}")

    print("\nRanking dos metodos considerados (melhor -> pior, segundo o criterio escolhido):")
    ranking_ordenado = sorted(considerados, key=lambda m: _valor_ranking(args.criterio, stats[m]), reverse=True)
    for posicao, metodo in enumerate(ranking_ordenado, start=1):
        score = VALOR_BRUTO[args.criterio](stats[metodo])
        peso = pesos_exibicao.get(metodo, 0.0)
        jogos_alocados = alocacao.get(metodo, 0)
        print(f"  {posicao}. {metodo:28s} score={score:.3f}  peso={peso:.3f}  jogos={jogos_alocados}")

    print(
        "\nAVISO: esta ponderacao reflete apenas o encaixe historico de cada metodo com"
        " o backtest ja sorteado. A Lotofacil e um sorteio independente - isso NAO"
        " garante nem indica desempenho melhor nos proximos concursos."
        " Ver reports/analise_comparativa_metodos.md.\n"
    )

    data_geracao = datetime.now(BRASILIA).strftime("%d/%m/%Y")
    gerados = []
    seed_base = concurso_alvo * 1000

    for metodo, k in alocacao.items():
        if k <= 0:
            continue
        jogos = gerar_k_jogos_para_metodo(metodo, k, ate_concurso=concurso_alvo - 1, seed_base=seed_base)
        peso = pesos_exibicao.get(metodo, 0.0)
        score = VALOR_BRUTO[args.criterio](stats[metodo])
        for dezenas in jogos:
            novo = gravar_jogo(
                data_geracao, concurso_alvo, metodo, dezenas,
                modo=args.modo, janela=args.janela, criterio=args.criterio, peso=peso, score=score,
            )
            dezenas_str = "-".join(f"{d:02d}" for d in sorted(dezenas))
            status = "ok" if novo else "skip (ja gravado)"
            print(f"[{status}] {metodo} -> {dezenas_str}")
            if novo:
                gerados.append((metodo, dezenas))

    melhor, score_melhor, pior, score_pior = melhor_e_pior(considerados, stats, args.criterio)
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"Concurso alvo: {concurso_alvo} | Modo: {args.modo} | Janela: {args.janela} | Criterio: {args.criterio}")
    print(f"Melhor metodo nesta janela/criterio: {melhor} (score={score_melhor:.3f})")
    print(f"Pior metodo nesta janela/criterio:   {pior} (score={score_pior:.3f})")
    print(f"Distribuicao usada (metodo -> jogos): {dict(alocacao)}")
    print(f"{len(gerados)} jogo(s) novo(s) gravado(s) em {SAIDA_CSV}.")


if __name__ == "__main__":
    main()
