"""
Ciclo diário completo do laboratório — pensado para rodar sozinho
(ex: GitHub Actions, com rede livre):

  1. Busca concursos novos (a partir do último registrado) via HTTP direto.
  2. Registra cada um no histórico real.
  3. Confere os jogos de estudo que tinham esses concursos como alvo.
  3b. Importa jogos manuais de dados/meus_jogos.csv (se existir).
  4. Gera os jogos de estudo do próximo concurso (5 métodos).
  5. Atualiza frequência/atraso e desempenho por método.
  6. Gera o relatório (reports/relatorio_estatistico.md).
  7. Gera o banco JSON do projeto (dados/banco_projeto.json).
  8. Gera o painel visual (painel.html + painel_jogos.html + painel_mobile.html).
  9. Anexa um bloco educativo em diario_estatistico.md.

Uso:
    python3 ciclo_diario.py
"""
from datetime import datetime, timezone, timedelta

import lotofacil_lib as lib
import gerar_relatorio
import gerar_banco_projeto
import gerar_painel
import gerar_painel_jogos
import gerar_painel_mobile
import conferir_meus_jogos
from diario import montar_bloco_diario, anexar_diario
from buscar_resultado import buscar_concurso

BRASILIA = timezone(timedelta(hours=-3))


def main():
    ultimo = lib.ultimo_concurso_registrado()
    proximo_a_buscar = (ultimo + 1) if ultimo else 1

    novos_concursos = []
    while True:
        resultado = buscar_concurso(proximo_a_buscar)
        if resultado is None:
            break
        novo = lib.registrar_resultado(resultado["concurso"], resultado["data"], set(resultado["dezenas"]))
        if novo:
            novos_concursos.append(resultado["concurso"])
            print(f"[ok] Concurso {resultado['concurso']} ({resultado['data']}) registrado.")
        proximo_a_buscar += 1

    # 3b. Importa jogos manuais antes de conferir
    conferir_meus_jogos.importar_meus_jogos()

    conferencias_do_dia = []
    resultados_map = {r["concurso"]: r for r in lib.carregar_resultados()}
    for c in novos_concursos:
        dezenas_sorteadas = resultados_map[c]["dezenas"]
        data_sorteio = resultados_map[c]["data"]
        jogos_do_concurso = [j for j in lib.carregar_jogos() if j["concurso_alvo"] == c]
        for j in jogos_do_concurso:
            acertos = lib.registrar_conferencia(c, data_sorteio, j["metodo"], j["dezenas_set"], dezenas_sorteadas)
            if acertos is not None:
                conferencias_do_dia.append({"concurso": c, "metodo": j["metodo"], "acertos": acertos})
                print(f"[ok] {j['metodo']} no concurso {c}: {acertos} acerto(s)")

    ultimo_atual = lib.ultimo_concurso_registrado()
    proximo_concurso = (ultimo_atual + 1) if ultimo_atual else 1
    jogos_gerados_map = lib.gerar_todos_metodos(ate_concurso=proximo_concurso - 1)
    data_geracao = datetime.now(BRASILIA).strftime("%d/%m/%Y")
    jogos_do_proximo = []
    for metodo, dezenas in jogos_gerados_map.items():
        if not lib.jogo_ja_gerado(proximo_concurso, metodo):
            lib.registrar_jogo(data_geracao, proximo_concurso, metodo, dezenas)
            jogos_do_proximo.append((metodo, dezenas))
            print(f"[ok] {metodo} gerado para concurso {proximo_concurso}")

    lib.salvar_frequencia_dezenas()
    lib.salvar_estatisticas_metodos()

    gerar_relatorio.main()
    gerar_banco_projeto.main()
    gerar_painel.main()
    gerar_painel_jogos.main()
    gerar_painel_mobile.main()

    total_concursos = len(lib.carregar_resultados())
    bloco = montar_bloco_diario(
        data_str=datetime.now(BRASILIA).strftime("%d/%m/%Y"),
        novos_concursos=novos_concursos,
        conferencias_do_dia=conferencias_do_dia,
        jogos_do_proximo=jogos_do_proximo,
        proximo_concurso=proximo_concurso,
        total_concursos=total_concursos,
    )
    anexar_diario(bloco)

    print(f"\nResumo: {len(novos_concursos)} concurso(s) novo(s), "
          f"{len(conferencias_do_dia)} conferência(s), "
          f"{len(jogos_do_proximo)} jogo(s) gerado(s) para o concurso {proximo_concurso}.")


if __name__ == "__main__":
    main()
