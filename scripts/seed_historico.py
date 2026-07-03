"""
Semeia o arquivo dados/resultados_lotofacil.csv com os concursos
recentes obtidos manualmente da API pública (loteriascaixa-api).

Rodar apenas uma vez, na configuração inicial do laboratório.
Depois disso, o histórico é atualizado dia a dia pela tarefa agendada
(ver scripts/atualizar_resultado_diario.py).
"""
import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "dados", "resultados_lotofacil.csv")

# concurso, data (dd/mm/aaaa), 15 dezenas sorteadas (ordem crescente)
SEED = [
    (3706, "09/06/2026", [1,4,6,8,9,10,12,14,15,16,18,21,22,24,25]),
    (3707, "10/06/2026", [1,2,3,7,8,9,10,13,14,18,20,21,22,23,24]),
    (3708, "11/06/2026", [1,2,4,5,6,8,9,12,16,17,18,19,21,23,24]),
    (3709, "12/06/2026", [1,4,6,7,9,10,11,14,15,18,19,20,23,24,25]),
    (3710, "14/06/2026", [1,2,3,4,5,6,9,12,13,14,15,16,17,18,25]),
    (3711, "15/06/2026", [1,5,6,8,9,10,12,13,15,16,17,20,22,24,25]),
    (3712, "16/06/2026", [1,3,4,6,13,14,15,16,18,19,20,21,22,23,25]),
    (3713, "17/06/2026", [2,4,5,6,7,8,9,11,12,13,14,15,19,20,22]),
    (3715, "20/06/2026", [3,5,6,9,11,12,14,16,18,20,21,22,23,24,25]),
    (3716, "20/06/2026", [1,2,4,5,7,11,12,15,17,18,21,22,23,24,25]),
    (3717, "22/06/2026", [1,2,4,5,6,7,9,10,11,14,15,17,18,20,25]),
    (3718, "23/06/2026", [1,5,7,9,11,12,14,16,17,18,19,20,21,22,25]),
    (3719, "25/06/2026", [2,3,4,8,10,11,12,14,15,18,19,21,22,23,25]),
    (3721, "27/06/2026", [1,3,4,5,7,8,10,11,12,14,15,20,21,23,24]),
    (3723, "30/06/2026", [2,4,5,6,7,10,12,15,17,18,19,20,22,23,25]),
    (3724, "01/07/2026", [1,2,3,5,6,7,12,15,16,17,19,21,22,24,25]),
    (3725, "02/07/2026", [1,2,4,5,6,8,11,13,14,16,17,19,21,24,25]),
]
# Observação: concursos 3714, 3720 e 3722 não retornaram na API pública
# no momento da coleta (falha pontual da fonte) e ficaram fora do
# histórico inicial. Isso não compromete o estudo: a série volta a ser
# contínua a partir da atualização diária automática.

FIELDNAMES = ["concurso", "data"] + [f"b{i:02d}" for i in range(1, 16)] + ["dezenas"]


def main():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    if os.path.exists(CSV_PATH):
        print(f"Já existe {CSV_PATH} — nada a fazer (para não sobrescrever dados reais).")
        return

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for concurso, data, dezenas in SEED:
            dezenas_sorted = sorted(dezenas)
            row = {"concurso": concurso, "data": data}
            for i, d in enumerate(dezenas_sorted, start=1):
                row[f"b{i:02d}"] = d
            row["dezenas"] = "-".join(f"{d:02d}" for d in dezenas_sorted)
            writer.writerow(row)

    print(f"Histórico inicial gravado com {len(SEED)} concursos em {CSV_PATH}")


if __name__ == "__main__":
    main()
