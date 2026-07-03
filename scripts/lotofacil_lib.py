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
]


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


def metodo_aleatorio_puro(rng):
    return set(rng.sample(TODAS_DEZENAS, 15))


def metodo_mais_frequentes(rng, freq):
    # ordena por frequência desc; empates quebrados aleatoriamente para não
    # favorecer sistematicamente dezenas menores
    dezenas = TODAS_DEZENAS[:]
    rng.shuffle(dezenas)
    dezenas.sort(key=lambda d: freq[d], reverse=True)
    return set(dezenas[:15])


def metodo_mais_atrasadas(rng, atraso):
    dezenas = TODAS_DEZENAS[:]
    rng.shuffle(dezenas)
    dezenas.sort(key=lambda d: atraso[d], reverse=True)
    return set(dezenas[:15])


def metodo_par_impar_balanceado(rng, alvo_pares=8, max_tentativas=500):
    for _ in range(max_tentativas):
        candidato = rng.sample(TODAS_DEZENAS, 15)
        pares = sum(1 for d in candidato if d % 2 == 0)
        if pares == alvo_pares:
            return set(candidato)
    return metodo_aleatorio_puro(rng)  # fallback, não deve ocorrer na prática


def metodo_soma_faixa_comum(rng, faixa_min=180, faixa_max=210, max_tentativas=1000):
    for _ in range(max_tentativas):
        candidato = rng.sample(TODAS_DEZENAS, 15)
        if faixa_min <= sum(candidato) <= faixa_max:
            return set(candidato)
    return metodo_aleatorio_puro(rng)  # fallback


def gerar_todos_metodos(seed=None, ate_concurso=None):
    rng = random.Random(seed)
    freq, atraso, _ = frequencia_e_atraso(ate_concurso)
    return {
        "M1_aleatorio_puro": metodo_aleatorio_puro(rng),
        "M2_mais_frequentes": metodo_mais_frequentes(rng, freq),
        "M3_mais_atrasadas": metodo_mais_atrasadas(rng, atraso),
        "M4_par_impar_balanceado": metodo_par_impar_balanceado(rng),
        "M5_soma_faixa_comum": metodo_soma_faixa_comum(rng),
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
