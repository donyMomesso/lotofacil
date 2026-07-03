"""
Gera reports/relatorio_estatistico.md: um resumo em linguagem simples
do estado atual do laboratório, a partir de dados reais.

Uso:
    python3 gerar_relatorio.py
"""
import os
import statistics
from datetime import datetime, timezone, timedelta

import lotofacil_lib as lib

REPORT_PATH = os.path.join(lib.BASE_DIR, "reports", "relatorio_estatistico.md")
BRASILIA = timezone(timedelta(hours=-3))


def linhas_do_concurso(dezenas):
    faixas = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 25)]
    return {f"linha_{a:02d}_{b:02d}": sum(1 for d in dezenas if a <= d <= b) for a, b in faixas}


def main():
    resultados = lib.carregar_resultados()
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

    linhas_md = [
        "# Relatório Estatístico Educativo — Lotofácil",
        "",
        f"_Atualizado em {datetime.now(BRASILIA).strftime('%d/%m/%Y %H:%M')} (horário de Brasília)_",
        "",
        "Este relatório é gerado automaticamente a partir de resultados reais da Lotofácil. "
        "Serve para estudo estatístico. Não prevê resultados, não recomenda apostas e não indica "
        "que qualquer combinação está mais perto de dar 14 ou 15 pontos.",
        "",
    ]

    if not resultados:
        linhas_md.append("Ainda não há concursos registrados.")
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas_md))
        print(f"Relatório criado em: {REPORT_PATH}")
        return

    somas = [sum(r["dezenas"]) for r in resultados]
    pares_por_concurso = [sum(1 for d in r["dezenas"] if d % 2 == 0) for r in resultados]

    linhas_md += [
        "## Base analisada",
        "",
        f"- Total de concursos no histórico: {len(resultados)}",
        f"- Concurso mais recente: {resultados[-1]['concurso']} ({resultados[-1]['data']})",
        f"- Soma média das dezenas por concurso: {statistics.mean(somas):.2f}",
        f"- Menor soma observada: {min(somas)}",
        f"- Maior soma observada: {max(somas)}",
        f"- Média de pares por concurso: {statistics.mean(pares_por_concurso):.2f} (de 15 dezenas)",
        "",
        "## Último concurso",
        "",
    ]

    ultimo = resultados[-1]
    dez = sorted(ultimo["dezenas"])
    pares = sum(1 for d in dez if d % 2 == 0)
    linhas_md += [
        f"- Concurso: {ultimo['concurso']}",
        f"- Data: {ultimo['data']}",
        f"- Dezenas: {'-'.join(f'{d:02d}' for d in dez)}",
        f"- Soma: {sum(dez)}",
        f"- Pares: {pares} / Ímpares: {15 - pares}",
        "",
        "### Distribuição por linha (faixas de 5 dezenas)",
        "",
    ]
    for nome, valor in linhas_do_concurso(dez).items():
        linhas_md.append(f"- {nome}: {valor}")

    freq, atraso, total = lib.frequencia_e_atraso()
    mais_frequentes = sorted(lib.TODAS_DEZENAS, key=lambda d: freq[d], reverse=True)[:5]
    menos_frequentes = sorted(lib.TODAS_DEZENAS, key=lambda d: freq[d])[:5]
    mais_atrasadas = sorted(lib.TODAS_DEZENAS, key=lambda d: atraso[d], reverse=True)[:5]

    linhas_md += ["", "## Frequência das dezenas (histórico completo)", "", "### Mais frequentes", ""]
    for d in mais_frequentes:
        linhas_md.append(f"- {d:02d}: {freq[d]} vez(es) ({100 * freq[d] / total:.1f}%)")
    linhas_md += ["", "### Menos frequentes", ""]
    for d in menos_frequentes:
        linhas_md.append(f"- {d:02d}: {freq[d]} vez(es) ({100 * freq[d] / total:.1f}%)")
    linhas_md += ["", "### Maior atraso atual (concursos sem sair)", ""]
    for d in mais_atrasadas:
        linhas_md.append(f"- {d:02d}: {atraso[d]} concurso(s)")

    stats_metodos = lib.calcular_estatisticas_metodos()
    linhas_md += [
        "",
        "## Desempenho comparado dos métodos (jogos fictícios de estudo)",
        "",
        f"Valor teórico esperado de acertos por jogo de 15 dezenas: **{lib.ESPERANCA_TEORICA}** "
        "(distribuição hipergeométrica — todo método tende a esse valor no longo prazo).",
        "",
        "| Método | Jogos conferidos | Média de acertos | Desvio padrão | % com 11+ | % com 13+ |",
        "|---|---|---|---|---|---|",
    ]
    for l in stats_metodos:
        linhas_md.append(
            f"| {l['metodo']} | {l['total_jogos_conferidos']} | {l['media_acertos']} | "
            f"{l['desvio_padrao_acertos']} | {l['pct_11_ou_mais']}% | {l['pct_13_ou_mais']}% |"
        )

    linhas_md += [
        "",
        "## Conclusão educativa",
        "",
        "Frequência e atraso mostram apenas o que já aconteceu na amostra observada — não indicam "
        "o que vai sair no próximo concurso. Cada sorteio é independente dos anteriores. Se, com o "
        "tempo, os métodos acima convergirem para uma média de acertos parecida com a esperança "
        "teórica, isso confirma que a Lotofácil se comporta como um sorteio aleatório, não que algum "
        "método é melhor para ganhar.",
        "",
    ]

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_md))
    print(f"Relatório criado em: {REPORT_PATH}")


if __name__ == "__main__":
    main()
