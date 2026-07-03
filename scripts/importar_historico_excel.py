"""
Importa um histórico completo de concursos a partir de uma planilha
.xlsx no formato "Concurso, Data, D. 1 ... D. 15" e substitui
dados/resultados_lotofacil.csv por esse histórico completo.

Uso:
    python3 importar_historico_excel.py <caminho_do_xlsx> [nome_da_aba]

Faz algumas validações antes de gravar:
  - cada concurso precisa ter 15 dezenas únicas entre 1 e 25
  - concursos duplicados são removidos (mantendo a primeira ocorrência)
  - a sequência de concursos não pode ter buracos (só avisa, não bloqueia)
"""
import csv
import sys

import pandas as pd

import lotofacil_lib as lib


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 importar_historico_excel.py <caminho_do_xlsx> [nome_da_aba]")
        sys.exit(1)

    caminho = sys.argv[1]
    aba = sys.argv[2] if len(sys.argv) > 2 else 0

    df = pd.read_excel(caminho, sheet_name=aba)
    dcols = [c for c in df.columns if str(c).startswith("D. ") or str(c).startswith("D.")]
    if len(dcols) != 15:
        print(f"Esperava 15 colunas de dezenas, encontrei {len(dcols)}: {dcols}")
        sys.exit(1)

    antes = len(df)
    df = df.drop_duplicates(subset=["Concurso"], keep="first").sort_values("Concurso")
    if len(df) != antes:
        print(f"[aviso] removidas {antes - len(df)} linha(s) duplicada(s) por número de concurso.")

    linhas_validas = []
    invalidas = 0
    for _, row in df.iterrows():
        dezenas = {int(row[c]) for c in dcols}
        if len(dezenas) != 15 or not all(1 <= d <= 25 for d in dezenas):
            invalidas += 1
            continue
        linhas_validas.append((int(row["Concurso"]), str(row["Data"]), sorted(dezenas)))

    if invalidas:
        print(f"[aviso] {invalidas} linha(s) descartada(s) por dezenas inválidas.")

    concursos = [c for c, _, _ in linhas_validas]
    faltando = sorted(set(range(min(concursos), max(concursos) + 1)) - set(concursos))
    if faltando:
        print(f"[aviso] concursos ausentes na sequência importada: {faltando}")

    fieldnames = ["concurso", "data"] + [f"b{i:02d}" for i in range(1, 16)] + ["dezenas"]
    with open(lib.RESULTADOS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for concurso, data, dezenas in linhas_validas:
            data_fmt = pd.to_datetime(data, dayfirst=True).strftime("%d/%m/%Y") if not isinstance(data, str) or "/" not in data else data
            row = {"concurso": concurso, "data": data_fmt}
            for i, d in enumerate(dezenas, start=1):
                row[f"b{i:02d}"] = d
            row["dezenas"] = "-".join(f"{d:02d}" for d in dezenas)
            writer.writerow(row)

    print(f"\nHistórico importado: {len(linhas_validas)} concursos "
          f"({linhas_validas[0][0]} a {linhas_validas[-1][0]}) gravados em {lib.RESULTADOS_CSV}")


if __name__ == "__main__":
    main()
