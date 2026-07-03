"""
Busca um resultado de concurso via HTTP direto (biblioteca `requests`).

Isto só funciona em ambientes com rede livre (ex: runner do GitHub
Actions). No sandbox do Cowork a rede é restrita e quem busca dados é
o agente, usando a ferramenta de fetch web e depois
`registrar_resultado.py` para gravar o resultado já obtido.

Uso:
    python3 buscar_resultado.py <concurso>
    (imprime "concurso;data;d1,d2,...,d15" em stdout, ou nada se o
    concurso ainda não foi sorteado)
"""
import sys

import requests

BASE_URL = "https://loteriascaixa-api.herokuapp.com/api/lotofacil"


def buscar_concurso(concurso, timeout=20):
    try:
        resp = requests.get(f"{BASE_URL}/{concurso}", timeout=timeout)
    except requests.RequestException:
        return None

    if resp.status_code != 200 or not resp.text.strip():
        return None

    try:
        data = resp.json()
    except ValueError:
        return None

    if not data or "dezenas" not in data or not data["dezenas"]:
        return None

    return {
        "concurso": int(data["concurso"]),
        "data": data["data"],
        "dezenas": sorted(int(d) for d in data["dezenas"]),
    }


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 buscar_resultado.py <concurso>", file=sys.stderr)
        sys.exit(1)

    concurso = int(sys.argv[1])
    resultado = buscar_concurso(concurso)
    if resultado is None:
        return  # silêncio proposital: sinaliza "ainda não sorteado / indisponível"

    dezenas_str = ",".join(str(d) for d in resultado["dezenas"])
    print(f"{resultado['concurso']};{resultado['data']};{dezenas_str}")


if __name__ == "__main__":
    main()
