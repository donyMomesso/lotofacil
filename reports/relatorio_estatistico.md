# Relatório Estatístico Educativo — Lotofácil

_Atualizado em 07/07/2026 12:38 (horário de Brasília)_

Este relatório é gerado automaticamente a partir de resultados reais da Lotofácil. Serve para estudo estatístico. Não prevê resultados, não recomenda apostas e não indica que qualquer combinação está mais perto de dar 14 ou 15 pontos.

## Base analisada

- Total de concursos no histórico: 3727
- Concurso mais recente: 3727 (04/07/2026)
- Soma média das dezenas por concurso: 195.15
- Menor soma observada: 133
- Maior soma observada: 257
- Média de pares por concurso: 7.20 (de 15 dezenas)

## Último concurso

- Concurso: 3727
- Data: 04/07/2026
- Dezenas: 01-02-03-04-05-09-10-11-13-14-16-18-19-22-23
- Soma: 170
- Pares: 7 / Ímpares: 8

### Distribuição por linha (faixas de 5 dezenas)

- linha_01_05: 5
- linha_06_10: 2
- linha_11_15: 3
- linha_16_20: 3
- linha_21_25: 2

## Frequência das dezenas (histórico completo)

### Mais frequentes

- 20: 2331 vez(es) (62.5%)
- 10: 2323 vez(es) (62.3%)
- 25: 2316 vez(es) (62.1%)
- 11: 2289 vez(es) (61.4%)
- 13: 2268 vez(es) (60.9%)

### Menos frequentes

- 16: 2128 vez(es) (57.1%)
- 08: 2157 vez(es) (57.9%)
- 23: 2185 vez(es) (58.6%)
- 17: 2187 vez(es) (58.7%)
- 06: 2192 vez(es) (58.8%)

### Maior atraso atual (concursos sem sair)

- 12: 3 concurso(s)
- 15: 3 concurso(s)
- 08: 2 concurso(s)
- 06: 1 concurso(s)
- 07: 1 concurso(s)

## Desempenho comparado dos métodos (jogos fictícios de estudo)

Valor teórico esperado de acertos por jogo de 15 dezenas: **9.0** (distribuição hipergeométrica — todo método tende a esse valor no longo prazo).

| Método | Jogos conferidos | Média de acertos | Desvio padrão | % com 11+ | % com 13+ |
|---|---|---|---|---|---|
| M1_aleatorio_puro | 2 | 8 | 1.0 | 0.0% | 0.0% |
| M2_mais_frequentes | 2 | 9.5 | 0.5 | 0.0% | 0.0% |
| M3_mais_atrasadas | 2 | 9.5 | 1.5 | 50.0% | 0.0% |
| M4_par_impar_balanceado | 2 | 8 | 0.0 | 0.0% | 0.0% |
| M5_soma_faixa_comum | 2 | 9.5 | 0.5 | 0.0% | 0.0% |
| M6_filtros_combinados | 0 | 0.0 | 0.0 | 0.0% | 0.0% |
| M7_cobertura_pares | 0 | 0.0 | 0.0 | 0.0% | 0.0% |
| M8_repeticao_controlada | 0 | 0.0 | 0.0 | 0.0% | 0.0% |

## Backtest completo M1-M8 (retroativo contra todo o histórico)

Simulação retroativa cobrindo os 8 métodos oficiais, usando apenas o histórico disponível até o concurso anterior em cada rodada: **3726 concursos** simulados e **149040 jogos** avaliados (5 jogos por método em cada concurso).

| Método | Jogos simulados | Média de acertos | Desvio padrão | Dif. vs. esperança | % com 11+ | % com 13+ | Máx. observado |
|---|---|---|---|---|---|---|---|
| M1_aleatorio_puro | 18630 | 8.9966 | 1.2295 | -0.0034 | 10.51% | 0.14% | 14 |
| M2_mais_frequentes | 18630 | 9.0388 | 1.2243 | +0.0388 | 11.331% | 0.102% | 14 |
| M3_mais_atrasadas | 18630 | 9.0158 | 1.222 | +0.0158 | 10.832% | 0.097% | 14 |
| M4_par_impar_balanceado | 18630 | 9.0005 | 1.2231 | +0.0005 | 10.617% | 0.107% | 13 |
| M5_soma_faixa_comum | 18630 | 8.9946 | 1.2265 | -0.0054 | 10.494% | 0.252% | 14 |
| M6_filtros_combinados | 18630 | 9.001 | 1.234 | +0.0010 | 10.902% | 0.183% | 13 |
| M7_cobertura_pares | 18630 | 8.9983 | 1.2186 | -0.0017 | 10.601% | 0.14% | 14 |
| M8_repeticao_controlada | 18630 | 8.9881 | 1.2221 | -0.0119 | 10.134% | 0.172% | 14 |

Assim como nos jogos fictícios de estudo, todos os métodos — incluindo M6, M7 e M8 — ficam próximos da esperança teórica de 9.0 acertos por jogo no backtest completo. Nenhum método demonstrou vantagem estatística consistente sobre os demais.


## Apostas estendidas (16 a 20 dezenas): mais cobertura custa mais, na mesma proporção

A Lotofácil permite apostar com mais de 15 dezenas por bilhete (até 20). Isso realmente aumenta o número esperado de dezenas certas — mas o preço sobe pela mesma combinatória, porque uma aposta de `n` dezenas equivale a pagar por C(n,15) combinações de 15 ao mesmo tempo. Não há atalho: o retorno esperado por real investido não muda.

| Dezenas na aposta | Combinações (C(n,15)) | Custo (R$) | Média esperada de acertos | % chance 11+ | % chance 13+ | Custo por ponto % de chance de 11+ |
|---|---|---|---|---|---|---|
| 15 | 1 | R$ 3.50 | 9.0 | 10.5889% | 0.1492% | R$ 0.33 |
| 16 | 16 | R$ 56.00 | 9.6 | 22.1645% | 0.6503% | R$ 2.53 |
| 17 | 136 | R$ 476.00 | 10.2 | 39.3135% | 2.2093% | R$ 12.11 |
| 18 | 816 | R$ 2,856.00 | 10.8 | 60.1373% | 6.1847% | R$ 47.49 |
| 19 | 3,876 | R$ 13,566.00 | 11.4 | 80.2174% | 14.7036% | R$ 169.12 |
| 20 | 15,504 | R$ 54,264.00 | 12.0 | 94.3478% | 30.1186% | R$ 575.15 |

Repare na última coluna: o custo para ganhar cada ponto percentual de chance de 11+ não cresce de forma linear, cresce cada vez mais rápido (de R$ 0,33 na aposta simples para mais de R$ 575,00 na aposta de 20 dezenas). Ou seja, além de não haver vantagem de retorno esperado, a eficiência do dinheiro investido piora conforme se tenta cobrir mais dezenas. Isso não é uma recomendação de aposta — é a mesma matemática de sempre, só expressa em reais.


## Sequência e salto das dezenas (trincas consecutivas)

Para cada trinca de dezenas consecutivas (01-02-03 até 23-24-25), o valor teórico fixo é **19.7826%** de chance de as 3 saírem juntas ("sequência") e **5.2174%** de chance de nenhuma das 3 sair ("salto"). A tabela abaixo compara isso com o que aconteceu de fato no histórico — a variação entre trincas é ruído amostral, não indica trinca "quente" ou "atrasada".

| Trinca | Sequência (qtd) | Sequência (%) | Teórico seq. | Salto (qtd) | Salto (%) | Teórico salto |
|---|---|---|---|---|---|---|
| 01,02,03 | 741 | 19.89% | 19.7826% | 185 | 4.97% | 5.2174% |
| 02,03,04 | 751 | 20.16% | 19.7826% | 201 | 5.39% | 5.2174% |
| 03,04,05 | 743 | 19.94% | 19.7826% | 193 | 5.18% | 5.2174% |
| 04,05,06 | 727 | 19.51% | 19.7826% | 198 | 5.31% | 5.2174% |
| 05,06,07 | 688 | 18.46% | 19.7826% | 211 | 5.66% | 5.2174% |
| 06,07,08 | 672 | 18.04% | 19.7826% | 202 | 5.42% | 5.2174% |
| 07,08,09 | 688 | 18.46% | 19.7826% | 211 | 5.66% | 5.2174% |
| 08,09,10 | 752 | 20.18% | 19.7826% | 210 | 5.64% | 5.2174% |
| 09,10,11 | 790 | 21.2% | 19.7826% | 177 | 4.75% | 5.2174% |
| 10,11,12 | 793 | 21.28% | 19.7826% | 176 | 4.72% | 5.2174% |
| 11,12,13 | 746 | 20.02% | 19.7826% | 174 | 4.67% | 5.2174% |
| 12,13,14 | 729 | 19.57% | 19.7826% | 158 | 4.24% | 5.2174% |
| 13,14,15 | 737 | 19.78% | 19.7826% | 207 | 5.56% | 5.2174% |
| 14,15,16 | 713 | 19.14% | 19.7826% | 217 | 5.82% | 5.2174% |
| 15,16,17 | 653 | 17.53% | 19.7826% | 200 | 5.37% | 5.2174% |
| 16,17,18 | 655 | 17.58% | 19.7826% | 217 | 5.82% | 5.2174% |
| 17,18,19 | 723 | 19.4% | 19.7826% | 192 | 5.15% | 5.2174% |
| 18,19,20 | 767 | 20.59% | 19.7826% | 203 | 5.45% | 5.2174% |
| 19,20,21 | 770 | 20.67% | 19.7826% | 196 | 5.26% | 5.2174% |
| 20,21,22 | 734 | 19.7% | 19.7826% | 194 | 5.21% | 5.2174% |
| 21,22,23 | 694 | 18.63% | 19.7826% | 184 | 4.94% | 5.2174% |
| 22,23,24 | 716 | 19.22% | 19.7826% | 212 | 5.69% | 5.2174% |
| 23,24,25 | 778 | 20.88% | 19.7826% | 184 | 4.94% | 5.2174% |

Nenhuma trinca desta tabela está "mais perto" ou "mais longe" de sair — todas têm a mesma probabilidade teórica; o que varia é só o resultado observado em uma amostra finita de concursos.


## Exemplos filtrados: combinações fixas testadas contra todo o histórico

Cada linha abaixo é uma combinação fixa de 15 dezenas, gerada só como exemplo do espaço filtrado (par/ímpar 8/7, soma 180-210, sem sequência de 6+, no máximo 1 linha vazia). Cada uma foi conferida contra **todos** os concursos reais do histórico — não é jogo para apostar, é ilustração de que combinações "bem-comportadas" continuam com média de acertos igual à esperança teórica (9.0).

| Exemplo | Dezenas | Concursos testados | Média | Dif. vs. esperança | Máx. observado | 11+ | 13+ |
|---|---|---|---|---|---|---|---|
| 1 | 01-02-03-04-06-07-08-14-16-18-19-20-21-23-25 | 3726 | 8.9656 | -0.0344 | 13 | 9.474% | 0.0805% |
| 2 | 01-02-05-07-08-09-10-11-16-18-19-20-22-23-24 | 3726 | 8.9909 | -0.0091 | 13 | 10.5207% | 0.1074% |
| 3 | 01-02-04-06-08-09-11-13-14-15-17-18-21-22-24 | 3726 | 8.9828 | -0.0172 | 13 | 10.3865% | 0.2147% |
| 4 | 02-03-04-06-08-11-13-14-15-17-19-20-22-24-25 | 3726 | 9.033 | +0.0330 | 13 | 11.6479% | 0.1879% |
| 5 | 03-04-05-06-08-09-12-14-15-16-17-21-22-24-25 | 3726 | 8.9538 | -0.0462 | 14 | 10.2254% | 0.1342% |

Nenhum exemplo passou de 14 acertos em nenhum dos milhares de concursos testados, e todas as médias ficam a menos de 0,05 acerto da esperança teórica — a mesma conclusão dos 8 métodos e do backtest geral, agora demonstrada também para combinações fixas filtradas.


## Conclusão educativa

Frequência e atraso mostram apenas o que já aconteceu na amostra observada — não indicam o que vai sair no próximo concurso. Cada sorteio é independente dos anteriores. Se, com o tempo, os métodos acima convergirem para uma média de acertos parecida com a esperança teórica, isso confirma que a Lotofácil se comporta como um sorteio aleatório, não que algum método é melhor para ganhar. O mesmo vale para apostas estendidas: cobrem mais combinações, não criam vantagem matemática nova.
