import lotofacil_lib as lib


if __name__ == "__main__":
    destino = lib.exportar_estatisticas_para_json(janela=50)
    print(f"Estatisticas exportadas para {destino}")
