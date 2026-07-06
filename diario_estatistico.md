# Diário Estatístico — Laboratório Lotofácil

Registro educativo, um bloco por dia. Ver `LEIA-ME.md` para o que é (e o
que não é) este projeto.

---

## 03/07/2026 — Configuração inicial

**1. O que foi observado**
O laboratório foi criado hoje. Carreguei os últimos 17 concursos
disponíveis (3706 a 3725, com três concursos ausentes na fonte pública
— 3714, 3720, 3722 — que ficaram fora dessa amostra inicial) para
calcular uma frequência e um atraso de partida. Nessa janela pequena,
as dezenas 01 e 25 apareceram mais vezes (13 de 17 concursos, 76,5%) e
a dezena 13 apareceu menos (6 de 17, 35,3%). Gerei um jogo fictício de
15 dezenas por método (5 no total) com alvo no concurso 3726, ainda não
sorteado.

**2. O que isso pode significar estatisticamente**
Com apenas 17 concursos, qualquer diferença de frequência entre
dezenas é esperada só por variação amostral — não é indício de viés
físico nas bolas ou no sorteio. É o tipo de oscilação que qualquer
gerador aleatório de 15 números entre 1 e 25 produziria em uma amostra
desse tamanho.

**3. O que isso não significa**
Não significa que 01 e 25 "estão quentes" nem que 13 "está devendo".
Cada sorteio da Lotofácil é independente dos anteriores — a bola não
tem memória. Frequência passada não altera a probabilidade futura.

**4. Risco de confundir padrão histórico com previsão**
É fácil olhar para uma dezena que saiu 76% das vezes em 17 concursos e
achar que isso é um padrão forte. Com uma amostra tão pequena, esse
número tende a se estabilizar perto de 60% (proporção teórica: 15/25)
conforme mais concursos entram na conta. Tratar esse número atual como
sinal de algo é viés de confirmação clássico.

**5. Conclusão educativa**
A partir de amanhã, a cada novo resultado real, o histórico cresce e a
tabela de frequência tende a ficar mais estável e mais próxima da
proporção teórica (cada dezena aparece, em média, em 60% dos
concursos). Acompanhar essa convergência ao longo do tempo é o
objetivo do laboratório — não prever números "quentes" ou "atrasados"
para apostar.

*Jogos fictícios gerados para o concurso 3726 (nenhum deles é uma
recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 01-02-03-05-07-09-10-11-14-15-19-20-21-22-23 |
| M2_mais_frequentes | 01-02-04-05-06-09-12-14-15-18-20-21-22-24-25 |
| M3_mais_atrasadas | 01-03-05-07-08-09-10-12-13-15-16-18-20-22-23 |
| M4_par_impar_balanceado | 02-03-04-06-08-09-11-12-13-16-19-22-23-24-25 |
| M5_soma_faixa_comum | 02-03-04-06-07-09-11-13-14-15-16-17-19-21-23 |

Ainda sem conferências — o concurso 3726 sorteia hoje à noite. A
tarefa agendada de amanhã confere esses 5 jogos contra o resultado
real e começa a série de desempenho por método.

---

## 03/07/2026

Nenhum concurso novo encontrado nesta execução (pode ser dia sem sorteio da Lotofácil, ou a fonte de dados ainda não publicou o resultado). Nenhuma alteração feita — a tarefa tenta de novo na próxima execução.

---

## 04/07/2026 — Primeira conferência real

**1. O que foi observado**
O concurso 3726 (sorteado em 03/07/2026) trouxe as dezenas
02-05-06-07-10-13-14-17-18-19-20-21-22-24-25. Conferi os 5 jogos
fictícios gerados ontem para esse concurso: M1_aleatorio_puro fez 7
acertos, M2_mais_frequentes fez 9, M3_mais_atrasadas fez 8,
M4_par_impar_balanceado fez 8 e M5_soma_faixa_comum fez 10. O
histórico consolidado agora cobre 3.726 concursos, e a frequência de
cada dezena está entre 57,1% e 62,6% — todas próximas da proporção
teórica de 60% (15 dezenas sorteadas em 25 possíveis).

**2. O que isso pode significar estatisticamente**
Com uma amostra grande (3.726 concursos), a frequência de cada dezena
já convergiu bastante para o valor teórico de 60%, exatamente como
esperado pela lei dos grandes números. Quanto ao resultado dos 5
métodos no concurso 3726, os valores (7, 8, 8, 9 e 10 acertos) são
compatíveis com a distribuição hipergeométrica de um jogo de 15
dezenas, cuja esperança teórica é 9,0 acertos — variação de um único
concurso em torno dessa média é normal e esperada.

**3. O que isso não significa**
O fato de M5_soma_faixa_comum ter feito 10 acertos e M1_aleatorio_puro
ter feito 7 não indica que o método M5 é "melhor" ou está mais
propenso a repetir esse resultado. É um único concurso — estatisticamente,
isso não distingue os métodos entre si. Nenhum jogo aqui esteve "mais
perto" de 14 ou 15 pontos em algum sentido preditivo; 9, 10 ou 14
acertos em um sorteio são todos desvios possíveis em torno da mesma
esperança teórica.

**4. Risco de confundir padrão histórico com previsão**
Depois de só uma conferência, é tentador achar que o método com mais
acertos hoje vai continuar acertando mais. Isso é viés de confirmação:
com n=1 por método, qualquer diferença observada é ruído estatístico,
não sinal. Seria necessário acumular dezenas ou centenas de
conferências por método, e ainda assim o resultado esperado de todos
eles tende ao mesmo valor teórico (9,0), porque nenhum deles usa
informação real sobre o próximo sorteio — a Lotofácil não tem memória.

**5. Conclusão educativa**
A esperança teórica de 9,0 acertos em 15 dezenas é a referência para
qualquer método, aleatório ou não. Acompanhar essas conferências ao
longo de muitos concursos é útil para visualizar a variância em torno
dessa média — não para escolher "o método vencedor". Nenhum dos jogos
abaixo é recomendação de aposta.

*Jogos fictícios gerados para o concurso 3727 (ainda não sorteado; nenhum deles é
recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 02-03-08-10-11-13-15-16-17-18-20-22-23-24-25 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 01-03-04-05-08-09-11-12-13-15-16-18-22-23-24 |
| M4_par_impar_balanceado | 01-02-03-06-08-09-16-17-18-19-20-21-22-24-25 |
| M5_soma_faixa_comum | 04-05-06-08-09-10-11-12-14-16-17-18-21-23-24 |

---

## 03/07/2026 — Histórico completo importado

**1. O que foi observado**
O usuário forneceu uma planilha com todos os concursos da Lotofácil desde o início (concurso 1, 29/09/2003) até o concurso 3725 (02/07/2026) — 3725 concursos reais, contra os 17 que tínhamos antes. Os 3 concursos que faltavam na API pública (3714, 3720 e 3722) estavam presentes nessa planilha. Com a base completa, a frequência de cada dezena passou a variar entre 57,1% e 62,55% — bem diferente da faixa de 35% a 77% que víamos com apenas 17 concursos. Os jogos fictícios do concurso 3726 foram regerados com essa base completa (o concurso ainda não tinha sido sorteado, então nada se perdeu).

**2. O que isso pode significar estatisticamente**
Isso é exatamente o que a teoria prevê: quanto maior a amostra, mais a frequência observada de cada dezena se aproxima da proporção teórica (15/25 = 60%). Com 17 concursos, o acaso ainda tinha bastante "folga" para produzir diferenças grandes entre dezenas. Com 3725 concursos, essa folga praticamente desaparece — a Lei dos Grandes Números em ação.

**3. O que isso não significa**
Não significa que a Lotofácil "corrige" dezenas para ficarem em 60% — não existe esse mecanismo. O sorteio de cada concurso continua sendo independente e sem memória. A convergência é uma propriedade da estatística de longo prazo, não um comportamento programado do sorteio.

**4. Risco de confundir padrão histórico com previsão**
Mesmo com uma base gigante, ainda dá para achar "diferenças" entre dezenas (por exemplo, dezena 20 aparece em 62,55% dos concursos e dezena 16 em 57,1%). Tratar essa diferença de 5 pontos percentuais, depois de 3725 sorteios, como sinal de alguma coisa é ainda mais viés de confirmação do que antes — a diferença é pequena precisamente porque é ruído, não sinal.

**5. Conclusão educativa**
Esse é o melhor ponto de partida possível para o laboratório: agora frequência e atraso refletem o histórico real completo, não uma amostra pequena. Os métodos de estudo (especialmente M2 e M3, que dependem de frequência/atraso) agora partem de uma base estatisticamente sólida. A partir de agora, qualquer diferença de desempenho entre métodos que aparecer nas próximas conferências é ainda mais claramente atribuível ao acaso do sorteio — não à qualidade dos dados de entrada.

*Jogos fictícios regerados para o concurso 3726 com a base completa (não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 01-03-04-05-06-08-10-12-15-16-17-19-20-23-24 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 03-05-06-07-09-10-11-12-15-16-18-20-21-22-23 |
| M4_par_impar_balanceado | 01-02-04-06-09-10-11-14-15-16-19-22-23-24-25 |
| M5_soma_faixa_comum | 01-02-03-04-07-13-14-15-16-17-18-19-20-22-24 |

---

## 03/07/2026 — Simulação retroativa (backtest) nos 3724 concursos anteriores

**1. O que foi observado**
Rodei os 5 métodos retroativamente contra todo o histórico: para cada concurso a partir do 2º, cada método monta um jogo usando só os dados disponíveis antes daquele concurso (sem "olhar o futuro"), e o resultado é conferido contra o sorteio real. Isso deu 3724 concursos simulados por método, 18620 jogos de estudo no total — uma amostra imensa comparada às conferências do dia a dia. Resultado das médias de acerto: aleatório puro 9,0003, mais frequentes 9,0336, mais atrasadas 9,0263, par/ímpar balanceado 8,9817, soma na faixa comum 8,9936. Nenhum jogo, em nenhum dos 18620, teve 15 acertos; menos de 0,3% teve 13 ou mais em qualquer método.

**2. O que isso pode significar estatisticamente**
Com quase 4 mil observações por método, isso é uma confirmação forte da esperança teórica: todas as médias caem dentro de ±0,034 de 9,0 — uma diferença desprezível diante do desvio padrão de ~1,22. É exatamente o que a matemática do sorteio aleatório prevê, agora com uma amostra grande o suficiente para a diferença entre métodos deixar de ser ruído de amostra pequena e virar, de fato, evidência de que não há diferença real.

**3. O que isso não significa**
"Mais frequentes" (9,0336) não é o melhor método, e "par/ímpar balanceado" (8,9817) não é o pior. A diferença entre eles é de 0,05 acerto em 3724 tentativas — estatisticamente irrelevante perto da variância natural do sorteio. Nenhum desses números diz nada sobre o concurso 3726 ou qualquer concurso futuro.

**4. Risco de confundir padrão histórico com previsão**
Esse é o ponto mais importante do laboratório inteiro: mesmo depois de simular quase 4 mil concursos reais, nenhum dos 5 métodos "venceu" de forma consistente. Se alguém parasse de olhar no meio da série (por exemplo, só nos primeiros 200 concursos), poderia ver um método na frente e concluir, erroneamente, que "funciona". A amostra completa mostra que essa vantagem teria sido só sorte de curto prazo, dissolvida no longo prazo.

**5. Conclusão educativa**
Esta é a demonstração mais completa possível com os dados disponíveis: usar frequência histórica, atraso, paridade ou soma para montar um jogo não muda a média de acertos esperada. A Lotofácil se comportou, nesses 3724 concursos, exatamente como um sorteio aleatório sem memória deveria se comportar. Os arquivos `dados/simulacao_metodos.csv` (linha a linha) e `dados/estatisticas_simulacao.csv` (agregado) ficam disponíveis para quem quiser conferir os números por conta própria.

---

## 04/07/2026 — Apostas estendidas: por que "mirar em 11" tem preço, não truque

**1. O que foi observado**
A partir de uma dúvida legítima ("dá pra garantir uma média de acertos maior, tipo cobrir os dois lados numa moeda?"), calculamos a matemática das apostas estendidas da Lotofácil (de 16 a 20 dezenas por bilhete, em vez de 15). Resultado: a média esperada de acertos sobe de fato — 9,0 (15 dezenas) até 12,0 (20 dezenas) — mas o custo sobe pela mesma combinatória, de R$ 3,50 até R$ 54.264,00 por jogo. A chance de bater 11+ vai de 10,6% para 94,3%, só que o custo para "comprar" cada ponto percentual dessa chance cresce de R$ 0,33 para R$ 575,15 — ou seja, a eficiência do dinheiro piora conforme se tenta cobrir mais dezenas.

**2. O que isso pode significar estatisticamente**
Isso confirma, com números concretos, algo que já era esperado pela teoria: apostar em mais combinações ao mesmo tempo aumenta a chance bruta de acerto, mas não cria retorno esperado extra por real investido — porque o preço da aposta estendida é definido exatamente pelo número de combinações de 15 que ela contém (C(n,15)). É a mesma lógica de comprar vários bilhetes simples ao mesmo tempo, só que embutida em um único bilhete maior.

**3. O que isso não significa**
Não significa que existe uma forma de "prever" 9, 11 ou qualquer quantidade fixa de dezenas certas antes do sorteio. A ideia de "cobrir os dois lados como numa moeda" não se aplica aqui: apostar nos dois resultados de uma moeda não gera lucro, só devolve o valor apostado (menos taxas) — e fixar parte das dezenas de um jogo como "certas" também não funciona, porque nenhuma dezena escolhida tem prioridade sobre outra no sorteio real.

**4. Risco de confundir padrão histórico com previsão**
O risco aqui é sutil: ver a média subir de 9,0 para 12,0 pode parecer uma "vitória" da estratégia, mas essa subida não vem de nenhuma informação sobre o sorteio — vem simplesmente de pagar por milhares de combinações simultâneas. Comparar apostas de tamanhos diferentes pela média de acertos, sem considerar o custo, é uma forma de viés de confirmação: olha-se para o número que confirma a ideia (mais acertos) e ignora-se o número que a desmente (o custo por real investido não melhorou nem um pouco).

**5. Conclusão educativa**
A tabela de apostas estendidas (16 a 20 dezenas) foi incorporada ao relatório e ao painel do laboratório como um novo estudo permanente. Ela mostra, com matemática simples de combinatória, por que não existe atalho estatístico para aumentar a média de acertos "de graça": todo ganho de cobertura tem um custo proporcional (e, neste caso, um custo por ponto percentual que piora conforme a aposta cresce). Continua não sendo recomendação de aposta — é só a aritmética por trás da regra do jogo, deixada explícita.

| Dezenas na aposta | Combinações (C(n,15)) | Custo (R$) | Média esperada de acertos | % chance 11+ | Custo por ponto % de chance de 11+ |
|---|---|---|---|---|---|
| 15 | 1 | 3,50 | 9,00 | 10,59% | 0,33 |
| 16 | 16 | 56,00 | 9,60 | 22,16% | 2,53 |
| 17 | 136 | 476,00 | 10,20 | 39,31% | 12,11 |
| 18 | 816 | 2.856,00 | 10,80 | 60,14% | 47,49 |
| 19 | 3.876 | 13.566,00 | 11,40 | 80,22% | 169,12 |
| 20 | 15.504 | 54.264,00 | 12,00 | 94,35% | 575,15 |

---

## 04/07/2026 — Sequência e salto das trincas de dezenas consecutivas

**1. O que foi observado**
Calculamos, para cada trinca de 3 dezenas consecutivas (01-02-03 até 23-24-25), duas contagens no histórico de 3.726 concursos: "sequência" (quantas vezes as 3 saíram juntas no mesmo sorteio) e "salto" (quantas vezes nenhuma das 3 saiu). Os valores observados variam de 17,53% a 21,28% para sequência (média 19,56%, desvio 1,04 p.p.) e de 4,24% a 5,82% para salto (média 5,25%, desvio 0,40 p.p.).

**2. O que isso pode significar estatisticamente**
Calculamos também o valor teórico exato (hipergeométrico) que qualquer trinca específica de 3 dezenas deveria ter: 19,7826% de chance de sair inteira e 5,2174% de chance de nenhuma sair. As médias observadas praticamente coincidem com isso, e a dispersão entre trincas é do tamanho esperado para ruído amostral em 3.726 sorteios — nenhuma trinca foge do previsto pela matemática.

**3. O que isso não significa**
A trinca 10,11,12 (21,28%, a mais alta) não é uma trinca "quente", e a trinca 15,16,17 (17,53%, a mais baixa) não está "atrasada". Toda trinca de 3 dezenas consecutivas tem exatamente a mesma probabilidade teórica — a diferença entre elas na tabela é só flutuação normal de amostra.

**4. Risco de confundir padrão histórico com previsão**
Esse é um exemplo clássico de viés de confirmação: tabelas assim circulam por aí sem a linha teórica ao lado, o que convida a interpretar a variação como sinal de trinca melhor ou pior. Ao colocar o valor teórico fixo ao lado de cada linha, a tabela vira uma demonstração de ruído, não uma sugestão de escolha.

**5. Conclusão educativa**
Tabela adicionada ao relatório e ao painel (`scripts/tabela_sequencias.py`, dados em `dados/sequencias_saltos.csv`), sempre ao lado do valor teórico de referência. Reforça o padrão do laboratório: qualquer estatística de frequência, por mais que varie entre categorias, tende ao mesmo valor teórico fixo — a variação é o objeto de estudo, não um indicador de escolha.

---

## 04/07/2026 — Desdobramento, filtros compostos e backtest de combinações fixas

**1. O que foi observado**
Adicionamos ao `lotofacil_lib.py` funções de desdobramento (gerar todas as combinações de 15 dentro de uma base maior, a mesma matemática das apostas estendidas) e um pipeline de filtros compostos (par/ímpar, soma, sequência, linha vazia — os mesmos 4 filtros já estudados). A partir disso, geramos 5 combinações de exemplo que passam pelos 4 filtros e testamos cada uma, fixa, contra os 3.726 concursos reais do histórico inteiro. Resultado: médias entre 8,95 e 9,03 acertos (todas a menos de 0,05 da esperança teórica de 9,0), desvio padrão entre 1,20 e 1,24, máximo observado de 13-14 acertos, e zero ocorrências de 15 acertos em qualquer exemplo.

**2. O que isso pode significar estatisticamente**
Isso é uma confirmação adicional, agora com combinações fixas e reais (não simuladas por concurso): mesmo escolhendo dezenas que atendem a critérios "bem-comportados" (soma central, paridade equilibrada, sem sequência longa, distribuição por linha), o resultado ao longo de milhares de sorteios reais converge para a mesma esperança teórica de qualquer combinação aleatória.

**3. O que isso não significa**
Não significa que essas 5 combinações são recomendadas, nem que qualquer uma delas teria sido "melhor" de se jogar historicamente — a diferença entre a de maior média (9,033) e a de menor (8,954) é ruído estatístico, do mesmo tamanho que já vimos entre os métodos M1-M5. Nenhuma delas é sugestão de aposta.

**4. Risco de confundir padrão histórico com previsão**
Poderia parecer tentador escolher, entre os exemplos, o que teve a maior média histórica (exemplo 4, 9,033) e tratá-lo como "o exemplo bom". Isso seria o mesmo erro de sempre: escolher depois de ver o resultado (viés de retrospectiva) não muda a probabilidade da próxima vez — o exemplo 4 tem exatamente a mesma esperança teórica de 9,0 para o concurso 3727 que qualquer um dos outros quatro.

**5. Conclusão educativa**
As novas funções (`desdobramento_total`, `aplicar_filtros_combinatorios`, `gerar_exemplos_filtrados`, `backtest_combinacoes_fixas`) ficam disponíveis para gerar mais exemplos ilustrativos no futuro, sempre acompanhados do backtest completo contra o histórico real. Dados salvos em `dados/exemplos_filtrados_backtest.csv`. O padrão se mantém: qualquer forma de escolher 15 dezenas, filtrada ou não, tem a mesma esperança matemática — o valor do estudo está em demonstrar isso repetidamente com métodos diferentes, não em encontrar uma exceção.

| Exemplo | Dezenas | Média | Dif. vs. esperança | Máx. observado | 11+ | 13+ |
|---|---|---|---|---|---|---|
| 1 | 01-02-03-04-06-07-08-14-16-18-19-20-21-23-25 | 8,9656 | -0,0344 | 13 | 9,47% | 0,08% |
| 2 | 01-02-05-07-08-09-10-11-16-18-19-20-22-23-24 | 8,9909 | -0,0091 | 13 | 10,52% | 0,11% |
| 3 | 01-02-04-06-08-09-11-13-14-15-17-18-21-22-24 | 8,9828 | -0,0172 | 13 | 10,39% | 0,21% |
| 4 | 02-03-04-06-08-11-13-14-15-17-19-20-22-24-25 | 9,0330 | +0,0330 | 13 | 11,65% | 0,19% |
| 5 | 03-04-05-06-08-09-12-14-15-16-17-21-22-24-25 | 8,9538 | -0,0462 | 14 | 10,23% | 0,13% |

---

## 05/07/2026

**1. O que foi observado**

- Concurso 3727: registrado e conferido contra os jogos de estudo — M1_aleatorio_puro: 9 acerto(s), M2_mais_frequentes: 10 acerto(s), M3_mais_atrasadas: 11 acerto(s), M4_par_impar_balanceado: 8 acerto(s), M5_soma_faixa_comum: 9 acerto(s).

**2. O que isso pode significar estatisticamente**

A média de acertos dos jogos de estudo hoje foi 9.40, contra a esperança teórica de 9.0 por jogo (distribuição hipergeométrica). Diferenças pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar conforme mais concursos entram na série.

**3. O que isso não significa**

Não significa que algum método está "mais perto" de 14 ou 15 acertos, nem que a frequência ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é independente dos anteriores — a bola não tem memória.

**4. Risco de confundir padrão histórico com previsão**

Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que este laboratório existe para demonstrar, não para praticar.

**5. Conclusão educativa**

O histórico real agora tem 3727 concurso(s). Quanto mais dados entram, mais estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do acaso, não encontrar um método vencedor.

*Jogos fictícios gerados para o concurso 3728 (estudo estatístico — não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 03-05-06-07-09-11-12-13-14-16-17-18-20-23-24 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 02-03-06-07-08-10-12-14-15-17-20-21-23-24-25 |
| M4_par_impar_balanceado | 01-02-03-06-08-09-11-12-14-15-16-18-19-20-21 |
| M5_soma_faixa_comum | 01-02-05-06-09-12-13-14-15-16-19-20-21-23-25 |


---

## 05/07/2026

Nenhum concurso novo encontrado nesta execução (pode ser dia sem sorteio da Lotofácil, ou a fonte de dados ainda não publicou o resultado). Nenhuma alteração feita — a tarefa tenta de novo na próxima execução.


---

## 05/07/2026

Nenhum concurso novo encontrado nesta execução (pode ser dia sem sorteio da Lotofácil, ou a fonte de dados ainda não publicou o resultado). Nenhuma alteração feita — a tarefa tenta de novo na próxima execução.

## 05/07/2026 - Backtest completo M1-M8

O backtest completo foi executado com 3.726 concursos avaliados e 149.040 jogos simulados, usando 5 jogos por método em cada concurso. A simulação respeitou a regra de usar apenas o histórico disponível até o concurso anterior.

Resultado agregado: todos os métodos continuaram próximos da esperança teórica de 9 acertos por jogo. Entre os percentuais de 11+ acertos, M2 ficou com 11,331%, M6 com 10,902%, M3 com 10,832%, M4 com 10,617%, M7 com 10,601%, M1 com 10,510%, M5 com 10,494% e M8 com 10,134%. Nenhum método registrou 15 acertos no backtest.

Arquivos atualizados: `dados/simulacao_metodos.csv`, `dados/estatisticas_simulacao.csv`, `reports/relatorio_estatistico.md`, `dados/banco_projeto.json` e painéis gerados.

---

## 06/07/2026

Nenhum concurso novo encontrado nesta execução (pode ser dia sem sorteio da Lotofácil, ou a fonte de dados ainda não publicou o resultado). Nenhuma alteração feita — a tarefa tenta de novo na próxima execução.

