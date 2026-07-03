"""
Monta o bloco de texto do diário estatístico do dia, seguindo a
estrutura de 5 pontos exigida pelas regras do laboratório:
  1. O que foi observado
  2. O que isso pode significar estatisticamente
  3. O que isso não significa
  4. Risco de confundir padrão histórico com previsão
  5. Conclusão educativa

Gerado de forma automática (template), por isso é propositalmente
conservador na linguagem: nunca compara métodos como "melhor" ou "mais
perto de ganhar", sempre ancora na esperança teórica de 9 acertos.
"""
import lotofacil_lib as lib


def montar_bloco_diario(data_str, novos_concursos, conferencias_do_dia, jogos_do_proximo, proximo_concurso, total_concursos):
    linhas = [f"## {data_str}", ""]

    if not novos_concursos:
        linhas += [
            "Nenhum concurso novo encontrado nesta execução (pode ser dia sem sorteio da Lotofácil, "
            "ou a fonte de dados ainda não publicou o resultado). Nenhuma alteração feita — a tarefa "
            "tenta de novo na próxima execução.",
            "",
        ]
        return "\n".join(linhas)

    linhas.append("**1. O que foi observado**")
    linhas.append("")
    for c in novos_concursos:
        confs = [x for x in conferencias_do_dia if x["concurso"] == c]
        if confs:
            resumo = ", ".join(f"{x['metodo']}: {x['acertos']} acerto(s)" for x in confs)
            linhas.append(f"- Concurso {c}: registrado e conferido contra os jogos de estudo — {resumo}.")
        else:
            linhas.append(f"- Concurso {c}: registrado no histórico (sem jogos de estudo com esse concurso como alvo).")
    linhas.append("")

    linhas.append("**2. O que isso pode significar estatisticamente**")
    linhas.append("")
    if conferencias_do_dia:
        acertos_hoje = [x["acertos"] for x in conferencias_do_dia]
        media_hoje = sum(acertos_hoje) / len(acertos_hoje)
        linhas.append(
            f"A média de acertos dos jogos de estudo hoje foi {media_hoje:.2f}, contra a esperança "
            f"teórica de {lib.ESPERANCA_TEORICA} por jogo (distribuição hipergeométrica). Diferenças "
            f"pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar "
            f"conforme mais concursos entram na série."
        )
    else:
        linhas.append(
            "Sem conferência nesta execução, não há novo dado de desempenho por método para interpretar "
            "hoje — só a atualização do histórico e da frequência das dezenas."
        )
    linhas.append("")

    linhas.append("**3. O que isso não significa**")
    linhas.append("")
    linhas.append(
        "Não significa que algum método está \"mais perto\" de 14 ou 15 acertos, nem que a frequência "
        "ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é "
        "independente dos anteriores — a bola não tem memória."
    )
    linhas.append("")

    linhas.append("**4. Risco de confundir padrão histórico com previsão**")
    linhas.append("")
    linhas.append(
        "Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um "
        "sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho "
        "em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que "
        "este laboratório existe para demonstrar, não para praticar."
    )
    linhas.append("")

    linhas.append("**5. Conclusão educativa**")
    linhas.append("")
    linhas.append(
        f"O histórico real agora tem {total_concursos} concurso(s). Quanto mais dados entram, mais "
        f"estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do "
        f"mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do "
        f"acaso, não encontrar um método vencedor."
    )
    linhas.append("")

    if jogos_do_proximo:
        linhas.append(
            f"*Jogos fictícios gerados para o concurso {proximo_concurso} "
            f"(estudo estatístico — não é recomendação de aposta):*"
        )
        linhas.append("")
        linhas.append("| Método | Dezenas |")
        linhas.append("|---|---|")
        for metodo, dezenas in jogos_do_proximo:
            linhas.append(f"| {metodo} | {'-'.join(f'{d:02d}' for d in sorted(dezenas))} |")
        linhas.append("")

    return "\n".join(linhas)


def anexar_diario(bloco):
    caminho = __import__("os").path.join(lib.BASE_DIR, "diario_estatistico.md")
    with open(caminho, "a", encoding="utf-8") as f:
        f.write("\n---\n\n")
        f.write(bloco)
        f.write("\n")
