"""
Gera dados/banco_projeto.json: um snapshot em JSON com o estado geral
 do laboratório.

Esse arquivo funciona como um "banco de leitura" para painel, celular,
integrações futuras ou qualquer ferramenta que queira consumir o projeto
sem precisar entender todos os CSVs separadamente.

Uso:
    python3 gerar_banco_projeto.py
"""
import csv
import json
import os
from datetime import datetime, timezone, timedelta

import lotofacil_lib as lib

BRASILIA = timezone(timedelta(hours=-3))
BANCO_PATH = os.path.join(lib.DADOS_DIR, "banco_projeto.json")


def _ler_csv(caminho, limite=None, reverso=False):
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    if reverso:
        linhas = linhas[::-1]
    if limite is not None:
        linhas = linhas[:limite]
    return linhas


def _resultado_para_json(r):
    return {
        "concurso": r["concurso"],
        "data": r["data"],
        "dezenas": sorted(r["dezenas"]),
        "dezenas_formatadas": "-".join(f"{d:02d}" for d in sorted(r["dezenas"])),
        "soma": sum(r["dezenas"]),
        "pares": sum(1 for d in r["dezenas"] if d % 2 == 0),
        "impares": sum(1 for d in r["dezenas"] if d % 2 != 0),
    }


def gerar_banco():
    os.makedirs(lib.DADOS_DIR, exist_ok=True)

    resultados = lib.carregar_resultados()
    ultimo = resultados[-1] if resultados else None
    proximo_concurso = (ultimo["concurso"] + 1) if ultimo else 1

    freq, atraso, total = lib.frequencia_e_atraso()
    stats_metodos = lib.calcular_estatisticas_metodos()

    jogos = lib.carregar_jogos()
    jogos_proximo = [{k: v for k, v in j.items() if k != "dezenas_set"} for j in jogos if j["concurso_alvo"] == proximo_concurso]

    conferencias = lib.carregar_conferencias()
    ultimas_conferencias = conferencias[-20:][::-1]

    estatisticas_simulacao = _ler_csv(os.path.join(lib.DADOS_DIR, "estatisticas_simulacao.csv"))

    banco = {
        "meta": {
            "nome": "Laboratório Estatístico Lotofácil",
            "tipo": "estudo_educativo",
            "gerado_em": datetime.now(BRASILIA).strftime("%d/%m/%Y %H:%M"),
            "timezone": "America/Sao_Paulo",
            "total_concursos": total,
            "ultimo_concurso": _resultado_para_json(ultimo) if ultimo else None,
            "proximo_concurso": proximo_concurso,
            "esperanca_teorica_acertos": lib.ESPERANCA_TEORICA,
            "aviso": "Estudo estatístico. Não prevê resultados e não recomenda apostas.",
        },
        "arquivos_principais": {
            "painel": "painel.html",
            "readme": "README.md",
            "diario": "diario_estatistico.md",
            "historico_resultados": "dados/resultados_lotofacil.csv",
            "jogos_gerados": "dados/jogos_gerados.csv",
            "conferencias": "dados/conferencia.csv",
            "frequencia": "dados/frequencia_dezenas.csv",
            "estatisticas_metodos": "dados/estatisticas_metodos.csv",
            "relatorio": "reports/relatorio_estatistico.md",
        },
        "ultimos_resultados": [_resultado_para_json(r) for r in resultados[-10:][::-1]],
        "frequencia_dezenas": [
            {
                "dezena": d,
                "dezena_formatada": f"{d:02d}",
                "frequencia_absoluta": freq[d],
                "frequencia_pct": round(100 * freq[d] / total, 2) if total else 0.0,
                "atraso_atual": atraso[d],
            }
            for d in lib.TODAS_DEZENAS
        ],
        "jogos_proximo_concurso": jogos_proximo,
        "ultimas_conferencias": ultimas_conferencias,
        "estatisticas_metodos": stats_metodos,
        "estatisticas_simulacao": estatisticas_simulacao,
        "links_internos": [
            {"titulo": "Painel visual", "arquivo": "painel.html"},
            {"titulo": "Relatório estatístico", "arquivo": "reports/relatorio_estatistico.md"},
            {"titulo": "Diário estatístico", "arquivo": "diario_estatistico.md"},
            {"titulo": "Histórico de resultados", "arquivo": "dados/resultados_lotofacil.csv"},
            {"titulo": "Banco do projeto", "arquivo": "dados/banco_projeto.json"},
        ],
    }

    return banco


def main():
    banco = gerar_banco()
    with open(BANCO_PATH, "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=2)
    print(f"Banco do projeto gerado em: {BANCO_PATH}")


if __name__ == "__main__":
    main()
