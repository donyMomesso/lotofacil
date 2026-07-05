import csv
import json
import os
import sys


def sql_quote(value):
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def main():
    destino = sys.argv[1] if len(sys.argv) > 1 else os.path.join("dados", "d1_import")
    os.makedirs(destino, exist_ok=True)

    with open(os.path.join("dados", "resultados_lotofacil.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    batch_size = 400
    files = []
    for batch_index, start in enumerate(range(0, len(rows), batch_size)):
        path = os.path.join(destino, f"resultados_{batch_index:03d}.sql")
        files.append(path)
        with open(path, "w", encoding="utf-8") as f:
            for row in rows[start:start + batch_size]:
                dezenas = [int(row[f"b{i:02d}"]) for i in range(1, 16)]
                values = [
                    int(row["concurso"]),
                    row["data"],
                    json.dumps(dezenas),
                    row["dezenas"],
                ]
                f.write(
                    "INSERT OR REPLACE INTO resultados "
                    "(concurso, data_sorteio, dezenas, dezenas_texto) VALUES ("
                    + ", ".join(sql_quote(value) for value in values)
                    + ");\n"
                )

    for path in files:
        print(path)


if __name__ == "__main__":
    main()
