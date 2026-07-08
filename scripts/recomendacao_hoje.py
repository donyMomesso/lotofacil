from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import cast

import lotofacil_lib

GeradorMetodos = Callable[[int | None, int | None], dict[str, list[int]]]

gerar_todos_metodos = cast(GeradorMetodos, lotofacil_lib.gerar_todos_metodos)

METHOD_LABELS = {
    "M1_aleatorio_puro": "M1 Aleatorio",
    "M2_mais_frequentes": "M2 Mais frequentes",
    "M3_mais_atrasadas": "M3 Mais atrasadas",
    "M4_par_impar_balanceado": "M4 Par/impar balanceado",
    "M5_soma_faixa_comum": "M5 Soma faixa comum",
    "M6_filtros_combinados": "M6 Filtros combinados",
    "M7_cobertura_pares": "M7 Cobertura pares",
    "M8_repeticao_controlada": "M8 Repeticao controlada",
    "M9_tese_v2": "M9 Tese V2",
}

METHOD_ORDER = [
    "M1_aleatorio_puro",
    "M2_mais_frequentes",
    "M3_mais_atrasadas",
    "M4_par_impar_balanceado",
    "M5_soma_faixa_comum",
    "M6_filtros_combinados",
    "M7_cobertura_pares",
    "M8_repeticao_controlada",
    "M9_tese_v2",
]


def dezenas_texto(dezenas: list[int]) -> str:
    return "-".join(f"{d:02d}" for d in dezenas)


def medir_jogo(metodo: str, dezenas: list[int]) -> dict[str, int | str | list[int]]:
    jogo = sorted(int(d) for d in dezenas)
    soma = sum(jogo)
    pares = sum(1 for d in jogo if d % 2 == 0)
    inicio = min(jogo)
    miolo = sum(1 for d in jogo if d in {7, 8, 9, 12, 13, 14, 17, 18, 19})

    # Ranking conservador: privilegia inicio 1-3, aceita 4 com perda,
    # soma perto de 200, pares 6-9 e miolo controlado.
    penalidade = 0
    penalidade += abs(soma - 200)
    if soma < 180 or soma > 220:
        penalidade += 30
    if pares < 6 or pares > 9:
        penalidade += 20
    if inicio > 4:
        penalidade += 60
    elif inicio == 4:
        penalidade += 12
    if miolo < 5 or miolo > 8:
        penalidade += 15
    if metodo == "M9_tese_v2":
        penalidade -= 8
    if metodo == "M3_mais_atrasadas":
        penalidade -= 4

    return {
        "metodo": metodo,
        "label": METHOD_LABELS.get(metodo, metodo),
        "dezenas": jogo,
        "inicio": inicio,
        "soma": soma,
        "pares": pares,
        "impares": 15 - pares,
        "miolo": miolo,
        "penalidade": penalidade,
    }


def explicar_status(info: dict[str, int | str | list[int]]) -> str:
    inicio = int(info["inicio"])
    soma = int(info["soma"])
    pares = int(info["pares"])
    miolo = int(info["miolo"])

    alertas: list[str] = []
    if inicio <= 3:
        alertas.append("inicio forte")
    elif inicio == 4:
        alertas.append("inicio 4 raro/aceitavel")
    else:
        alertas.append("inicio fraco")

    if 190 <= soma <= 210:
        alertas.append("soma ideal")
    elif 180 <= soma <= 220:
        alertas.append("soma aceitavel")
    else:
        alertas.append("soma fora")

    if 6 <= pares <= 9:
        alertas.append("pares ok")
    else:
        alertas.append("pares fora")

    if 5 <= miolo <= 8:
        alertas.append("miolo ok")
    else:
        alertas.append("miolo fora")

    return ", ".join(alertas)


def main() -> None:
    seed_hoje = int(datetime.now().strftime("%Y%m%d"))
    metodos = gerar_todos_metodos(seed_hoje, None)

    jogos = [
        medir_jogo(metodo, metodos[metodo])
        for metodo in METHOD_ORDER
        if metodo in metodos
    ]
    ranking = sorted(jogos, key=lambda item: int(item["penalidade"]))

    print("=" * 92)
    print("  RECOMENDACOES PARA HOJE - 9 METODOS DO SISTEMA")
    print("=" * 92)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    print(f"Seed: {seed_hoje}")
    print("Objetivo tecnico: filtrar jogos ruins e estudar candidatos para 11+ acertos.")
    print("Aviso: isto e estudo estatistico, nao previsao garantida.")

    print("\n" + "=" * 92)
    print("RANKING PELO FILTRO ATUAL")
    print("=" * 92)
    print(f"{'#':<3} {'Metodo':<30} {'Inicio':<7} {'Soma':<6} {'Pares':<6} {'Miolo':<6} Dezenas")
    print("-" * 92)
    for posicao, info in enumerate(ranking, start=1):
        dezenas = cast(list[int], info["dezenas"])
        print(
            f"{posicao:<3} {str(info['label']):<30} "
            f"{int(info['inicio']):02d}      {int(info['soma']):<6} "
            f"{int(info['pares']):<6} {int(info['miolo']):<6} {dezenas_texto(dezenas)}"
        )

    print("\n" + "=" * 92)
    print("DETALHE DOS 9 METODOS")
    print("=" * 92)
    for info in jogos:
        dezenas = cast(list[int], info["dezenas"])
        print(f"\n{info['label']}")
        print(f"Dezenas: {dezenas_texto(dezenas)}")
        print(
            f"Inicio: {int(info['inicio']):02d} | Soma: {int(info['soma'])} | "
            f"Pares: {int(info['pares'])} | Impares: {int(info['impares'])} | "
            f"Miolo: {int(info['miolo'])}"
        )
        print(f"Leitura: {explicar_status(info)}")

    melhor = ranking[0]
    melhor_dezenas = cast(list[int], melhor["dezenas"])

    print("\n" + "=" * 92)
    print("RECOMENDACAO DO FILTRO")
    print("=" * 92)
    print(f"Primeira escolha tecnica: {melhor['label']}")
    print(f"Jogo: {dezenas_texto(melhor_dezenas)}")
    print(f"Motivo: {explicar_status(melhor)}")
    print("\nUse os 9 como base de comparacao. O sistema deve aprender com a conferencia real.")


if __name__ == "__main__":
    main()
