# DiÃ¡rio EstatÃ­stico â€” LaboratÃ³rio LotofÃ¡cil

Registro educativo, um bloco por dia. Ver `LEIA-ME.md` para o que Ã© (e o
que nÃ£o Ã©) este projeto.

---

## 03/07/2026 â€” ConfiguraÃ§Ã£o inicial

**1. O que foi observado**
O laboratÃ³rio foi criado hoje. Carreguei os Ãºltimos 17 concursos
disponÃ­veis (3706 a 3725, com trÃªs concursos ausentes na fonte pÃºblica
â€” 3714, 3720, 3722 â€” que ficaram fora dessa amostra inicial) para
calcular uma frequÃªncia e um atraso de partida. Nessa janela pequena,
as dezenas 01 e 25 apareceram mais vezes (13 de 17 concursos, 76,5%) e
a dezena 13 apareceu menos (6 de 17, 35,3%). Gerei um jogo fictÃ­cio de
15 dezenas por mÃ©todo (5 no total) com alvo no concurso 3726, ainda nÃ£o
sorteado.

**2. O que isso pode significar estatisticamente**
Com apenas 17 concursos, qualquer diferenÃ§a de frequÃªncia entre
dezenas Ã© esperada sÃ³ por variaÃ§Ã£o amostral â€” nÃ£o Ã© indÃ­cio de viÃ©s
fÃ­sico nas bolas ou no sorteio. Ã‰ o tipo de oscilaÃ§Ã£o que qualquer
gerador aleatÃ³rio de 15 nÃºmeros entre 1 e 25 produziria em uma amostra
desse tamanho.

**3. O que isso nÃ£o significa**
NÃ£o significa que 01 e 25 "estÃ£o quentes" nem que 13 "estÃ¡ devendo".
Cada sorteio da LotofÃ¡cil Ã© independente dos anteriores â€” a bola nÃ£o
tem memÃ³ria. FrequÃªncia passada nÃ£o altera a probabilidade futura.

**4. Risco de confundir padrÃ£o histÃ³rico com previsÃ£o**
Ã‰ fÃ¡cil olhar para uma dezena que saiu 76% das vezes em 17 concursos e
achar que isso Ã© um padrÃ£o forte. Com uma amostra tÃ£o pequena, esse
nÃºmero tende a se estabilizar perto de 60% (proporÃ§Ã£o teÃ³rica: 15/25)
conforme mais concursos entram na conta. Tratar esse nÃºmero atual como
sinal de algo Ã© viÃ©s de confirmaÃ§Ã£o clÃ¡ssico.

**5. ConclusÃ£o educativa**
A partir de amanhÃ£, a cada novo resultado real, o histÃ³rico cresce e a
tabela de frequÃªncia tende a ficar mais estÃ¡vel e mais prÃ³xima da
proporÃ§Ã£o teÃ³rica (cada dezena aparece, em mÃ©dia, em 60% dos
concursos). Acompanhar essa convergÃªncia ao longo do tempo Ã© o
objetivo do laboratÃ³rio â€” nÃ£o prever nÃºmeros "quentes" ou "atrasados"
para apostar.

*Jogos fictÃ­cios gerados para o concurso 3726 (nenhum deles Ã© uma
recomendaÃ§Ã£o de aposta):*

| MÃ©todo | Dezenas |
|---|---|
| M1_aleatorio_puro | 01-02-03-05-07-09-10-11-14-15-19-20-21-22-23 |
| M2_mais_frequentes | 01-02-04-05-06-09-12-14-15-18-20-21-22-24-25 |
| M3_mais_atrasadas | 01-03-05-07-08-09-10-12-13-15-16-18-20-22-23 |
| M4_par_impar_balanceado | 02-03-04-06-08-09-11-12-13-16-19-22-23-24-25 |
| M5_soma_faixa_comum | 02-03-04-06-07-09-11-13-14-15-16-17-19-21-23 |

Ainda sem conferÃªncias â€” o concurso 3726 sorteia hoje Ã  noite. A
tarefa agendada de amanhÃ£ confere esses 5 jogos contra o resultado
real e comeÃ§a a sÃ©rie de desempenho por mÃ©todo.

---

## 03/07/2026

Nenhum concurso novo encontrado nesta execuÃ§Ã£o (pode ser dia sem sorteio da LotofÃ¡cil, ou a fonte de dados ainda nÃ£o publicou o resultado). Nenhuma alteraÃ§Ã£o feita â€” a tarefa tenta de novo na prÃ³xima execuÃ§Ã£o.

---

## 04/07/2026 â€” Primeira conferÃªncia real

**1. O que foi observado**
O concurso 3726 (sorteado em 03/07/2026) trouxe as dezenas
02-05-06-07-10-13-14-17-18-19-20-21-22-24-25. Conferi os 5 jogos
fictÃ­cios gerados ontem para esse concurso: M1_aleatorio_puro fez 7
acertos, M2_mais_frequentes fez 9, M3_mais_atrasadas fez 8,
M4_par_impar_balanceado fez 8 e M5_soma_faixa_comum fez 10. O
histÃ³rico consolidado agora cobre 3.726 concursos, e a frequÃªncia de
cada dezena estÃ¡ entre 57,1% e 62,6% â€” todas prÃ³ximas da proporÃ§Ã£o
teÃ³rica de 60% (15 dezenas sorteadas em 25 possÃ­veis).

**2. O que isso pode significar estatisticamente**
Com uma amostra grande (3.726 concursos), a frequÃªncia de cada dezena
jÃ¡ convergiu bastante para o valor teÃ³rico de 60%, exatamente como
esperado pela lei dos grandes nÃºmeros. Quanto ao resultado dos 5
mÃ©todos no concurso 3726, os valores (7, 8, 8, 9 e 10 acertos) sÃ£o
compatÃ­veis com a distribuiÃ§Ã£o hipergeomÃ©trica de um jogo de 15
dezenas, cuja esperanÃ§a teÃ³rica Ã© 9,0 acertos â€” variaÃ§Ã£o de um Ãºnico
concurso em torno dessa mÃ©dia Ã© normal e esperada.

**3. O que isso nÃ£o significa**
O fato de M5_soma_faixa_comum ter feito 10 acertos e M1_aleatorio_puro
ter feito 7 nÃ£o indica que o mÃ©todo M5 Ã© "melhor" ou estÃ¡ mais
propenso a repetir esse resultado. Ã‰ um Ãºnico concurso â€” estatisticamente,
isso nÃ£o distingue os mÃ©todos entre si. Nenhum jogo aqui esteve "mais
perto" de 14 ou 15 pontos em algum sentido preditivo; 9, 10 ou 14
acertos em um sorteio sÃ£o todos desvios possÃ­veis em torno da mesma
esperanÃ§a teÃ³rica.

**4. Risco de confundir padrÃ£o histÃ³rico com previsÃ£o**
Depois de sÃ³ uma conferÃªncia, Ã© tentador achar que o mÃ©todo com mais
acertos hoje vai continuar acertando mais. Isso Ã© viÃ©s de confirmaÃ§Ã£o:
com n=1 por mÃ©todo, qualquer diferenÃ§a observada Ã© ruÃ­do estatÃ­stico,
nÃ£o sinal. Seria necessÃ¡rio acumular dezenas ou centenas de
conferÃªncias por mÃ©todo, e ainda assim o resultado esperado de todos
eles tende ao mesmo valor teÃ³rico (9,0), porque nenhum deles usa
informaÃ§Ã£o real sobre o prÃ³ximo sorteio â€” a LotofÃ¡cil nÃ£o tem memÃ³ria.

**5. ConclusÃ£o educativa**
A esperanÃ§a teÃ³rica de 9,0 acertos em 15 dezenas Ã© a referÃªncia para
qualquer mÃ©todo, aleatÃ³rio ou nÃ£o. Acompanhar essas conferÃªncias ao
longo de muitos concursos Ã© Ãºtil para visualizar a variÃ¢ncia em torno
dessa mÃ©dia â€” nÃ£o para escolher "o mÃ©todo vencedor". Nenhum dos jogos
abaixo Ã© recomendaÃ§Ã£o de aposta.

*Jogos fictÃ­cios gerados para o concurso 3727 (ainda nÃ£o sorteado; nenhum deles Ã©
recomendaÃ§Ã£o de aposta):*

| MÃ©todo | Dezenas |
|---|---|
| M1_aleatorio_puro | 02-03-08-10-11-13-15-16-17-18-20-22-23-24-25 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 01-03-04-05-08-09-11-12-13-15-16-18-22-23-24 |
| M4_par_impar_balanceado | 01-02-03-06-08-09-16-17-18-19-20-21-22-24-25 |
| M5_soma_faixa_comum | 04-05-06-08-09-10-11-12-14-16-17-18-21-23-24 |

---

## 03/07/2026 â€” HistÃ³rico completo importado

**1. O que foi observado**
O usuÃ¡rio forneceu uma planilha com todos os concursos da LotofÃ¡cil desde o inÃ­cio (concurso 1, 29/09/2003) atÃ© o concurso 3725 (02/07/2026) â€” 3725 concursos reais, contra os 17 que tÃ­nhamos antes. Os 3 concursos que faltavam na API pÃºblica (3714, 3720 e 3722) estavam presentes nessa planilha. Com a base completa, a frequÃªncia de cada dezena passou a variar entre 57,1% e 62,55% â€” bem diferente da faixa de 35% a 77% que vÃ­amos com apenas 17 concursos. Os jogos fictÃ­cios do concurso 3726 foram regerados com essa base completa (o concurso ainda nÃ£o tinha sido sorteado, entÃ£o nada se perdeu).

**2. O que isso pode significar estatisticamente**
Isso Ã© exatamente o que a teoria prevÃª: quanto maior a amostra, mais a frequÃªncia observada de cada dezena se aproxima da proporÃ§Ã£o teÃ³rica (15/25 = 60%). Com 17 concursos, o acaso ainda tinha bastante "folga" para produzir diferenÃ§as grandes entre dezenas. Com 3725 concursos, essa folga praticamente desaparece â€” a Lei dos Grandes NÃºmeros em aÃ§Ã£o.

**3. O que isso nÃ£o significa**
NÃ£o significa que a LotofÃ¡cil "corrige" dezenas para ficarem em 60% â€” nÃ£o existe esse mecanismo. O sorteio de cada concurso continua sendo independente e sem memÃ³ria. A convergÃªncia Ã© uma propriedade da estatÃ­stica de longo prazo, nÃ£o um comportamento programado do sorteio.

**4. Risco de confundir padrÃ£o histÃ³rico com previsÃ£o**
Mesmo com uma base gigante, ainda dÃ¡ para achar "diferenÃ§as" entre dezenas (por exemplo, dezena 20 aparece em 62,55% dos concursos e dezena 16 em 57,1%). Tratar essa diferenÃ§a de 5 pontos percentuais, depois de 3725 sorteios, como sinal de alguma coisa Ã© ainda mais viÃ©s de confirmaÃ§Ã£o do que antes â€” a diferenÃ§a Ã© pequena precisamente porque Ã© ruÃ­do, nÃ£o sinal.

**5. ConclusÃ£o educativa**
Esse Ã© o melhor ponto de partida possÃ­vel para o laboratÃ³rio: agora frequÃªncia e atraso refletem o histÃ³rico real completo, nÃ£o uma amostra pequena. Os mÃ©todos de estudo (especialmente M2 e M3, que dependem de frequÃªncia/atraso) agora partem de uma base estatisticamente sÃ³lida. A partir de agora, qualquer diferenÃ§a de desempenho entre mÃ©todos que aparecer nas prÃ³ximas conferÃªncias Ã© ainda mais claramente atribuÃ­vel ao acaso do sorteio â€” nÃ£o Ã  qualidade dos dados de entrada.

*Jogos fictÃ­cios regerados para o concurso 3726 com a base completa (nÃ£o Ã© recomendaÃ§Ã£o de aposta):*

| MÃ©todo | Dezenas |
|---|---|
| M1_aleatorio_puro | 01-03-04-05-06-08-10-12-15-16-17-19-20-23-24 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 03-05-06-07-09-10-11-12-15-16-18-20-21-22-23 |
| M4_par_impar_balanceado | 01-02-04-06-09-10-11-14-15-16-19-22-23-24-25 |
| M5_soma_faixa_comum | 01-02-03-04-07-13-14-15-16-17-18-19-20-22-24 |

---

## 03/07/2026 â€” SimulaÃ§Ã£o retroativa (backtest) nos 3724 concursos anteriores

**1. O que foi observado**
Rodei os 5 mÃ©todos retroativamente contra todo o histÃ³rico: para cada concurso a partir do 2Âº, cada mÃ©todo monta um jogo usando sÃ³ os dados disponÃ­veis antes daquele concurso (sem "olhar o futuro"), e o resultado Ã© conferido contra o sorteio real. Isso deu 3724 concursos simulados por mÃ©todo, 18620 jogos de estudo no total â€” uma amostra imensa comparada Ã s conferÃªncias do dia a dia. Resultado das mÃ©dias de acerto: aleatÃ³rio puro 9,0003, mais frequentes 9,0336, mais atrasadas 9,0263, par/Ã­mpar balanceado 8,9817, soma na faixa comum 8,9936. Nenhum jogo, em nenhum dos 18620, teve 15 acertos; menos de 0,3% teve 13 ou mais em qualquer mÃ©todo.

**2. O que isso pode significar estatisticamente**
Com quase 4 mil observaÃ§Ãµes por mÃ©todo, isso Ã© uma confirmaÃ§Ã£o forte da esperanÃ§a teÃ³rica: todas as mÃ©dias caem dentro de Â±0,034 de 9,0 â€” uma diferenÃ§a desprezÃ­vel diante do desvio padrÃ£o de ~1,22. Ã‰ exatamente o que a matemÃ¡tica do sorteio aleatÃ³rio prevÃª, agora com uma amostra grande o suficiente para a diferenÃ§a entre mÃ©todos deixar de ser ruÃ­do de amostra pequena e virar, de fato, evidÃªncia de que nÃ£o hÃ¡ diferenÃ§a real.

**3. O que isso nÃ£o significa**
"Mais frequentes" (9,0336) nÃ£o Ã© o melhor mÃ©todo, e "par/Ã­mpar balanceado" (8,9817) nÃ£o Ã© o pior. A diferenÃ§a entre eles Ã© de 0,05 acerto em 3724 tentativas â€” estatisticamente irrelevante perto da variÃ¢ncia natural do sorteio. Nenhum desses nÃºmeros diz nada sobre o concurso 3726 ou qualquer concurso futuro.

**4. Risco de confundir padrÃ£o histÃ³rico com previsÃ£o**
Esse Ã© o ponto mais importante do laboratÃ³rio inteiro: mesmo depois de simular quase 4 mil concursos reais, nenhum dos 5 mÃ©todos "venceu" de forma consistente. Se alguÃ©m parasse de olhar no meio da sÃ©rie (por exemplo, sÃ³ nos primeiros 200 concursos), poderia ver um mÃ©todo na frente e concluir, erroneamente, que "funciona". A amostra completa mostra que essa vantagem teria sido sÃ³ sorte de curto prazo, dissolvida no longo prazo.

**5. ConclusÃ£o educativa**
Esta Ã© a demonstraÃ§Ã£o mais completa possÃ­vel com os dados disponÃ­veis: usar frequÃªncia histÃ³rica, atraso, paridade ou soma para montar um jogo nÃ£o muda a mÃ©dia de acertos esperada. A LotofÃ¡cil se comportou, nesses 3724 concursos, exatamente como um sorteio aleatÃ³rio sem memÃ³ria deveria se comportar. Os arquivos `dados/simulacao_metodos.csv` (linha a linha) e `dados/estatisticas_simulacao.csv` (agregado) ficam disponÃ­veis para quem quiser conferir os nÃºmeros por conta prÃ³pria.

---

## 04/07/2026 â€” Apostas estendidas: por que "mirar em 11" tem preÃ§o, nÃ£o truque

**1. O que foi observado**
A partir de uma dÃºvida legÃ­tima ("dÃ¡ pra garantir uma mÃ©dia de acertos maior, tipo cobrir os dois lados numa moeda?"), calculamos a matemÃ¡tica das apostas estendidas da LotofÃ¡cil (de 16 a 20 dezenas por bilhete, em vez de 15). Resultado: a mÃ©dia esperada de acertos sobe de fato â€” 9,0 (15 dezenas) atÃ© 12,0 (20 dezenas) â€” mas o custo sobe pela mesma combinatÃ³ria, de R$ 3,50 atÃ© R$ 54.264,00 por jogo. A chance de bater 11+ vai de 10,6% para 94,3%, sÃ³ que o custo para "comprar" cada ponto percentual dessa chance cresce de R$ 0,33 para R$ 575,15 â€” ou seja, a eficiÃªncia do dinheiro piora conforme se tenta cobrir mais dezenas.

**2. O que isso pode significar estatisticamente**
Isso confirma, com nÃºmeros concretos, algo que jÃ¡ era esperado pela teoria: apostar em mais combinaÃ§Ãµes ao mesmo tempo aumenta a chance bruta de acerto, mas nÃ£o cria retorno esperado extra por real investido â€” porque o preÃ§o da aposta estendida Ã© definido exatamente pelo nÃºmero de combinaÃ§Ãµes de 15 que ela contÃ©m (C(n,15)). Ã‰ a mesma lÃ³gica de comprar vÃ¡rios bilhetes simples ao mesmo tempo, sÃ³ que embutida em um Ãºnico bilhete maior.

**3. O que isso nÃ£o significa**
NÃ£o significa que existe uma forma de "prever" 9, 11 ou qualquer quantidade fixa de dezenas certas antes do sorteio. A ideia de "cobrir os dois lados como numa moeda" nÃ£o se aplica aqui: apostar nos dois resultados de uma moeda nÃ£o gera lucro, sÃ³ devolve o valor apostado (menos taxas) â€” e fixar parte das dezenas de um jogo como "certas" tambÃ©m nÃ£o funciona, porque nenhuma dezena escolhida tem prioridade sobre outra no sorteio real.

**4. Risco de confundir padrÃ£o histÃ³rico com previsÃ£o**
O risco aqui Ã© sutil: ver a mÃ©dia subir de 9,0 para 12,0 pode parecer uma "vitÃ³ria" da estratÃ©gia, mas essa subida nÃ£o vem de nenhuma informaÃ§Ã£o sobre o sorteio â€” vem simplesmente de pagar por milhares de combinaÃ§Ãµes simultÃ¢neas. Comparar apostas de tamanhos diferentes pela mÃ©dia de acertos, sem considerar o custo, Ã© uma forma de viÃ©s de confirmaÃ§Ã£o: olha-se para o nÃºmero que confirma a ideia (mais acertos) e ignora-se o nÃºmero que a desmente (o custo por real investido nÃ£o melhorou nem um pouco).

**5. ConclusÃ£o educativa**
A tabela de apostas estendidas (16 a 20 dezenas) foi incorporada ao relatÃ³rio e ao painel do laboratÃ³rio como um novo estudo permanente. Ela mostra, com matemÃ¡tica simples de combinatÃ³ria, por que nÃ£o existe atalho estatÃ­stico para aumentar a mÃ©dia de acertos "de graÃ§a": todo ganho de cobertura tem um custo proporcional (e, neste caso, um custo por ponto percentual que piora conforme a aposta cresce). Continua nÃ£o sendo recomendaÃ§Ã£o de aposta â€” Ã© sÃ³ a aritmÃ©tica por trÃ¡s da regra do jogo, deixada explÃ­cita.

| Dezenas na aposta | CombinaÃ§Ãµes (C(n,15)) | Custo (R$) | MÃ©dia esperada de acertos | % chance 11+ | Custo por ponto % de chance de 11+ |
|---|---|---|---|---|---|
| 15 | 1 | 3,50 | 9,00 | 10,59% | 0,33 |
| 16 | 16 | 56,00 | 9,60 | 22,16% | 2,53 |
| 17 | 136 | 476,00 | 10,20 | 39,31% | 12,11 |
| 18 | 816 | 2.856,00 | 10,80 | 60,14% | 47,49 |
| 19 | 3.876 | 13.566,00 | 11,40 | 80,22% | 169,12 |
| 20 | 15.504 | 54.264,00 | 12,00 | 94,35% | 575,15 |

---

## 04/07/2026 â€” SequÃªncia e salto das trincas de dezenas consecutivas

**1. O que foi observado**
Calculamos, para cada trinca de 3 dezenas consecutivas (01-02-03 atÃ© 23-24-25), duas contagens no histÃ³rico de 3.726 concursos: "sequÃªncia" (quantas vezes as 3 saÃ­ram juntas no mesmo sorteio) e "salto" (quantas vezes nenhuma das 3 saiu). Os valores observados variam de 17,53% a 21,28% para sequÃªncia (mÃ©dia 19,56%, desvio 1,04 p.p.) e de 4,24% a 5,82% para salto (mÃ©dia 5,25%, desvio 0,40 p.p.).

**2. O que isso pode significar estatisticamente**
Calculamos tambÃ©m o valor teÃ³rico exato (hipergeomÃ©trico) que qualquer trinca especÃ­fica de 3 dezenas deveria ter: 19,7826% de chance de sair inteira e 5,2174% de chance de nenhuma sair. As mÃ©dias observadas praticamente coincidem com isso, e a dispersÃ£o entre trincas Ã© do tamanho esperado para ruÃ­do amostral em 3.726 sorteios â€” nenhuma trinca foge do previsto pela matemÃ¡tica.

**3. O que isso nÃ£o significa**
A trinca 10,11,12 (21,28%, a mais alta) nÃ£o Ã© uma trinca "quente", e a trinca 15,16,17 (17,53%, a mais baixa) nÃ£o estÃ¡ "atrasada". Toda trinca de 3 dezenas consecutivas tem exatamente a mesma probabilidade teÃ³rica â€” a diferenÃ§a entre elas na tabela Ã© sÃ³ flutuaÃ§Ã£o normal de amostra.

**4. Risco de confundir padrÃ£o histÃ³rico com previsÃ£o**
Esse Ã© um exemplo clÃ¡ssico de viÃ©s de confirmaÃ§Ã£o: tabelas assim circulam por aÃ­ sem a linha teÃ³rica ao lado, o que convida a interpretar a variaÃ§Ã£o como sinal de trinca melhor ou pior. Ao colocar o valor teÃ³rico fixo ao lado de cada linha, a tabela vira uma demonstraÃ§Ã£o de ruÃ­do, nÃ£o uma sugestÃ£o de escolha.

**5. ConclusÃ£o educativa**
Tabela adicionada ao relatÃ³rio e ao painel (`scripts/tabela_sequencias.py`, dados em `dados/sequencias_saltos.csv`), sempre ao lado do valor teÃ³rico de referÃªncia. ReforÃ§a o padrÃ£o do laboratÃ³rio: qualquer estatÃ­stica de frequÃªncia, por mais que varie entre categorias, tende ao mesmo valor teÃ³rico fixo â€” a variaÃ§Ã£o Ã© o objeto de estudo, nÃ£o um indicador de escolha.

---

## 04/07/2026 â€” Desdobramento, filtros compostos e backtest de combinaÃ§Ãµes fixas

**1. O que foi observado**
Adicionamos ao `lotofacil_lib.py` funÃ§Ãµes de desdobramento (gerar todas as combinaÃ§Ãµes de 15 dentro de uma base maior, a mesma matemÃ¡tica das apostas estendidas) e um pipeline de filtros compostos (par/Ã­mpar, soma, sequÃªncia, linha vazia â€” os mesmos 4 filtros jÃ¡ estudados). A partir disso, geramos 5 combinaÃ§Ãµes de exemplo que passam pelos 4 filtros e testamos cada uma, fixa, contra os 3.726 concursos reais do histÃ³rico inteiro. Resultado: mÃ©dias entre 8,95 e 9,03 acertos (todas a menos de 0,05 da esperanÃ§a teÃ³rica de 9,0), desvio padrÃ£o entre 1,20 e 1,24, mÃ¡ximo observado de 13-14 acertos, e zero ocorrÃªncias de 15 acertos em qualquer exemplo.

**2. O que isso pode significar estatisticamente**
Isso Ã© uma confirmaÃ§Ã£o adicional, agora com combinaÃ§Ãµes fixas e reais (nÃ£o simuladas por concurso): mesmo escolhendo dezenas que atendem a critÃ©rios "bem-comportados" (soma central, paridade equilibrada, sem sequÃªncia longa, distribuiÃ§Ã£o por linha), o resultado ao longo de milhares de sorteios reais converge para a mesma esperanÃ§a teÃ³rica de qualquer combinaÃ§Ã£o aleatÃ³ria.

**3. O que isso nÃ£o significa**
NÃ£o significa que essas 5 combinaÃ§Ãµes sÃ£o recomendadas, nem que qualquer uma delas teria sido "melhor" de se jogar historicamente â€” a diferenÃ§a entre a de maior mÃ©dia (9,033) e a de menor (8,954) Ã© ruÃ­do estatÃ­stico, do mesmo tamanho que jÃ¡ vimos entre os mÃ©todos M1-M5. Nenhuma delas Ã© sugestÃ£o de aposta.

**4. Risco de confundir padrÃ£o histÃ³rico com previsÃ£o**
Poderia parecer tentador escolher, entre os exemplos, o que teve a maior mÃ©dia histÃ³rica (exemplo 4, 9,033) e tratÃ¡-lo como "o exemplo bom". Isso seria o mesmo erro de sempre: escolher depois de ver o resultado (viÃ©s de retrospectiva) nÃ£o muda a probabilidade da prÃ³xima vez â€” o exemplo 4 tem exatamente a mesma esperanÃ§a teÃ³rica de 9,0 para o concurso 3727 que qualquer um dos outros quatro.

**5. ConclusÃ£o educativa**
As novas funÃ§Ãµes (`desdobramento_total`, `aplicar_filtros_combinatorios`, `gerar_exemplos_filtrados`, `backtest_combinacoes_fixas`) ficam disponÃ­veis para gerar mais exemplos ilustrativos no futuro, sempre acompanhados do backtest completo contra o histÃ³rico real. Dados salvos em `dados/exemplos_filtrados_backtest.csv`. O padrÃ£o se mantÃ©m: qualquer forma de escolher 15 dezenas, filtrada ou nÃ£o, tem a mesma esperanÃ§a matemÃ¡tica â€” o valor do estudo estÃ¡ em demonstrar isso repetidamente com mÃ©todos diferentes, nÃ£o em encontrar uma exceÃ§Ã£o.

| Exemplo | Dezenas | MÃ©dia | Dif. vs. esperanÃ§a | MÃ¡x. observado | 11+ | 13+ |
|---|---|---|---|---|---|---|
| 1 | 01-02-03-04-06-07-08-14-16-18-19-20-21-23-25 | 8,9656 | -0,0344 | 13 | 9,47% | 0,08% |
| 2 | 01-02-05-07-08-09-10-11-16-18-19-20-22-23-24 | 8,9909 | -0,0091 | 13 | 10,52% | 0,11% |
| 3 | 01-02-04-06-08-09-11-13-14-15-17-18-21-22-24 | 8,9828 | -0,0172 | 13 | 10,39% | 0,21% |
| 4 | 02-03-04-06-08-11-13-14-15-17-19-20-22-24-25 | 9,0330 | +0,0330 | 13 | 11,65% | 0,19% |
| 5 | 03-04-05-06-08-09-12-14-15-16-17-21-22-24-25 | 8,9538 | -0,0462 | 14 | 10,23% | 0,13% |

---

## 05/07/2026

**1. O que foi observado**

- Concurso 3727: registrado e conferido contra os jogos de estudo â€” M1_aleatorio_puro: 9 acerto(s), M2_mais_frequentes: 10 acerto(s), M3_mais_atrasadas: 11 acerto(s), M4_par_impar_balanceado: 8 acerto(s), M5_soma_faixa_comum: 9 acerto(s).

**2. O que isso pode significar estatisticamente**

A mÃ©dia de acertos dos jogos de estudo hoje foi 9.40, contra a esperanÃ§a teÃ³rica de 9.0 por jogo (distribuiÃ§Ã£o hipergeomÃ©trica). DiferenÃ§as pontuais como essa sÃ£o esperadas em qualquer sorteio aleatÃ³rio e tendem a se equilibrar conforme mais concursos entram na sÃ©rie.

**3. O que isso nÃ£o significa**

NÃ£o significa que algum mÃ©todo estÃ¡ "mais perto" de 14 ou 15 acertos, nem que a frequÃªncia ou o atraso de uma dezena influenciam o prÃ³ximo sorteio. Cada concurso da LotofÃ¡cil Ã© independente dos anteriores â€” a bola nÃ£o tem memÃ³ria.

**4. Risco de confundir padrÃ£o histÃ³rico com previsÃ£o**

Observar uma sequÃªncia de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um mÃ©todo estÃ¡ funcionando, mas Ã© o tipo de variaÃ§Ã£o que o acaso produz sozinho em amostras pequenas. Tratar isso como previsÃ£o Ã© viÃ©s de confirmaÃ§Ã£o â€” e Ã© exatamente o que este laboratÃ³rio existe para demonstrar, nÃ£o para praticar.

**5. ConclusÃ£o educativa**

O histÃ³rico real agora tem 3727 concurso(s). Quanto mais dados entram, mais estÃ¡vel fica a comparaÃ§Ã£o entre os mÃ©todos e mais claro fica que todos oscilam ao redor do mesmo valor esperado â€” esse Ã© o ponto central do laboratÃ³rio: mostrar a matemÃ¡tica do acaso, nÃ£o encontrar um mÃ©todo vencedor.

*Jogos fictÃ­cios gerados para o concurso 3728 (estudo estatÃ­stico â€” nÃ£o Ã© recomendaÃ§Ã£o de aposta):*

| MÃ©todo | Dezenas |
|---|---|
| M1_aleatorio_puro | 03-05-06-07-09-11-12-13-14-16-17-18-20-23-24 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 02-03-06-07-08-10-12-14-15-17-20-21-23-24-25 |
| M4_par_impar_balanceado | 01-02-03-06-08-09-11-12-14-15-16-18-19-20-21 |
| M5_soma_faixa_comum | 01-02-05-06-09-12-13-14-15-16-19-20-21-23-25 |


---

## 05/07/2026

Nenhum concurso novo encontrado nesta execuÃ§Ã£o (pode ser dia sem sorteio da LotofÃ¡cil, ou a fonte de dados ainda nÃ£o publicou o resultado). Nenhuma alteraÃ§Ã£o feita â€” a tarefa tenta de novo na prÃ³xima execuÃ§Ã£o.


---

## 05/07/2026

Nenhum concurso novo encontrado nesta execuÃ§Ã£o (pode ser dia sem sorteio da LotofÃ¡cil, ou a fonte de dados ainda nÃ£o publicou o resultado). Nenhuma alteraÃ§Ã£o feita â€” a tarefa tenta de novo na prÃ³xima execuÃ§Ã£o.

## 05/07/2026 - Backtest completo M1-M8

O backtest completo foi executado com 3.726 concursos avaliados e 149.040 jogos simulados, usando 5 jogos por mÃ©todo em cada concurso. A simulaÃ§Ã£o respeitou a regra de usar apenas o histÃ³rico disponÃ­vel atÃ© o concurso anterior.

Resultado agregado: todos os mÃ©todos continuaram prÃ³ximos da esperanÃ§a teÃ³rica de 9 acertos por jogo. Entre os percentuais de 11+ acertos, M2 ficou com 11,331%, M6 com 10,902%, M3 com 10,832%, M4 com 10,617%, M7 com 10,601%, M1 com 10,510%, M5 com 10,494% e M8 com 10,134%. Nenhum mÃ©todo registrou 15 acertos no backtest.

Arquivos atualizados: `dados/simulacao_metodos.csv`, `dados/estatisticas_simulacao.csv`, `reports/relatorio_estatistico.md`, `dados/banco_projeto.json` e painÃ©is gerados.

---

## 06/07/2026

Nenhum concurso novo encontrado nesta execuÃ§Ã£o (pode ser dia sem sorteio da LotofÃ¡cil, ou a fonte de dados ainda nÃ£o publicou o resultado). Nenhuma alteraÃ§Ã£o feita â€” a tarefa tenta de novo na prÃ³xima execuÃ§Ã£o.

---

## 06/07/2026 - ExecuÃ§Ã£o confirmada do backtest completo

O comando `python scripts/executar_backtest_completo.py` foi executado com sucesso. A rotina simulou 3.726 concursos e 149.040 jogos, cobrindo os 8 mÃ©todos oficiais (M1 a M8), com 5 jogos por mÃ©todo em cada concurso e sem usar o resultado do concurso atual na geraÃ§Ã£o.

Resumo do percentual de 11+ acertos: M2 11,331%, M6 10,902%, M3 10,832%, M4 10,617%, M7 10,601%, M1 10,510%, M5 10,494% e M8 10,134%. As mÃ©dias permaneceram prÃ³ximas de 9 acertos por jogo, reforÃ§ando a leitura estatÃ­stica do laboratÃ³rio.

Arquivos atualizados nesta execuÃ§Ã£o: `dados/simulacao_metodos.csv`, `dados/estatisticas_simulacao.csv`, `reports/relatorio_estatistico.md`, `dados/banco_projeto.json`, `painel.html`, `painel_jogos.html`, `painel_mobile.html` e `index.html`.

---

## 06/07/2026 - Backtest completo reexecutado e relatório com seção dedicada aos 8 métodos

O backtest completo (`python scripts/executar_backtest_completo.py`) foi reexecutado para confirmar os dados: 3.726 concursos simulados e 149.040 jogos avaliados (5 jogos por método, 8 métodos). Os resultados são determinísticos e coincidiram exatamente com a execução anterior, já que o histórico de concursos não mudou desde então.

Média de acertos por método (esperança teórica 9.0): M1 8.9966, M2 9.0388, M3 9.0158, M4 9.0005, M5 8.9946, M6 9.001, M7 8.9983, M8 8.9881. Percentual de 11+ acertos: M2 11,331%, M6 10,902%, M3 10,832%, M4 10,617%, M7 10,601%, M1 10,51%, M5 10,494% e M8 10,134%. Nenhum método passou de 14 acertos.

`reports/relatorio_estatistico.md` ganhou uma seção nova, "Backtest completo M1-M8 (retroativo contra todo o histórico)", com a tabela completa de `dados/estatisticas_simulacao.csv` (média, desvio padrão, diferença vs. esperança, % 11+/13+ e máximo observado por método) — antes o relatório só trazia a tabela pequena de jogos fictícios de estudo, que ainda não cobre M6-M8 com jogos reais conferidos.

---

## 06/07/2026 - Análise comparativa completa entre os 8 métodos (M1-M8)

Foi criado `reports/analise_comparativa_metodos.md` a partir dos dados reais de `dados/estatisticas_simulacao.csv` e `dados/simulacao_metodos.csv` (3.726 concursos, 149.040 jogos, 18.630 jogos por método). O documento traz rankings por média de acertos, por % de 11+ e 13+ acertos, análise de estabilidade (desvio padrão e amplitude), tabela comparativa completa e um recorte de desempenho nos últimos 100, 200 e 500 concursos.

Principais achados: M2_mais_frequentes lidera o ranking geral de média (9,0388) e de % 11+ (11,331%), e se mantém em 1º lugar em média nos três recortes recentes. M4_par_impar_balanceado e M6_filtros_combinados têm a menor amplitude (8, sem nenhum jogo de 14+ acertos); M7_cobertura_pares tem o menor desvio padrão isolado (1,2186). M5_soma_faixa_comum se destaca isoladamente em % de 13+ acertos (0,252%, mais que o dobro dos últimos colocados nessa métrica).

A maior diferença do backtest (M2 vs. M8, nos extremos do ranking geral) corresponde a z≈4,0 na média e z≈3,7 no % de 11+ — perceptível dentro deste recorte de 3.726 concursos, mas sem qualquer valor preditivo: a esperança teórica de 9,0 acertos é idêntica para qualquer conjunto de 15 dezenas, já que cada sorteio da Lotofácil é independente dos anteriores. Conclusão do documento: nenhum método deve ser priorizado ou descartado com base nesses dados.

---

## 06/07/2026 - Fase 3: organização de estrutura do projeto

Foram criadas as pastas `analises/`, `graficos/`, `backups/` e `docs/` (adicionadas ao `.assetsignore` para não serem servidas pelo site publicado), e movidos 3 arquivos órfãos sem nenhuma referência em código: `LEIA-ME.md` → `docs/`, `painel_jogos nv.html` → `backups/`, `Melhorias design página loto.zip` → `docs/`. O `README.md` foi atualizado para refletir os 8 métodos e os números reais do backtest completo. `dados/`, `scripts/`, `reports/` e os `painel*.html`/`index.html` na raiz não foram tocados, pois são referenciados diretamente pelo workflow diário e pelo Cloudflare Workers (site publicado).
---

## 06/07/2026 - Fase 4: gerador de jogos ponderado pelo backtest (meta-método)

Criado `scripts/gerar_jogos_inteligente.py`, um meta-método que decide quais métodos usar e quantos jogos por método a partir dos dados reais do backtest (`dados/estatisticas_simulacao.csv` para a janela geral, ou `dados/simulacao_metodos.csv` recalculado ao vivo para janelas de 100/200/500 concursos — mesma lógica usada em `reports/analise_comparativa_metodos.md`). Não reimplementa a geração de dezenas: reaproveita `lib.gerar_todos_metodos()` e `gerar_jogos_avancados()`, os mesmos usados por `scripts/gerar_jogos.py`.

Três modos: `todos` (1 jogo por método, comportamento atual), `ponderado` (distribui N jogos proporcionalmente ao % de 11+, % de 13+ ou estabilidade de cada método) e `top` (usa só os 3-4 métodos com melhor indicador na janela escolhida). Grava em `dados/jogos_inteligente.csv` (arquivo próprio, não interfere na conferência diária de produção nem nas estatísticas oficiais dos 8 métodos). Testado nos três modos com dados reais.

Como os 8 métodos ficam muito próximos entre si no backtest completo (diferença máxima de ~1,2 ponto percentual em % de 11+), a ponderação por peso no modo `geral` resulta em pesos quase uniformes (~0,12-0,13 cada) — o próprio script imprime um aviso de que isso reflete só o encaixe histórico com o backtest já sorteado, não uma garantia de desempenho futuro, consistente com a conclusão de `analise_comparativa_metodos.md`.

Investigada também a funcionalidade "Meus Jogos" (item 2 da Fase 4): já está implementada de ponta a ponta em `painel_jogos_v2.html` + `/api/jogos` (`worker.js`) + banco D1, já registrando `concurso` e `metodo` por jogo salvo. Nenhuma alteração foi necessária ali por enquanto.

---

## 06/07/2026 - Evolução do meta-método (gerar_jogos_inteligente.py)

Adicionado o modo `hibrido` (top 3 métodos da janela por peso principal + 2 métodos sorteados por diversidade, com seed reprodutível por concurso) e o atalho `--janela=recent` (últimos 100 concursos, automático). A saída ficou mais clara: ranking numerado dos métodos considerados com `score` (valor bruto do critério) e peso, aviso de qual janela foi usada e por quê, e um resumo final com melhor/pior método e a distribuição de jogos usada. O CSV `dados/jogos_inteligente.csv` ganhou a coluna `score`. Adicionada validação: no modo `top`, `--total` acima de `n × 5` é avisado e limitado automaticamente (evita pedir mais jogos do que os métodos conseguem variar, especialmente os determinísticos M2/M3). Compatibilidade mantida com os modos `todos`, `ponderado` e `top` já existentes — todos testados de novo com dados reais.
---

## 06/07/2026 - Fechamento combinatório trocado por matrizes de cobertura reduzidas

O fechamento (16 a 20 dezenas) do painel usava `itertools.combinations`-equivalente em JS para calcular a combinação total (16 a 15.504 jogos, guardando garantia de 15 pontos), o que era inviável de exibir/gerenciar acima de 16 dezenas. Criado `scripts/gerar_matrizes_cobertura.py`, que calcula e verifica por força bruta (contra todos os C(v,15) sorteios hipotéticos possíveis) uma matriz de cobertura reduzida por tamanho de grupo, trocando a garantia de 15 para 14 pontos: v=16 → 1 jogo (vs. 16), v=17 → 8 (vs. 136), v=18 → 24 (vs. 816), v=19 → 144 (vs. 3.876), v=20 → 481 (vs. 15.504) — reduções de 93,8% a 97,1%. Resultado salvo em `dados/matrizes_cobertura.json` e embutido em `painel_jogos_v2.html`, que agora consulta essa matriz fixa (mapeando posições para as dezenas escolhidas pelo usuário) em vez de calcular a combinação total. O custo exibido no painel passou a refletir o fechamento reduzido (jogos × R$3,50), não mais a aposta estendida. O antigo fallback de "5 opções sem garantia" para grupos acima de 16 foi removido, pois agora todos os tamanhos (16 a 20) têm garantia real e verificada.

---

## 06/07/2026 - Fase 3: aprendizado por origem no painel

Implementado o aprendizado por origem a partir do histórico real de conferências salvas no banco D1. O `worker.js` passou a calcular ranking por origem usando janela dos últimos 60 concursos, ponderação temporal para dar mais peso às conferências recentes, penalização de origens com média baixa, pouca frequência de 11+ ou amostra insuficiente, além de tendência, confiança e peso por origem.

O painel ganhou a seção "Aprendizado do sistema", exibindo perfil mais estável, melhor média recente, origem sugerida para priorizar, origem com peso reduzido, tendência, confiança e peso da IA. A geração por IA passou a usar esses pesos do aprendizado como freio e acelerador: perfis com melhor comportamento recente recebem bônus, enquanto perfis penalizados têm menor influência. A leitura continua estatística e educacional, sem tratar o histórico como garantia de acerto futuro.

---

## 06/07/2026 - Fase 4: combinação inteligente de perfis

Criada no `worker.js` a função `calcularCombinacaoRecomendada`, responsável por sugerir uma carteira prática de jogos para o próximo sorteio. A combinação usa até 5 origens, limita concentração em um único método e considera pesos, tendência, estabilidade, confiança e penalizações calculadas pelo aprendizado por origem.

O painel passou a exibir a seção "Combinação recomendada para o próximo sorteio", mostrando quantidade sugerida por origem e justificativa curta de cada escolha. Também foi adicionado o botão "Gerar jogos desta combinação", que monta os jogos conforme a carteira recomendada e salva automaticamente em "Jogos registrados" com origem `Combo Inteligente - ...`, mantendo o fluxo de conferência automática das fases anteriores.

---

## 07/07/2026

**1. O que foi observado**

- Concurso 3728: registrado e conferido contra os jogos de estudo — M1_aleatorio_puro: 7 acerto(s), M2_mais_frequentes: 7 acerto(s), M3_mais_atrasadas: 10 acerto(s), M4_par_impar_balanceado: 9 acerto(s), M5_soma_faixa_comum: 8 acerto(s), M6_filtros_combinados: 9 acerto(s), M7_cobertura_pares: 8 acerto(s), M8_repeticao_controlada: 11 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 7 acerto(s), M6_filtros_combinados: 8 acerto(s), M6_filtros_combinados: 8 acerto(s), M6_filtros_combinados: 11 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 11 acerto(s), M7_cobertura_pares: 10 acerto(s), M7_cobertura_pares: 7 acerto(s), M7_cobertura_pares: 7 acerto(s), M8_repeticao_controlada: 9 acerto(s), M8_repeticao_controlada: 9 acerto(s), M8_repeticao_controlada: 9 acerto(s), M8_repeticao_controlada: 8 acerto(s), M8_repeticao_controlada: 6 acerto(s).

**2. O que isso pode significar estatisticamente**

A média de acertos dos jogos de estudo hoje foi 8.61, contra a esperança teórica de 9.0 por jogo (distribuição hipergeométrica). Diferenças pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar conforme mais concursos entram na série.

**3. O que isso não significa**

Não significa que algum método está "mais perto" de 14 ou 15 acertos, nem que a frequência ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é independente dos anteriores — a bola não tem memória.

**4. Risco de confundir padrão histórico com previsão**

Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que este laboratório existe para demonstrar, não para praticar.

**5. Conclusão educativa**

O histórico real agora tem 3728 concurso(s). Quanto mais dados entram, mais estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do acaso, não encontrar um método vencedor.

*Jogos fictícios gerados para o concurso 3729 (estudo estatístico — não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 01-02-03-08-10-12-13-15-16-17-18-19-21-22-24 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 04-05-08-09-12-13-14-15-18-19-20-21-22-23-24 |
| M4_par_impar_balanceado | 02-03-04-07-09-10-11-13-14-15-16-18-19-20-24 |
| M5_soma_faixa_comum | 01-03-04-06-09-11-12-13-14-16-19-20-22-23-24 |
| M6_filtros_combinados | 02-03-04-08-10-11-12-15-16-17-18-19-21-22-23 |
| M6_filtros_combinados | 01-02-04-06-07-10-14-16-17-18-19-20-21-22-25 |
| M6_filtros_combinados | 02-03-04-06-07-10-11-13-16-17-20-21-23-24-25 |
| M6_filtros_combinados | 02-03-05-06-09-10-11-12-16-17-19-20-21-22-25 |
| M6_filtros_combinados | 01-04-06-07-08-10-11-12-17-18-19-20-21-23-25 |
| M7_cobertura_pares | 01-02-06-07-09-10-11-14-16-17-19-20-21-23-24 |
| M7_cobertura_pares | 02-03-06-07-08-09-11-12-16-18-19-21-22-23-24 |
| M7_cobertura_pares | 02-03-05-07-08-10-11-13-16-18-19-20-21-22-23 |
| M7_cobertura_pares | 02-03-04-06-07-10-11-14-16-17-18-19-21-24-25 |
| M7_cobertura_pares | 02-03-05-07-08-10-11-12-13-18-19-21-22-24-25 |
| M8_repeticao_controlada | 01-03-04-07-08-10-11-12-16-17-19-20-23-24-25 |
| M8_repeticao_controlada | 02-03-06-07-08-10-12-13-14-17-19-20-22-23-25 |
| M8_repeticao_controlada | 01-02-03-06-10-11-12-15-16-17-19-20-22-23-24 |
| M8_repeticao_controlada | 01-03-05-06-07-08-10-12-16-18-19-22-23-24-25 |
| M8_repeticao_controlada | 02-03-04-06-07-08-10-11-18-19-20-21-22-23-24 |


---

## 08/07/2026

**1. O que foi observado**

- Concurso 3729: registrado e conferido contra os jogos de estudo — M1_aleatorio_puro: 10 acerto(s), M2_mais_frequentes: 11 acerto(s), M3_mais_atrasadas: 9 acerto(s), M4_par_impar_balanceado: 9 acerto(s), M5_soma_faixa_comum: 10 acerto(s), M6_filtros_combinados: 9 acerto(s), M6_filtros_combinados: 9 acerto(s), M6_filtros_combinados: 8 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 7 acerto(s), M7_cobertura_pares: 8 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 10 acerto(s), M7_cobertura_pares: 8 acerto(s), M7_cobertura_pares: 9 acerto(s), M8_repeticao_controlada: 6 acerto(s), M8_repeticao_controlada: 8 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 8 acerto(s), M8_repeticao_controlada: 8 acerto(s).

**2. O que isso pode significar estatisticamente**

A média de acertos dos jogos de estudo hoje foi 8.80, contra a esperança teórica de 9.0 por jogo (distribuição hipergeométrica). Diferenças pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar conforme mais concursos entram na série.

**3. O que isso não significa**

Não significa que algum método está "mais perto" de 14 ou 15 acertos, nem que a frequência ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é independente dos anteriores — a bola não tem memória.

**4. Risco de confundir padrão histórico com previsão**

Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que este laboratório existe para demonstrar, não para praticar.

**5. Conclusão educativa**

O histórico real agora tem 3729 concurso(s). Quanto mais dados entram, mais estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do acaso, não encontrar um método vencedor.

*Jogos fictícios gerados para o concurso 3730 (estudo estatístico — não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 02-04-05-06-08-09-10-11-12-13-15-16-17-18-23 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 04-07-08-09-10-11-13-14-16-17-19-20-23-24-25 |
| M4_par_impar_balanceado | 01-02-03-04-05-06-07-10-13-16-17-18-20-21-24 |
| M5_soma_faixa_comum | 01-02-04-05-07-11-13-14-16-17-19-20-21-23-25 |
| M6_filtros_combinados | 01-05-06-08-10-11-12-13-14-15-18-19-21-22-25 |
| M6_filtros_combinados | 01-03-05-06-10-12-13-15-16-17-18-19-20-22-23 |
| M6_filtros_combinados | 02-04-05-06-10-11-12-14-15-16-18-19-21-22-25 |
| M6_filtros_combinados | 02-03-04-06-11-12-13-14-15-17-18-19-20-21-24 |
| M6_filtros_combinados | 01-04-06-07-09-12-13-14-15-16-18-20-21-22-23 |
| M7_cobertura_pares | 02-04-05-06-10-11-12-14-15-16-19-20-21-22-23 |
| M7_cobertura_pares | 02-03-06-08-10-11-12-13-14-15-16-21-22-23-24 |
| M7_cobertura_pares | 01-02-05-06-07-10-11-12-15-18-20-21-22-24-25 |
| M7_cobertura_pares | 02-03-06-09-10-11-12-13-14-15-18-19-20-22-25 |
| M7_cobertura_pares | 01-03-06-09-10-11-12-13-14-16-18-19-20-22-25 |
| M8_repeticao_controlada | 01-02-04-05-09-11-12-15-16-18-19-20-21-22-25 |
| M8_repeticao_controlada | 02-03-05-09-10-11-13-14-16-17-18-19-20-21-22 |
| M8_repeticao_controlada | 01-02-04-10-11-12-13-14-15-16-18-19-20-21-24 |
| M8_repeticao_controlada | 02-04-05-06-08-11-12-13-14-16-18-20-21-23-25 |
| M8_repeticao_controlada | 01-03-05-08-10-11-12-15-16-17-18-20-21-22-24 |


---

## 09/07/2026

Nenhum concurso novo encontrado nesta execução (pode ser dia sem sorteio da Lotofácil, ou a fonte de dados ainda não publicou o resultado). Nenhuma alteração feita — a tarefa tenta de novo na próxima execução.


---

## 10/07/2026

**1. O que foi observado**

- Concurso 3730: registrado e conferido contra os jogos de estudo — M1_aleatorio_puro: 9 acerto(s), M2_mais_frequentes: 10 acerto(s), M3_mais_atrasadas: 8 acerto(s), M4_par_impar_balanceado: 9 acerto(s), M5_soma_faixa_comum: 9 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 9 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 12 acerto(s), M6_filtros_combinados: 8 acerto(s), M7_cobertura_pares: 11 acerto(s), M7_cobertura_pares: 12 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 10 acerto(s), M7_cobertura_pares: 9 acerto(s), M8_repeticao_controlada: 9 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 11 acerto(s), M8_repeticao_controlada: 11 acerto(s), M8_repeticao_controlada: 10 acerto(s).
- Concurso 3731: registrado no histórico (sem jogos de estudo com esse concurso como alvo).

**2. O que isso pode significar estatisticamente**

A média de acertos dos jogos de estudo hoje foi 9.80, contra a esperança teórica de 9.0 por jogo (distribuição hipergeométrica). Diferenças pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar conforme mais concursos entram na série.

**3. O que isso não significa**

Não significa que algum método está "mais perto" de 14 ou 15 acertos, nem que a frequência ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é independente dos anteriores — a bola não tem memória.

**4. Risco de confundir padrão histórico com previsão**

Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que este laboratório existe para demonstrar, não para praticar.

**5. Conclusão educativa**

O histórico real agora tem 3731 concurso(s). Quanto mais dados entram, mais estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do acaso, não encontrar um método vencedor.

*Jogos fictícios gerados para o concurso 3732 (estudo estatístico — não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 02-04-05-06-07-08-10-11-15-16-19-21-22-24-25 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 01-03-07-08-09-11-13-14-15-16-18-19-20-21-24 |
| M4_par_impar_balanceado | 02-03-04-05-06-08-10-13-14-17-18-19-22-23-25 |
| M5_soma_faixa_comum | 01-02-03-04-06-07-09-13-15-19-20-21-22-24-25 |
| M6_filtros_combinados | 02-04-05-06-07-08-12-14-16-17-19-20-22-23-25 |
| M6_filtros_combinados | 02-04-05-06-07-09-10-15-16-17-19-20-22-23-25 |
| M6_filtros_combinados | 01-04-05-06-08-10-11-12-16-18-19-20-22-23-25 |
| M6_filtros_combinados | 02-04-06-07-08-10-11-12-14-17-18-21-22-23-25 |
| M6_filtros_combinados | 01-02-04-06-07-09-10-12-16-19-21-22-23-24-25 |
| M7_cobertura_pares | 02-03-04-07-10-11-12-13-16-17-19-20-21-22-25 |
| M7_cobertura_pares | 01-04-06-07-10-11-12-14-16-17-18-20-21-22-23 |
| M7_cobertura_pares | 01-02-04-05-06-11-12-13-17-19-20-21-22-24-25 |
| M7_cobertura_pares | 01-02-07-08-10-11-12-13-15-16-17-21-22-23-24 |
| M7_cobertura_pares | 01-02-06-07-10-11-12-14-16-17-18-20-21-23-25 |
| M8_repeticao_controlada | 01-04-06-07-09-10-11-12-14-16-19-21-22-23-25 |
| M8_repeticao_controlada | 01-04-05-06-07-08-12-13-16-17-19-20-23-24-25 |
| M8_repeticao_controlada | 02-04-06-07-08-09-11-12-16-17-18-20-22-23-25 |
| M8_repeticao_controlada | 01-02-03-04-06-10-11-14-16-17-21-22-23-24-25 |
| M8_repeticao_controlada | 01-02-05-06-07-10-12-13-16-18-19-21-22-24-25 |


---

## 11/07/2026

**1. O que foi observado**

- Concurso 3732: registrado e conferido contra os jogos de estudo — M1_aleatorio_puro: 9 acerto(s), M2_mais_frequentes: 8 acerto(s), M3_mais_atrasadas: 10 acerto(s), M4_par_impar_balanceado: 10 acerto(s), M5_soma_faixa_comum: 9 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 9 acerto(s), M6_filtros_combinados: 9 acerto(s), M6_filtros_combinados: 9 acerto(s), M6_filtros_combinados: 8 acerto(s), M7_cobertura_pares: 11 acerto(s), M7_cobertura_pares: 8 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 10 acerto(s), M7_cobertura_pares: 9 acerto(s), M8_repeticao_controlada: 7 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 11 acerto(s), M8_repeticao_controlada: 9 acerto(s), M8_repeticao_controlada: 9 acerto(s).

**2. O que isso pode significar estatisticamente**

A média de acertos dos jogos de estudo hoje foi 9.20, contra a esperança teórica de 9.0 por jogo (distribuição hipergeométrica). Diferenças pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar conforme mais concursos entram na série.

**3. O que isso não significa**

Não significa que algum método está "mais perto" de 14 ou 15 acertos, nem que a frequência ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é independente dos anteriores — a bola não tem memória.

**4. Risco de confundir padrão histórico com previsão**

Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que este laboratório existe para demonstrar, não para praticar.

**5. Conclusão educativa**

O histórico real agora tem 3732 concurso(s). Quanto mais dados entram, mais estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do acaso, não encontrar um método vencedor.

*Jogos fictícios gerados para o concurso 3733 (estudo estatístico — não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 04-05-06-07-08-10-12-13-16-17-19-21-22-24-25 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 01-02-04-05-06-08-09-10-12-13-14-15-21-22-25 |
| M4_par_impar_balanceado | 01-02-04-06-08-12-13-14-15-17-20-21-22-23-25 |
| M5_soma_faixa_comum | 01-02-04-05-10-11-12-13-15-16-17-18-21-22-24 |
| M6_filtros_combinados | 03-05-06-07-08-10-11-12-13-16-18-20-22-24-25 |
| M6_filtros_combinados | 02-03-06-07-08-09-11-12-15-17-19-20-22-24-25 |
| M6_filtros_combinados | 03-04-07-08-09-11-12-13-14-16-17-18-19-24-25 |
| M6_filtros_combinados | 01-02-07-08-09-10-11-12-13-16-19-20-22-24-25 |
| M6_filtros_combinados | 01-02-03-04-08-13-14-15-16-17-18-19-22-24-25 |
| M7_cobertura_pares | 01-02-06-08-09-11-13-14-16-17-18-19-20-22-24 |
| M7_cobertura_pares | 02-03-04-05-08-11-12-13-17-18-19-20-21-22-25 |
| M7_cobertura_pares | 02-03-04-06-08-10-11-13-15-16-18-22-23-24-25 |
| M7_cobertura_pares | 01-02-05-07-08-11-12-13-14-16-19-20-23-24-25 |
| M7_cobertura_pares | 02-03-05-08-11-12-13-14-15-16-17-18-19-23-24 |
| M8_repeticao_controlada | 03-05-06-07-08-11-12-13-14-16-18-19-20-23-25 |
| M8_repeticao_controlada | 02-03-05-06-08-09-11-12-16-17-19-20-22-24-25 |
| M8_repeticao_controlada | 01-02-04-07-08-09-13-14-16-17-18-19-22-24-25 |
| M8_repeticao_controlada | 01-02-07-08-10-11-12-13-15-17-18-19-20-22-24 |
| M8_repeticao_controlada | 01-02-03-06-07-08-13-14-15-18-20-22-23-24-25 |


---

## 12/07/2026

**1. O que foi observado**

- Concurso 3733: registrado e conferido contra os jogos de estudo — M1_aleatorio_puro: 10 acerto(s), M2_mais_frequentes: 11 acerto(s), M3_mais_atrasadas: 9 acerto(s), M4_par_impar_balanceado: 8 acerto(s), M5_soma_faixa_comum: 10 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 9 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 11 acerto(s), M6_filtros_combinados: 10 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 10 acerto(s), M7_cobertura_pares: 8 acerto(s), M7_cobertura_pares: 11 acerto(s), M7_cobertura_pares: 10 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 8 acerto(s).

**2. O que isso pode significar estatisticamente**

A média de acertos dos jogos de estudo hoje foi 9.70, contra a esperança teórica de 9.0 por jogo (distribuição hipergeométrica). Diferenças pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar conforme mais concursos entram na série.

**3. O que isso não significa**

Não significa que algum método está "mais perto" de 14 ou 15 acertos, nem que a frequência ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é independente dos anteriores — a bola não tem memória.

**4. Risco de confundir padrão histórico com previsão**

Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que este laboratório existe para demonstrar, não para praticar.

**5. Conclusão educativa**

O histórico real agora tem 3733 concurso(s). Quanto mais dados entram, mais estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do acaso, não encontrar um método vencedor.

*Jogos fictícios gerados para o concurso 3734 (estudo estatístico — não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 01-02-03-04-06-07-08-13-14-19-20-21-23-24-25 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 02-04-06-07-08-09-12-13-15-18-20-21-23-24-25 |
| M4_par_impar_balanceado | 01-03-04-06-07-10-11-12-14-16-17-20-22-23-25 |
| M5_soma_faixa_comum | 01-04-06-07-08-09-10-11-13-18-20-22-23-24-25 |
| M6_filtros_combinados | 02-03-05-07-08-11-12-13-14-16-17-20-23-24-25 |
| M6_filtros_combinados | 02-03-04-07-08-10-11-14-16-17-19-20-21-22-25 |
| M6_filtros_combinados | 04-05-07-08-10-11-12-13-14-15-16-17-20-22-25 |
| M6_filtros_combinados | 02-05-06-08-10-11-12-13-14-15-17-19-20-22-25 |
| M6_filtros_combinados | 01-05-09-10-11-12-13-14-15-16-17-18-19-20-22 |
| M7_cobertura_pares | 03-04-05-06-07-10-12-13-16-17-19-20-21-22-25 |
| M7_cobertura_pares | 01-03-05-06-07-08-12-14-16-17-19-21-22-24-25 |
| M7_cobertura_pares | 01-05-06-07-08-11-12-13-14-16-17-20-22-23-25 |
| M7_cobertura_pares | 03-05-06-08-10-11-12-13-14-15-16-19-21-22-25 |
| M7_cobertura_pares | 03-05-07-08-09-10-12-13-14-16-17-18-20-22-25 |
| M8_repeticao_controlada | 01-02-03-08-11-12-13-14-15-16-18-19-20-22-25 |
| M8_repeticao_controlada | 01-02-04-07-09-10-12-13-14-16-17-22-23-24-25 |
| M8_repeticao_controlada | 02-04-06-07-08-10-11-13-14-16-17-19-22-24-25 |
| M8_repeticao_controlada | 02-03-04-07-08-11-12-13-16-17-18-19-21-22-25 |
| M8_repeticao_controlada | 02-03-04-05-06-10-12-14-16-17-19-20-22-23-25 |


---

## 13/07/2026

Nenhum concurso novo encontrado nesta execução (pode ser dia sem sorteio da Lotofácil, ou a fonte de dados ainda não publicou o resultado). Nenhuma alteração feita — a tarefa tenta de novo na próxima execução.


---

## 14/07/2026

**1. O que foi observado**

- Concurso 3734: registrado e conferido contra os jogos de estudo — M1_aleatorio_puro: 8 acerto(s), M2_mais_frequentes: 10 acerto(s), M3_mais_atrasadas: 7 acerto(s), M4_par_impar_balanceado: 9 acerto(s), M5_soma_faixa_comum: 6 acerto(s), M6_filtros_combinados: 11 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 11 acerto(s), M6_filtros_combinados: 12 acerto(s), M6_filtros_combinados: 10 acerto(s), M7_cobertura_pares: 10 acerto(s), M7_cobertura_pares: 10 acerto(s), M7_cobertura_pares: 10 acerto(s), M7_cobertura_pares: 12 acerto(s), M7_cobertura_pares: 11 acerto(s), M8_repeticao_controlada: 11 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 12 acerto(s).

**2. O que isso pode significar estatisticamente**

A média de acertos dos jogos de estudo hoje foi 10.00, contra a esperança teórica de 9.0 por jogo (distribuição hipergeométrica). Diferenças pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar conforme mais concursos entram na série.

**3. O que isso não significa**

Não significa que algum método está "mais perto" de 14 ou 15 acertos, nem que a frequência ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é independente dos anteriores — a bola não tem memória.

**4. Risco de confundir padrão histórico com previsão**

Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que este laboratório existe para demonstrar, não para praticar.

**5. Conclusão educativa**

O histórico real agora tem 3734 concurso(s). Quanto mais dados entram, mais estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do acaso, não encontrar um método vencedor.

*Jogos fictícios gerados para o concurso 3735 (estudo estatístico — não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 01-03-05-07-10-11-13-18-19-20-21-22-23-24-25 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 01-03-04-05-06-07-09-11-15-16-17-18-20-21-24 |
| M4_par_impar_balanceado | 02-05-06-08-12-13-14-17-18-19-20-21-22-23-25 |
| M5_soma_faixa_comum | 01-03-04-05-06-08-13-15-18-20-21-22-23-24-25 |
| M6_filtros_combinados | 02-03-05-06-07-08-13-14-16-17-19-21-22-23-24 |
| M6_filtros_combinados | 02-04-06-07-08-11-12-13-15-16-17-19-22-23-25 |
| M6_filtros_combinados | 02-03-04-05-07-10-12-13-14-16-20-22-23-24-25 |
| M6_filtros_combinados | 02-05-06-08-09-11-13-14-15-16-17-19-20-22-25 |
| M6_filtros_combinados | 04-05-06-07-09-10-12-13-14-16-17-19-22-23-25 |
| M7_cobertura_pares | 01-02-05-07-08-10-12-14-15-17-19-21-22-23-24 |
| M7_cobertura_pares | 01-02-04-05-10-11-12-14-16-17-19-20-22-23-25 |
| M7_cobertura_pares | 02-03-05-06-10-11-12-14-15-16-19-20-21-22-23 |
| M7_cobertura_pares | 02-03-04-05-06-08-12-15-16-17-19-21-22-24-25 |
| M7_cobertura_pares | 01-03-04-05-08-10-12-13-14-17-20-22-23-24-25 |
| M8_repeticao_controlada | 02-04-05-08-10-11-12-13-14-16-19-20-21-22-23 |
| M8_repeticao_controlada | 02-03-05-06-07-08-10-13-15-18-19-22-23-24-25 |
| M8_repeticao_controlada | 02-03-05-06-08-10-11-14-15-16-19-20-22-24-25 |
| M8_repeticao_controlada | 02-03-04-05-06-13-14-15-16-17-18-19-20-23-25 |
| M8_repeticao_controlada | 02-05-06-08-09-10-11-13-14-15-16-19-22-24-25 |


---

## 15/07/2026

**1. O que foi observado**

- Concurso 3735: registrado e conferido contra os jogos de estudo — M1_aleatorio_puro: 10 acerto(s), M2_mais_frequentes: 9 acerto(s), M3_mais_atrasadas: 10 acerto(s), M4_par_impar_balanceado: 10 acerto(s), M5_soma_faixa_comum: 10 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 8 acerto(s), M6_filtros_combinados: 11 acerto(s), M6_filtros_combinados: 8 acerto(s), M6_filtros_combinados: 9 acerto(s), M7_cobertura_pares: 10 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 10 acerto(s), M7_cobertura_pares: 10 acerto(s), M7_cobertura_pares: 10 acerto(s), M8_repeticao_controlada: 8 acerto(s), M8_repeticao_controlada: 9 acerto(s), M8_repeticao_controlada: 9 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 7 acerto(s).

**2. O que isso pode significar estatisticamente**

A média de acertos dos jogos de estudo hoje foi 9.35, contra a esperança teórica de 9.0 por jogo (distribuição hipergeométrica). Diferenças pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar conforme mais concursos entram na série.

**3. O que isso não significa**

Não significa que algum método está "mais perto" de 14 ou 15 acertos, nem que a frequência ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é independente dos anteriores — a bola não tem memória.

**4. Risco de confundir padrão histórico com previsão**

Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que este laboratório existe para demonstrar, não para praticar.

**5. Conclusão educativa**

O histórico real agora tem 3735 concurso(s). Quanto mais dados entram, mais estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do acaso, não encontrar um método vencedor.

*Jogos fictícios gerados para o concurso 3736 (estudo estatístico — não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 01-04-07-09-10-12-14-17-18-19-20-21-22-23-25 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 01-02-04-05-06-08-09-10-11-13-14-16-18-19-21 |
| M4_par_impar_balanceado | 01-04-06-07-08-09-10-12-14-15-18-19-21-22-23 |
| M5_soma_faixa_comum | 01-03-05-06-07-08-10-14-15-16-17-20-22-23-25 |
| M6_filtros_combinados | 01-04-05-06-07-08-12-14-16-17-18-21-22-24-25 |
| M6_filtros_combinados | 02-03-05-07-08-10-12-13-14-15-17-22-23-24-25 |
| M6_filtros_combinados | 01-02-03-05-08-12-13-14-15-16-18-21-22-24-25 |
| M6_filtros_combinados | 01-02-03-07-08-09-12-14-16-17-18-21-22-24-25 |
| M6_filtros_combinados | 03-04-05-07-08-10-12-14-16-17-18-19-20-21-25 |
| M7_cobertura_pares | 01-02-03-05-06-12-13-14-16-17-18-21-22-24-25 |
| M7_cobertura_pares | 03-04-05-06-07-10-13-15-16-17-18-20-21-22-24 |
| M7_cobertura_pares | 01-02-03-05-09-10-12-14-16-17-20-21-22-23-24 |
| M7_cobertura_pares | 03-05-06-07-09-11-12-13-15-16-18-20-21-22-24 |
| M7_cobertura_pares | 03-04-05-06-07-10-12-15-16-17-18-19-20-21-25 |
| M8_repeticao_controlada | 01-02-05-07-10-11-12-14-15-17-18-20-21-22-25 |
| M8_repeticao_controlada | 03-04-05-07-09-10-12-14-16-17-18-19-20-22-24 |
| M8_repeticao_controlada | 03-05-06-07-08-10-12-15-16-17-18-19-20-22-23 |
| M8_repeticao_controlada | 01-02-03-04-07-08-12-16-17-18-20-21-23-24-25 |
| M8_repeticao_controlada | 01-02-03-06-10-12-14-15-16-17-18-20-21-23-24 |


---

## 16/07/2026

**1. O que foi observado**

- Concurso 3736: registrado e conferido contra os jogos de estudo — M1_aleatorio_puro: 11 acerto(s), M2_mais_frequentes: 6 acerto(s), M3_mais_atrasadas: 9 acerto(s), M4_par_impar_balanceado: 12 acerto(s), M5_soma_faixa_comum: 8 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 8 acerto(s), M6_filtros_combinados: 7 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 10 acerto(s), M7_cobertura_pares: 8 acerto(s), M7_cobertura_pares: 8 acerto(s), M7_cobertura_pares: 8 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 9 acerto(s), M8_repeticao_controlada: 8 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 9 acerto(s), M8_repeticao_controlada: 8 acerto(s).

**2. O que isso pode significar estatisticamente**

A média de acertos dos jogos de estudo hoje foi 8.90, contra a esperança teórica de 9.0 por jogo (distribuição hipergeométrica). Diferenças pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar conforme mais concursos entram na série.

**3. O que isso não significa**

Não significa que algum método está "mais perto" de 14 ou 15 acertos, nem que a frequência ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é independente dos anteriores — a bola não tem memória.

**4. Risco de confundir padrão histórico com previsão**

Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que este laboratório existe para demonstrar, não para praticar.

**5. Conclusão educativa**

O histórico real agora tem 3736 concurso(s). Quanto mais dados entram, mais estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do acaso, não encontrar um método vencedor.

*Jogos fictícios gerados para o concurso 3737 (estudo estatístico — não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 03-04-07-08-09-11-12-13-16-17-18-22-23-24-25 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 01-02-05-06-10-11-12-13-15-16-20-22-23-24-25 |
| M4_par_impar_balanceado | 02-03-05-08-09-10-12-16-19-20-21-22-23-24-25 |
| M5_soma_faixa_comum | 01-02-05-07-08-09-10-12-16-17-18-19-21-23-25 |
| M6_filtros_combinados | 05-06-07-08-09-10-11-12-13-14-19-20-21-22-23 |
| M6_filtros_combinados | 01-06-07-08-09-11-12-13-14-15-17-18-22-23-24 |
| M6_filtros_combinados | 01-03-04-07-09-10-12-14-16-17-18-21-22-23-24 |
| M6_filtros_combinados | 01-03-06-07-08-11-12-14-15-17-18-20-22-23-24 |
| M6_filtros_combinados | 02-04-06-07-08-09-12-13-14-17-19-20-22-23-25 |
| M7_cobertura_pares | 02-03-04-06-07-08-14-15-16-17-18-21-22-23-24 |
| M7_cobertura_pares | 01-03-06-07-09-10-12-14-16-17-19-20-21-22-23 |
| M7_cobertura_pares | 01-03-06-08-09-10-11-12-14-18-19-20-21-23-25 |
| M7_cobertura_pares | 02-04-07-08-09-10-11-13-14-17-18-19-21-22-24 |
| M7_cobertura_pares | 02-03-06-08-09-10-11-12-13-18-19-21-22-23-24 |
| M8_repeticao_controlada | 02-04-06-08-09-11-12-13-16-17-18-19-20-22-23 |
| M8_repeticao_controlada | 03-04-07-08-09-10-12-14-15-16-17-18-19-23-25 |
| M8_repeticao_controlada | 03-05-06-07-08-11-12-14-15-17-18-19-20-21-24 |
| M8_repeticao_controlada | 03-06-08-09-10-11-12-13-14-15-16-18-21-22-23 |
| M8_repeticao_controlada | 02-05-06-07-08-11-12-14-15-17-18-19-21-22-24 |


---

## 17/07/2026

**1. O que foi observado**

- Concurso 3737: registrado e conferido contra os jogos de estudo — M1_aleatorio_puro: 10 acerto(s), M2_mais_frequentes: 10 acerto(s), M3_mais_atrasadas: 10 acerto(s), M4_par_impar_balanceado: 9 acerto(s), M5_soma_faixa_comum: 8 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 11 acerto(s), M6_filtros_combinados: 7 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 11 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 8 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 8 acerto(s), M7_cobertura_pares: 10 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 9 acerto(s), M8_repeticao_controlada: 9 acerto(s), M8_repeticao_controlada: 11 acerto(s), M8_repeticao_controlada: 10 acerto(s).

**2. O que isso pode significar estatisticamente**

A média de acertos dos jogos de estudo hoje foi 9.45, contra a esperança teórica de 9.0 por jogo (distribuição hipergeométrica). Diferenças pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar conforme mais concursos entram na série.

**3. O que isso não significa**

Não significa que algum método está "mais perto" de 14 ou 15 acertos, nem que a frequência ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é independente dos anteriores — a bola não tem memória.

**4. Risco de confundir padrão histórico com previsão**

Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que este laboratório existe para demonstrar, não para praticar.

**5. Conclusão educativa**

O histórico real agora tem 3737 concurso(s). Quanto mais dados entram, mais estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do acaso, não encontrar um método vencedor.

*Jogos fictícios gerados para o concurso 3738 (estudo estatístico — não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 04-06-07-08-10-12-13-14-16-18-19-20-22-23-25 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 01-04-05-06-07-10-12-13-16-18-19-20-21-23-24 |
| M4_par_impar_balanceado | 01-02-05-07-08-10-12-13-14-15-16-18-19-24-25 |
| M5_soma_faixa_comum | 01-02-04-05-06-11-12-13-15-16-18-20-21-22-24 |
| M6_filtros_combinados | 02-04-05-06-07-08-12-14-15-17-20-21-22-23-25 |
| M6_filtros_combinados | 01-02-03-06-10-11-12-13-14-15-18-22-23-24-25 |
| M6_filtros_combinados | 02-05-06-07-08-09-11-13-14-15-16-20-23-24-25 |
| M6_filtros_combinados | 02-04-06-08-09-11-12-13-14-16-17-18-21-22-25 |
| M6_filtros_combinados | 02-03-05-06-08-10-12-13-15-16-18-22-23-24-25 |
| M7_cobertura_pares | 03-04-06-07-08-09-11-12-15-17-18-20-22-23-25 |
| M7_cobertura_pares | 02-05-06-07-08-09-11-14-15-17-18-20-22-23-24 |
| M7_cobertura_pares | 02-03-06-08-09-10-11-14-15-16-17-21-22-23-24 |
| M7_cobertura_pares | 02-05-06-08-10-11-12-13-15-16-17-19-20-22-23 |
| M7_cobertura_pares | 02-05-06-07-09-10-11-13-14-15-16-22-23-24-25 |
| M8_repeticao_controlada | 02-03-04-05-06-08-12-14-17-18-20-21-22-23-25 |
| M8_repeticao_controlada | 03-04-06-08-09-10-12-13-14-15-17-19-22-24-25 |
| M8_repeticao_controlada | 02-03-05-08-09-10-12-13-15-16-17-20-22-23-24 |
| M8_repeticao_controlada | 02-03-05-08-09-10-11-12-15-16-17-19-22-24-25 |
| M8_repeticao_controlada | 03-04-05-06-08-09-10-12-14-15-18-22-23-24-25 |


---

## 18/07/2026

**1. O que foi observado**

- Concurso 3738: registrado e conferido contra os jogos de estudo — M1_aleatorio_puro: 9 acerto(s), M2_mais_frequentes: 10 acerto(s), M3_mais_atrasadas: 9 acerto(s), M4_par_impar_balanceado: 9 acerto(s), M5_soma_faixa_comum: 8 acerto(s), M6_filtros_combinados: 9 acerto(s), M6_filtros_combinados: 9 acerto(s), M6_filtros_combinados: 10 acerto(s), M6_filtros_combinados: 8 acerto(s), M6_filtros_combinados: 9 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 11 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 9 acerto(s), M7_cobertura_pares: 9 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 8 acerto(s), M8_repeticao_controlada: 10 acerto(s), M8_repeticao_controlada: 8 acerto(s), M8_repeticao_controlada: 9 acerto(s).

**2. O que isso pode significar estatisticamente**

A média de acertos dos jogos de estudo hoje foi 9.10, contra a esperança teórica de 9.0 por jogo (distribuição hipergeométrica). Diferenças pontuais como essa são esperadas em qualquer sorteio aleatório e tendem a se equilibrar conforme mais concursos entram na série.

**3. O que isso não significa**

Não significa que algum método está "mais perto" de 14 ou 15 acertos, nem que a frequência ou o atraso de uma dezena influenciam o próximo sorteio. Cada concurso da Lotofácil é independente dos anteriores — a bola não tem memória.

**4. Risco de confundir padrão histórico com previsão**

Observar uma sequência de acertos altos (ou baixos) em poucos concursos pode parecer um sinal de que um método está funcionando, mas é o tipo de variação que o acaso produz sozinho em amostras pequenas. Tratar isso como previsão é viés de confirmação — e é exatamente o que este laboratório existe para demonstrar, não para praticar.

**5. Conclusão educativa**

O histórico real agora tem 3738 concurso(s). Quanto mais dados entram, mais estável fica a comparação entre os métodos e mais claro fica que todos oscilam ao redor do mesmo valor esperado — esse é o ponto central do laboratório: mostrar a matemática do acaso, não encontrar um método vencedor.

*Jogos fictícios gerados para o concurso 3739 (estudo estatístico — não é recomendação de aposta):*

| Método | Dezenas |
|---|---|
| M1_aleatorio_puro | 01-03-04-07-09-11-13-14-15-16-17-18-20-21-22 |
| M2_mais_frequentes | 01-02-03-04-05-10-11-12-13-14-15-20-22-24-25 |
| M3_mais_atrasadas | 01-02-06-08-09-11-12-15-16-19-20-21-22-23-25 |
| M4_par_impar_balanceado | 01-02-06-07-08-09-10-11-13-14-16-17-18-19-22 |
| M5_soma_faixa_comum | 01-02-04-06-07-11-13-14-15-16-18-20-22-23-25 |
| M6_filtros_combinados | 01-02-03-04-05-10-13-14-17-18-19-22-23-24-25 |
| M6_filtros_combinados | 02-03-05-08-09-10-11-12-14-17-18-20-22-24-25 |
| M6_filtros_combinados | 02-03-04-08-10-11-12-13-16-17-18-20-21-22-23 |
| M6_filtros_combinados | 02-03-04-05-06-10-11-13-14-19-20-21-23-24-25 |
| M6_filtros_combinados | 02-03-05-07-09-10-12-14-16-17-18-19-20-23-24 |
| M7_cobertura_pares | 02-04-05-06-08-10-11-13-15-16-18-20-23-24-25 |
| M7_cobertura_pares | 03-04-05-08-10-12-13-14-15-16-17-18-20-22-23 |
| M7_cobertura_pares | 01-02-04-07-08-10-12-13-14-17-18-22-23-24-25 |
| M7_cobertura_pares | 02-03-05-07-08-10-13-14-15-16-18-20-21-23-25 |
| M7_cobertura_pares | 03-05-08-09-10-11-12-13-14-15-16-17-20-23-24 |
| M8_repeticao_controlada | 02-04-05-08-10-12-13-14-15-16-17-18-19-23-24 |
| M8_repeticao_controlada | 02-03-04-07-10-11-12-14-15-17-18-19-21-23-24 |
| M8_repeticao_controlada | 02-03-05-06-08-10-11-12-17-18-19-20-22-23-24 |
| M8_repeticao_controlada | 02-03-04-07-11-12-13-14-15-16-18-19-20-23-24 |
| M8_repeticao_controlada | 03-04-05-08-09-10-12-13-14-15-18-20-21-23-24 |

