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

