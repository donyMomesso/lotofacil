"""
Biblioteca comum do Laboratório Estatístico Lotofácil.

Este módulo só faz matemática e leitura/escrita de CSV local.
Nenhuma função aqui "escolhe o jogo certo" ou avalia qualidade de
aposta — cada método é apenas uma hipótese estatística diferente,
comparada de forma neutra contra as demais e contra o valor
teórico esperado (hipergeométrico).

Lembrete de regra do laboratório: nunca reportar um método como
"mais perto" de 14 ou 15 acertos. Reportar sempre médias, dispersão
e frequência relativa dos resultados de acertos (0 a 15).
"""
import csv
import itertools
import json
import os
import random
import statistics
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS_DIR = os.path.join(BASE_DIR, "dados")

RESULTADOS_CSV = os.path.join(DADOS_DIR, "resultados_lotofacil.csv")
JOGOS_CSV = os.path.join(DADOS_DIR, "jogos_gerados.csv")
CONFERENCIA_CSV = os.path.join(DADOS_DIR, "conferencia.csv")
FREQUENCIA_CSV = os.path.join(DADOS_DIR, "frequencia_dezenas.csv")
ESTATISTICAS_CSV = os.path.join(DADOS_DIR, "estatisticas_metodos.csv")
ESTATISTICAS_JSON = os.path.join(DADOS_DIR, "estatisticas.json")

TODAS_DEZENAS = list(range(1, 26))

# Valor teórico esperado de acertos para um jogo de 15 dezenas
# (distribuição hipergeométrica: N=25, K=15 sorteadas, n=15 escolhidas)
# E[acertos] = n*K/N = 15*15/25 = 9.0
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


# ---------- leitura/escrita ----------

def _ensure_files():
    os.makedirs(DADOS_DIR, exist_ok=True)
    if not os.path.exists(RESULTADOS_CSV):
        with open(RESULTADOS_CSV, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["concurso", "data"] + [f"b{i:02d}" for i in range(1, 16)] + ["dezenas"]
            csv.DictWriter(f, fieldnames=fieldnames).writeheader()
    if not os.path.exists(JOGOS_CSV):
        with open(JOGOS_CSV, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["data_geracao", "concurso_alvo", "metodo", "dezenas", "soma", "pares", "impares"]
            csv.DictWriter(f, fieldnames=fieldnames).writeheader()
    if not os.path.exists(CONFERENCIA_CSV):
        with open(CONFERENCIA_CSV, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["concurso", "data_sorteio", "metodo", "dezenas_jogo", "dezenas_sorteadas", "acertos"]
            csv.DictWriter(f, fieldnames=fieldnames).writeheader()


def carregar_resultados():
    """Retorna lista de dicts ordenada por concurso crescente:
    {concurso:int, data:str, dezenas:set[int]}"""
    _ensure_files()
    out = []
    with open(RESULTADOS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            dezenas = {int(row[f"b{i:02d}"]) for i in range(1, 16)}
            out.append({"concurso": int(row["concurso"]), "data": row["data"], "dezenas": dezenas})
    out.sort(key=lambda r: r["concurso"])
    return out


def ultimo_concurso_registrado():
    resultados = carregar_resultados()
    if not resultados:
        return None
    return resultados[-1]["concurso"]


def resultado_ja_registrado(concurso):
    return any(r["concurso"] == concurso for r in carregar_resultados())


def registrar_resultado(concurso, data, dezenas):
    """Acrescenta um novo concurso real ao histórico (idempotente)."""
    _ensure_files()
    if resultado_ja_registrado(concurso):
        return False
    dezenas_sorted = sorted(dezenas)
    row = {"concurso": concurso, "data": data}
    for i, d in enumerate(dezenas_sorted, start=1):
        row[f"b{i:02d}"] = d
    row["dezenas"] = "-".join(f"{d:02d}" for d in dezenas_sorted)
    with open(RESULTADOS_CSV, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["concurso", "data"] + [f"b{i:02d}" for i in range(1, 16)] + ["dezenas"]
        csv.DictWriter(f, fieldnames=fieldnames).writerow(row)
    return True


def carregar_jogos():
    _ensure_files()
    out = []
    with open(JOGOS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["concurso_alvo"] = int(row["concurso_alvo"])
            row["dezenas_set"] = {int(x) for x in row["dezenas"].split("-")}
            out.append(row)
    return out


def jogo_ja_gerado(concurso_alvo, metodo):
    return any(j["concurso_alvo"] == concurso_alvo and j["metodo"] == metodo for j in carregar_jogos())


def registrar_jogo(data_geracao, concurso_alvo, metodo, dezenas):
    _ensure_files()
    dezenas_sorted = sorted(dezenas)
    pares = sum(1 for d in dezenas_sorted if d % 2 == 0)
    row = {
        "data_geracao": data_geracao,
        "concurso_alvo": concurso_alvo,
        "metodo": metodo,
        "dezenas": "-".join(f"{d:02d}" for d in dezenas_sorted),
        "soma": sum(dezenas_sorted),
        "pares": pares,
        "impares": 15 - pares,
    }
    with open(JOGOS_CSV, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["data_geracao", "concurso_alvo", "metodo", "dezenas", "soma", "pares", "impares"]
        csv.DictWriter(f, fieldnames=fieldnames).writerow(row)


def jogo_ja_conferido(concurso, metodo, dezenas_str):
    _ensure_files()
    with open(CONFERENCIA_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if int(row["concurso"]) == concurso and row["metodo"] == metodo and row["dezenas_jogo"] == dezenas_str:
                return True
    return False


def registrar_conferencia(concurso, data_sorteio, metodo, dezenas_jogo, dezenas_sorteadas):
    _ensure_files()
    dezenas_str = "-".join(f"{d:02d}" for d in sorted(dezenas_jogo))
    if jogo_ja_conferido(concurso, metodo, dezenas_str):
        return None
    acertos = len(set(dezenas_jogo) & set(dezenas_sorteadas))
    row = {
        "concurso": concurso,
        "data_sorteio": data_sorteio,
        "metodo": metodo,
        "dezenas_jogo": dezenas_str,
        "dezenas_sorteadas": "-".join(f"{d:02d}" for d in sorted(dezenas_sorteadas)),
        "acertos": acertos,
    }
    with open(CONFERENCIA_CSV, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["concurso", "data_sorteio", "metodo", "dezenas_jogo", "dezenas_sorteadas", "acertos"]
        csv.DictWriter(f, fieldnames=fieldnames).writerow(row)
    return acertos


# ---------- estatística de frequência / atraso ----------

def frequencia_e_atraso(ate_concurso=None):
    """Frequência absoluta de cada dezena e atraso atual (nº de concursos
    desde a última vez que a dezena saiu), considerando o histórico até
    `ate_concurso` (inclusive) ou tudo, se None."""
    resultados = carregar_resultados()
    if ate_concurso is not None:
        resultados = [r for r in resultados if r["concurso"] <= ate_concurso]

    freq = Counter()
    ultima_aparicao = {}
    for idx, r in enumerate(resultados):
        for d in r["dezenas"]:
            freq[d] += 1
            ultima_aparicao[d] = idx

    total_concursos = len(resultados)
    atraso = {}
    for d in TODAS_DEZENAS:
        if d in ultima_aparicao:
            atraso[d] = (total_concursos - 1) - ultima_aparicao[d]
        else:
            atraso[d] = total_concursos  # nunca saiu na janela observada

    for d in TODAS_DEZENAS:
        freq.setdefault(d, 0)

    return freq, atraso, total_concursos


# ---------- geração dos 5 métodos (hipóteses de estudo) ----------

def _sorteio_valido(dezenas):
    return len(set(dezenas)) == 15 and all(1 <= d <= 25 for d in dezenas)


def _rng_or_default(rng):
    return rng if rng is not None else random.Random()


def metodo_aleatorio_puro(rng):
    rng = _rng_or_default(rng)
    return set(rng.sample(TODAS_DEZENAS, 15))


def metodo_mais_frequentes(rng, freq):
    rng = _rng_or_default(rng)
    # ordena por frequência desc; empates quebrados aleatoriamente para não
    # favorecer sistematicamente dezenas menores
    dezenas = TODAS_DEZENAS[:]
    rng.shuffle(dezenas)
    dezenas.sort(key=lambda d: freq[d], reverse=True)
    return set(dezenas[:15])


def metodo_mais_atrasadas(rng, atraso):
    rng = _rng_or_default(rng)
    dezenas = TODAS_DEZENAS[:]
    rng.shuffle(dezenas)
    dezenas.sort(key=lambda d: atraso[d], reverse=True)
    return set(dezenas[:15])


def metodo_par_impar_balanceado(rng, alvo_pares=8, max_tentativas=500):
    rng = _rng_or_default(rng)
    for _ in range(max_tentativas):
        candidato = rng.sample(TODAS_DEZENAS, 15)
        pares = sum(1 for d in candidato if d % 2 == 0)
        if pares == alvo_pares:
            return set(candidato)
    return metodo_aleatorio_puro(rng)  # fallback, não deve ocorrer na prática


def metodo_soma_faixa_comum(rng, faixa_min=180, faixa_max=210, max_tentativas=1000):
    rng = _rng_or_default(rng)
    for _ in range(max_tentativas):
        candidato = rng.sample(TODAS_DEZENAS, 15)
        if faixa_min <= sum(candidato) <= faixa_max:
            return set(candidato)
    return metodo_aleatorio_puro(rng)  # fallback


def _resultados_como_sets(ate_concurso=None):
    resultados = carregar_resultados()
    if ate_concurso is not None:
        resultados = [r for r in resultados if r["concurso"] <= ate_concurso]
    return [set(r["dezenas"]) for r in resultados]


def _pares_recentes(resultados_sets, n_concursos=COBERTURA_PARES_RECENTES):
    pares = set()
    for resultado in resultados_sets[-n_concursos:]:
        for a, b in itertools.combinations(sorted(resultado), 2):
            pares.add((a, b))
    return pares


def _contar_repeticoes(jogo, resultado_anterior):
    return len(set(jogo) & set(resultado_anterior))


def _cobertura_pares_adjacentes(jogo, pares_recentes):
    jogo_sorted = sorted(jogo)
    return sum(
        1
        for a, b in zip(jogo_sorted, jogo_sorted[1:])
        if (min(a, b), max(a, b)) in pares_recentes
    )


def _score_avancado(jogo, pares_recentes, resultado_anterior):
    soma = sum(jogo)
    pares = sum(1 for d in jogo if d % 2 == 0)
    repeticoes = _contar_repeticoes(jogo, resultado_anterior)
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


def _melhor_candidato_avancado(rng, resultados_sets, filtro=None, max_tentativas=NUM_CANDIDATOS_AVANCADOS):
    if not resultados_sets:
        return metodo_aleatorio_puro(rng)

    resultado_anterior = resultados_sets[-1]
    pares_recentes = _pares_recentes(resultados_sets)
    melhor = None
    melhor_score = -1

    for _ in range(max_tentativas):
        candidato = set(rng.sample(TODAS_DEZENAS, 15))
        if filtro and not filtro(candidato, resultado_anterior):
            continue
        score = _score_avancado(candidato, pares_recentes, resultado_anterior)
        if score > melhor_score:
            melhor = candidato
            melhor_score = score

    return melhor or metodo_aleatorio_puro(rng)


def metodo_filtros_combinados(rng, resultados_sets):
    def filtro(jogo, resultado_anterior):
        soma = sum(jogo)
        pares = sum(1 for d in jogo if d % 2 == 0)
        repeticoes = _contar_repeticoes(jogo, resultado_anterior)
        return (
            SOMA_AVANCADA_MIN <= soma <= SOMA_AVANCADA_MAX
            and PARES_AVANCADO_MIN <= pares <= PARES_AVANCADO_MAX
            and REPETICOES_MIN <= repeticoes <= REPETICOES_MAX
        )

    return _melhor_candidato_avancado(rng, resultados_sets, filtro=filtro)


def metodo_cobertura_pares(rng, resultados_sets):
    return _melhor_candidato_avancado(rng, resultados_sets)


def metodo_repeticao_controlada(rng, resultados_sets):
    def filtro(jogo, resultado_anterior):
        repeticoes = _contar_repeticoes(jogo, resultado_anterior)
        return 9 <= repeticoes <= 11

    return _melhor_candidato_avancado(rng, resultados_sets, filtro=filtro)


def gerar_todos_metodos(seed=None, ate_concurso=None):
    rng = random.Random(seed)
    freq, atraso, _ = frequencia_e_atraso(ate_concurso)
    resultados_sets = _resultados_como_sets(ate_concurso)
    return {
        "M1_aleatorio_puro": metodo_aleatorio_puro(rng),
        "M2_mais_frequentes": metodo_mais_frequentes(rng, freq),
        "M3_mais_atrasadas": metodo_mais_atrasadas(rng, atraso),
        "M4_par_impar_balanceado": metodo_par_impar_balanceado(rng),
        "M5_soma_faixa_comum": metodo_soma_faixa_comum(rng),
        "M6_filtros_combinados": metodo_filtros_combinados(rng, resultados_sets),
        "M7_cobertura_pares": metodo_cobertura_pares(rng, resultados_sets),
        "M8_repeticao_controlada": metodo_repeticao_controlada(rng, resultados_sets),
    }


# ---------- estatísticas de desempenho por método ----------

def carregar_conferencias():
    _ensure_files()
    out = []
    with open(CONFERENCIA_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["concurso"] = int(row["concurso"])
            row["acertos"] = int(row["acertos"])
            out.append(row)
    return out


def calcular_estatisticas_metodos():
    conf = carregar_conferencias()
    por_metodo = {m: [] for m in METODOS}
    for row in conf:
        if row["metodo"] in por_metodo:
            por_metodo[row["metodo"]].append(row["acertos"])

    linhas = []
    for metodo, acertos_lista in por_metodo.items():
        n = len(acertos_lista)
        dist = Counter(acertos_lista)
        media = statistics.mean(acertos_lista) if n else 0.0
        desvio = statistics.pstdev(acertos_lista) if n > 1 else 0.0
        linha = {
            "metodo": metodo,
            "total_jogos_conferidos": n,
            "media_acertos": round(media, 3),
            "desvio_padrao_acertos": round(desvio, 3),
            "esperanca_teorica": ESPERANCA_TEORICA,
            "min_acertos": min(acertos_lista) if n else "",
            "max_acertos": max(acertos_lista) if n else "",
            "pct_11_ou_mais": round(100 * sum(1 for a in acertos_lista if a >= 11) / n, 2) if n else 0.0,
            "pct_13_ou_mais": round(100 * sum(1 for a in acertos_lista if a >= 13) / n, 2) if n else 0.0,
        }
        for k in range(16):
            linha[f"qtd_{k}_acertos"] = dist.get(k, 0)
        linhas.append(linha)
    return linhas


def calcular_series_metodos(janela=50):
    conf = carregar_conferencias()
    concursos = sorted({row["concurso"] for row in conf})[-janela:]
    por_concurso = {concurso: {m: None for m in METODOS} for concurso in concursos}

    for row in conf:
        concurso = row["concurso"]
        metodo = row["metodo"]
        if concurso in por_concurso and metodo in por_concurso[concurso]:
            por_concurso[concurso][metodo] = row["acertos"]

    series = []
    for metodo in METODOS:
        acertos = [por_concurso[concurso][metodo] for concurso in concursos]
        validos = [valor for valor in acertos if valor is not None]
        desvios = [valor - ESPERANCA_TEORICA for valor in validos]
        rms = (sum(d * d for d in desvios) / len(desvios)) ** 0.5 if desvios else 0.0
        media = statistics.mean(validos) if validos else 0.0
        desvio_padrao = statistics.pstdev(validos) if len(validos) > 1 else 0.0
        series.append({
            "metodo": metodo,
            "acertos_por_concurso": acertos,
            "media_periodo": round(media, 4),
            "desvio_padrao_periodo": round(desvio_padrao, 4),
            "desvio_vs_esperanca_rms": round(rms, 4),
            "total_concursos_periodo": len(validos),
        })

    metodo_estavel = min(
        series,
        key=lambda item: (item["desvio_vs_esperanca_rms"], item["desvio_padrao_periodo"], item["metodo"])
    )["metodo"] if series else None

    return {
        "janela": janela,
        "esperanca_teorica": ESPERANCA_TEORICA,
        "concursos": concursos,
        "series": series,
        "metodo_mais_estavel": metodo_estavel,
    }


def exportar_estatisticas_para_json(janela=50, caminho=None):
    _ensure_files()
    payload = {
        "resumo_historico": calcular_estatisticas_metodos(),
        "ultimos_concursos": calcular_series_metodos(janela=janela),
    }
    destino = caminho or ESTATISTICAS_JSON
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return destino


def salvar_estatisticas_metodos():
    linhas = calcular_estatisticas_metodos()
    if not linhas:
        return
    fieldnames = list(linhas[0].keys())
    with open(ESTATISTICAS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(linhas)


def salvar_frequencia_dezenas():
    freq, atraso, total = frequencia_e_atraso()
    fieldnames = ["dezena", "frequencia_absoluta", "frequencia_pct", "atraso_atual", "total_concursos_considerados"]
    with open(FREQUENCIA_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for d in TODAS_DEZENAS:
            pct = round(100 * freq[d] / total, 2) if total else 0.0
            writer.writerow({
                "dezena": f"{d:02d}",
                "frequencia_absoluta": freq[d],
                "frequencia_pct": pct,
                "atraso_atual": atraso[d],
                "total_concursos_considerados": total,
            })



def formatar_para_extensao(matrizes_geradas):
    if not matrizes_geradas:
        return ""

    linhas_formatadas = []
    for matriz in matrizes_geradas:
        numeros_formatados = [f"{numero:02d}" for numero in sorted(matriz)]
        linhas_formatadas.append(" ".join(numeros_formatados))

    return "\n".join(linhas_formatadas)

# ---------- desdobramento e filtros combinatorios (estudo, não geração de apostas) ----------
#
# Estas funções servem só para ILUSTRAR o espaço de combinações que atendem a
# certos critérios estruturais (soma, paridade, sequência, distribuição por
# linha) — nunca para produzir uma lista de jogos "para jogar". Sempre usar em
# conjunto com o backtest de combinações fixas abaixo, que mostra que mesmo
# essas combinações "bem-comportadas" têm a mesma esperança teórica de 9,0.

def desdobramento_total(dezenas_base, tamanho_linha=15):
    """
    Recebe uma base com mais de `tamanho_linha` dezenas (ex: 18) e retorna
    todas as combinações possíveis de `tamanho_linha` dezenas dentro dela —
    a mesma matemática por trás de uma aposta estendida da Lotofácil
    (C(len(base), tamanho_linha) combinações). Ver dados/apostas_estendidas.csv
    para o custo de cada tamanho de base.
    """
    if len(dezenas_base) < tamanho_linha:
        raise ValueError(f"A base deve ter pelo menos {tamanho_linha} dezenas.")
    matriz_gerada = list(itertools.combinations(sorted(dezenas_base), tamanho_linha))
    return [list(linha) for linha in matriz_gerada]


def passa_filtro_par_impar(linha, pares_min=8, pares_max=8):
    pares = sum(1 for d in linha if d % 2 == 0)
    return pares_min <= pares <= pares_max


def passa_filtro_soma(linha, soma_min=180, soma_max=210):
    return soma_min <= sum(linha) <= soma_max


def passa_filtro_sem_sequencia_longa(linha, max_run=5):
    """True se a linha não tem uma sequência de mais de `max_run` dezenas
    consecutivas (ex: 10,11,12,13,14,15,16 seria uma sequência de 7)."""
    dezenas_ordenadas = sorted(linha)
    maior_run = 1
    run_atual = 1
    for i in range(1, len(dezenas_ordenadas)):
        if dezenas_ordenadas[i] == dezenas_ordenadas[i - 1] + 1:
            run_atual += 1
            maior_run = max(maior_run, run_atual)
        else:
            run_atual = 1
    return maior_run <= max_run


def passa_filtro_linhas_vazias(linha, max_linhas_vazias=1):
    """True se no máximo `max_linhas_vazias` das 5 linhas do volante
    (1-5, 6-10, 11-15, 16-20, 21-25) ficam sem nenhuma dezena escolhida."""
    faixas = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 25)]
    vazias = sum(1 for a, b in faixas if not any(a <= d <= b for d in linha))
    return vazias <= max_linhas_vazias


def aplicar_filtros_combinatorios(matriz_bidimensional, pares_min=8, pares_max=8,
                                   soma_min=180, soma_max=210,
                                   max_run=5, max_linhas_vazias=1):
    """
    Filtra uma matriz de combinações, mantendo só as linhas que atendem a
    todos os critérios simultaneamente (par/ímpar, soma, sem sequência longa,
    no máximo 1 linha vazia). Por padrão usa exatamente os critérios do
    estudo "4 filtros combinados" do diário (que reduz as 3.268.760
    combinações possíveis para 366.487 — 11,21%). Isto é só descrição do
    espaço combinatório, não é indicação de jogo.
    """
    matriz_filtrada = []
    for linha in matriz_bidimensional:
        if (passa_filtro_par_impar(linha, pares_min, pares_max)
                and passa_filtro_soma(linha, soma_min, soma_max)
                and passa_filtro_sem_sequencia_longa(linha, max_run)
                and passa_filtro_linhas_vazias(linha, max_linhas_vazias)):
            matriz_filtrada.append(linha)
    return matriz_filtrada


def gerar_exemplos_filtrados(n_exemplos=5, seed=None, **filtros_kwargs):
    """
    Gera `n_exemplos` combinações de 15 dezenas, por amostragem aleatória
    com rejeição, que passam pelos filtros combinados (mesma definição de
    `aplicar_filtros_combinatorios`). Não enumera as 3.268.760 combinações
    inteiras — amostra direto do espaço de 25 dezenas até achar exemplos
    válidos, o que é equivalente e muito mais rápido (o filtro combinado
    aceita ~11% das combinações aleatórias).
    """
    rng = random.Random(seed)
    exemplos = []
    tentativas = 0
    max_tentativas = 200_000
    while len(exemplos) < n_exemplos and tentativas < max_tentativas:
        tentativas += 1
        candidato = sorted(rng.sample(TODAS_DEZENAS, 15))
        if aplicar_filtros_combinatorios([candidato], **filtros_kwargs):
            if candidato not in exemplos:
                exemplos.append(candidato)
    return exemplos


def backtest_combinacoes_fixas(combinacoes, resultados=None):
    """
    Para cada combinação fixa (uma lista de 15 dezenas), confere quantos
    acertos ela teria feito em CADA concurso real do histórico. Diferente
    do backtest dos métodos M1-M5 (que gera um jogo novo por concurso),
    aqui é a MESMA combinação testada contra todos os sorteios já
    realizados — serve para mostrar que mesmo uma combinação "bem
    filtrada" tem média de acertos igual à esperança teórica no longo
    prazo, sem nenhuma vantagem preditiva.
    """
    if resultados is None:
        resultados = carregar_resultados()

    linhas = []
    for idx, combinacao in enumerate(combinacoes, start=1):
        combinacao_set = set(combinacao)
        acertos_lista = [len(combinacao_set & r["dezenas"]) for r in resultados]
        n = len(acertos_lista)
        media = statistics.mean(acertos_lista) if n else 0.0
        desvio = statistics.pstdev(acertos_lista) if n > 1 else 0.0
        dist = Counter(acertos_lista)
        linhas.append({
            "exemplo": idx,
            "dezenas": "-".join(f"{d:02d}" for d in sorted(combinacao)),
            "total_concursos_testados": n,
            "media_acertos": round(media, 4),
            "desvio_padrao_acertos": round(desvio, 4),
            "esperanca_teorica": ESPERANCA_TEORICA,
            "diferenca_vs_esperanca": round(media - ESPERANCA_TEORICA, 4),
            "max_acertos_observado": max(acertos_lista) if n else "",
            "pct_11_ou_mais": round(100 * sum(1 for a in acertos_lista if a >= 11) / n, 4) if n else 0.0,
            "pct_13_ou_mais": round(100 * sum(1 for a in acertos_lista if a >= 13) / n, 4) if n else 0.0,
            "qtd_15_acertos": dist.get(15, 0),
        })
    return linhas

