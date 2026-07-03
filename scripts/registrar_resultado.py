"""
Registra um resultado real de concurso no histórico local.
Quem busca o dado na web é o agente (via web_fetch) — este script só
grava o que já foi obtido, para manter o sandbox de execução sem
depender de rede.

Uso:
    python3 registrar_resultado.py <concurso> <dd/mm/aaaa> <d1,d2,...,d15>

Exemplo:
    python3 registrar_resultado.py 3726 03/07/2026 1,2,3,5,6,7,9,10,12,14,16,18,20,22,25
"""
import sys

import lotofacil_lib as lib


def main():
    if len(sys.argv) < 4:
        print("Uso: python3 registrar_resultado.py <concurso> <dd/mm/aaaa> <d1,d2,...,d15>")
        sys.exit(1)

    concurso = int(sys.argv[1])
    data = sys.argv[2]
    dezenas = {int(x) for x in sys.argv[3].split(",")}

    if len(dezenas) != 15 or not all(1 <= d <= 25 for d in dezenas):
        print(f"Erro: esperado 15 dezenas distintas entre 1 e 25, recebi {sorted(dezenas)}")
        sys.exit(1)

    novo = lib.registrar_resultado(concurso, data, dezenas)
    if novo:
        print(f"[ok] Concurso {concurso} ({data}) registrado: "
              f"{'-'.join(f'{d:02d}' for d in sorted(dezenas))}")
    else:
        print(f"[skip] Concurso {concurso} já estava registrado.")


if __name__ == "__main__":
    main()
