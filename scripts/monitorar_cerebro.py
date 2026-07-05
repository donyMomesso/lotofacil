import lotofacil_lib as lib


def monitorar():
    print("--- INICIANDO CEREBRO ESTATISTICO ---")

    freq, atraso, total = lib.frequencia_e_atraso()
    if total == 0:
        print("Nenhum resultado encontrado em dados/resultados_lotofacil.csv.")
        return

    print(f"Historico carregado: {total} concurso(s).")
    print("Processando top 15 dezenas mais frequentes...")

    metodo = lib.metodo_mais_frequentes(None, freq)
    dezenas = sorted(metodo)
    soma = sum(dezenas)
    pares = sum(1 for dezena in dezenas if dezena % 2 == 0)
    impares = len(dezenas) - pares

    print(f"Decisao tomada: {dezenas}")
    print("Aplicando filtros de soma e par/impar...")
    print(f"Resultado do filtro: Soma={soma}, Pares={pares}, Impares={impares}")

    top_frequencias = sorted(dezenas, key=lambda dezena: (-freq[dezena], dezena))
    print("Frequencia das dezenas escolhidas:")
    for dezena in top_frequencias:
        print(f"  {dezena:02d}: freq={freq[dezena]}, atraso={atraso[dezena]}")

    if 180 <= soma <= 210 and 6 <= pares <= 8:
        print(">> Jogo aprovado pelo cerebro!")
    else:
        print(">> Jogo descartado (fora do padrao).")

    print("Aviso: isto e monitoramento estatistico, nao previsao de sorteio.")


if __name__ == "__main__":
    monitorar()
