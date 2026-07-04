"""
conferir_meus_jogos.py
======================
Integra os jogos manuais (dados/meus_jogos.csv) ao ciclo de conferência.

Como usar:
  1. No painel, clique em "Exportar CSV" na aba "Meus Jogos"
  2. Salve o arquivo como dados/meus_jogos.csv no repositório
  3. Este script é chamado automaticamente pelo ciclo_diario.py

O script lê meus_jogos.csv, registra cada jogo em jogos_gerados.csv
(usando metodo='MANUAL') e depois dispara a conferência normal.
"""
import os, csv, sys
sys.path.insert(0, os.path.dirname(__file__))
import lotofacil_lib as lib

MEUS_JOGOS_CSV = os.path.join(lib.DADOS_DIR, "meus_jogos.csv")


def importar_meus_jogos():
    """Lê meus_jogos.csv e registra em jogos_gerados.csv (idempotente)."""
    if not os.path.exists(MEUS_JOGOS_CSV):
        print("[meus_jogos] Arquivo meus_jogos.csv não encontrado — pulando.")
        return 0

    importados = 0
    with open(MEUS_JOGOS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            concurso = int(row["concurso_alvo"])
            metodo = row.get("metodo", "MANUAL").strip() or "MANUAL"
            dezenas_str = row["dezenas"].strip()
            dezenas = {int(d) for d in dezenas_str.split("-")}

            # Usa dezenas como chave de idempotência para jogos manuais
            ja_existe = any(
                j["concurso_alvo"] == concurso
                and j["metodo"] == metodo
                and j["dezenas"] == dezenas_str
                for j in lib.carregar_jogos()
            )
            if ja_existe:
                continue

            data = row.get("data_geracao", "").strip() or row.get("data", "").strip()
            lib.registrar_jogo(data, concurso, metodo, dezenas)
            importados += 1
            print(f"[meus_jogos] Importado: concurso={concurso} dezenas={dezenas_str}")

    print(f"[meus_jogos] {importados} jogo(s) importado(s) de meus_jogos.csv")
    return importados


if __name__ == "__main__":
    importar_meus_jogos()
