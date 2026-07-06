# Análise Comparativa dos Métodos M1–M8 — Backtest Completo

_Fonte dos dados: `dados/estatisticas_simulacao.csv` e `dados/simulacao_metodos.csv`, gerados pelo backtest retroativo executado por `scripts/executar_backtest_completo.py`._

**Escopo do backtest**: 3.726 concursos simulados (concurso 2 ao 3.727), 149.040 jogos avaliados no total — 18.630 jogos por método (5 jogos por método em cada concurso), usando em cada rodada apenas o histórico disponível até o concurso anterior. Valor teórico esperado de acertos por jogo de 15 dezenas: **9.0** (distribuição hipergeométrica).

Este documento é uma leitura estatística objetiva dos resultados já gerados. Nenhum valor aqui foi estimado ou arredondado além do que já consta nos CSVs de origem.

---

## 1. Ranking geral por média de acertos

| # | Método | Média de acertos | Dif. vs. esperança (9.0) |
|---|---|---|---|
| 1 | M2_mais_frequentes | 9.0388 | +0.0388 |
| 2 | M3_mais_atrasadas | 9.0158 | +0.0158 |
| 3 | M6_filtros_combinados | 9.0010 | +0.0010 |
| 4 | M4_par_impar_balanceado | 9.0005 | +0.0005 |
| 5 | M7_cobertura_pares | 8.9983 | -0.0017 |
| 6 | M1_aleatorio_puro | 8.9966 | -0.0034 |
| 7 | M5_soma_faixa_comum | 8.9946 | -0.0054 |
| 8 | M8_repeticao_controlada | 8.9881 | -0.0119 |

A amplitude entre o 1º e o 8º colocado é de apenas **0,0507 acerto** — bem pequena frente ao desvio padrão individual de cada método (≈1,22). Todos os 8 métodos estão a menos de 0,04 acerto da esperança teórica.

## 2. Ranking por percentual de jogos com 11+ acertos

| # | Método | % com 11+ acertos |
|---|---|---|
| 1 | M2_mais_frequentes | 11,331% |
| 2 | M6_filtros_combinados | 10,902% |
| 3 | M3_mais_atrasadas | 10,832% |
| 4 | M4_par_impar_balanceado | 10,617% |
| 5 | M7_cobertura_pares | 10,601% |
| 6 | M1_aleatorio_puro | 10,510% |
| 7 | M5_soma_faixa_comum | 10,494% |
| 8 | M8_repeticao_controlada | 10,134% |

## 3. Ranking por percentual de jogos com 13+ acertos

| # | Método | % com 13+ acertos |
|---|---|---|
| 1 | M5_soma_faixa_comum | 0,252% |
| 2 | M6_filtros_combinados | 0,183% |
| 3 | M8_repeticao_controlada | 0,172% |
| 4 | M1_aleatorio_puro | 0,140% |
| 4 | M7_cobertura_pares | 0,140% |
| 6 | M4_par_impar_balanceado | 0,107% |
| 7 | M2_mais_frequentes | 0,102% |
| 8 | M3_mais_atrasadas | 0,097% |

M5_soma_faixa_comum se destaca nesta métrica específica: sua taxa de 13+ (0,252%) é o dobro ou mais da taxa dos métodos nas últimas posições (M3: 0,097%, M2: 0,102%).

## 4. Análise de estabilidade (desvio padrão + amplitude)

| Método | Desvio padrão | Mínimo | Máximo | Amplitude (máx-mín) |
|---|---|---|---|---|
| M7_cobertura_pares | 1,2186 | 5 | 14 | 9 |
| M3_mais_atrasadas | 1,2220 | 5 | 14 | 9 |
| M8_repeticao_controlada | 1,2221 | 5 | 14 | 9 |
| M4_par_impar_balanceado | 1,2231 | 5 | 13 | **8** |
| M2_mais_frequentes | 1,2243 | 5 | 14 | 9 |
| M5_soma_faixa_comum | 1,2265 | 5 | 14 | 9 |
| M1_aleatorio_puro | 1,2295 | 5 | 14 | 9 |
| M6_filtros_combinados | 1,2340 | 5 | 13 | **8** |

(ordenado por desvio padrão, do menor para o maior)

- **Menor desvio padrão**: M7_cobertura_pares (1,2186).
- **Menor amplitude**: M4_par_impar_balanceado e M6_filtros_combinados empatados (8), os únicos dois métodos que não registraram nenhum jogo com 14 ou 15 acertos no backtest completo.
- Combinando as duas medidas, M4_par_impar_balanceado é o único método com amplitude mínima (8) e desvio padrão abaixo da mediana do grupo (1,2231, 4º menor entre os 8).

## 5. Tabela comparativa completa

| Método | Jogos simulados | Média | Desvio padrão | Dif. vs. esperança | Mín. | Máx. | Amplitude | % 11+ | % 12+ | % 13+ | % 14+ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1_aleatorio_puro | 18.630 | 8,9966 | 1,2295 | -0,0034 | 5 | 14 | 9 | 10,510% | 1,895% | 0,140% | 0,0054% |
| M2_mais_frequentes | 18.630 | 9,0388 | 1,2243 | +0,0388 | 5 | 14 | 9 | 11,331% | 1,755% | 0,102% | 0,0161% |
| M3_mais_atrasadas | 18.630 | 9,0158 | 1,2220 | +0,0158 | 5 | 14 | 9 | 10,832% | 1,723% | 0,097% | 0,0054% |
| M4_par_impar_balanceado | 18.630 | 9,0005 | 1,2231 | +0,0005 | 5 | 13 | 8 | 10,617% | 1,809% | 0,107% | 0,0000% |
| M5_soma_faixa_comum | 18.630 | 8,9946 | 1,2265 | -0,0054 | 5 | 14 | 9 | 10,494% | 1,793% | 0,252% | 0,0161% |
| M6_filtros_combinados | 18.630 | 9,0010 | 1,2340 | +0,0010 | 5 | 13 | 8 | 10,902% | 1,820% | 0,183% | 0,0000% |
| M7_cobertura_pares | 18.630 | 8,9983 | 1,2186 | -0,0017 | 5 | 14 | 9 | 10,601% | 1,798% | 0,140% | 0,0107% |
| M8_repeticao_controlada | 18.630 | 8,9881 | 1,2221 | -0,0119 | 5 | 14 | 9 | 10,134% | 1,798% | 0,172% | 0,0161% |

Nenhum método registrou qualquer jogo com 15 acertos nos 149.040 jogos simulados.

---

## 6. Desempenho por período (últimos 100, 200 e 500 concursos)

Cada período foi extraído diretamente de `dados/simulacao_metodos.csv`, filtrando pelo número do concurso. Concurso mais recente no backtest: **3.727**.

### Últimos 100 concursos (concursos 3.628 a 3.727 — 500 jogos por método)

| Método | Média | Desvio padrão | Mín. | Máx. | % 11+ | % 13+ |
|---|---|---|---|---|---|---|
| M2_mais_frequentes | 9,124 | 1,1174 | 7 | 12 | 10,0% | 0,0% |
| M6_filtros_combinados | 9,080 | 1,2384 | 6 | 12 | 12,6% | 0,0% |
| M1_aleatorio_puro | 9,048 | 1,1789 | 6 | 13 | 10,8% | 0,2% |
| M7_cobertura_pares | 9,038 | 1,2118 | 5 | 12 | 11,2% | 0,0% |
| M5_soma_faixa_comum | 9,016 | 1,2648 | 6 | 13 | 10,6% | 0,6% |
| M8_repeticao_controlada | 9,006 | 1,2108 | 6 | 13 | 10,2% | 0,2% |
| M3_mais_atrasadas | 8,956 | 1,1773 | 6 | 12 | 9,0% | 0,0% |
| M4_par_impar_balanceado | 8,950 | 1,2278 | 5 | 13 | 9,2% | 0,2% |

### Últimos 200 concursos (concursos 3.528 a 3.727 — 1.000 jogos por método)

| Método | Média | Desvio padrão | Mín. | Máx. | % 11+ | % 13+ |
|---|---|---|---|---|---|---|
| M2_mais_frequentes | 9,055 | 1,1992 | 7 | 12 | 11,5% | 0,0% |
| M7_cobertura_pares | 9,028 | 1,1930 | 5 | 12 | 10,5% | 0,0% |
| M5_soma_faixa_comum | 9,019 | 1,2291 | 6 | 13 | 10,8% | 0,3% |
| M1_aleatorio_puro | 9,007 | 1,2062 | 5 | 13 | 10,1% | 0,4% |
| M6_filtros_combinados | 9,005 | 1,2494 | 5 | 12 | 11,4% | 0,0% |
| M8_repeticao_controlada | 8,991 | 1,2029 | 5 | 13 | 10,5% | 0,1% |
| M4_par_impar_balanceado | 8,980 | 1,2655 | 5 | 13 | 10,2% | 0,3% |
| M3_mais_atrasadas | 8,956 | 1,2231 | 5 | 13 | 9,3% | 0,1% |

### Últimos 500 concursos (concursos 3.228 a 3.727 — 2.500 jogos por método)

| Método | Média | Desvio padrão | Mín. | Máx. | % 11+ | % 13+ |
|---|---|---|---|---|---|---|
| M2_mais_frequentes | 9,0476 | 1,2450 | 5 | 12 | 10,88% | 0,00% |
| M7_cobertura_pares | 9,0168 | 1,2187 | 5 | 14 | 11,12% | 0,12% |
| M6_filtros_combinados | 9,0080 | 1,2303 | 5 | 13 | 11,08% | 0,12% |
| M5_soma_faixa_comum | 9,0028 | 1,2275 | 6 | 13 | 10,84% | 0,36% |
| M1_aleatorio_puro | 8,9840 | 1,2174 | 5 | 13 | 10,08% | 0,16% |
| M4_par_impar_balanceado | 8,9816 | 1,2108 | 5 | 13 | 9,56% | 0,12% |
| M8_repeticao_controlada | 8,9696 | 1,1939 | 5 | 13 | 9,28% | 0,08% |
| M3_mais_atrasadas | 8,9644 | 1,1856 | 5 | 13 | 9,24% | 0,04% |

### Leitura dos períodos recentes

- **M2_mais_frequentes** ocupa a 1ª posição em média de acertos nos três períodos recentes (100, 200 e 500 concursos) e também no ranking geral — é o único método com esse padrão de consistência.
- **M6_filtros_combinados** e **M7_cobertura_pares** aparecem entre os 3 primeiros em % de 11+ acertos em todos os recortes recentes, reforçando a posição de destaque que também têm no ranking geral (2º e 5º lugar, respectivamente).
- **M3_mais_atrasadas**, apesar de ocupar o 2º lugar no ranking geral por média, cai para a última ou penúltima posição em % de 11+ acertos em todos os três períodos recentes (9,0% / 9,3% / 9,24%) — um contraste que evidencia como rankings por métrica diferente (média vs. % de 11+) podem divergir dentro do mesmo método.
- Nenhum método muda de forma abrupta ou monotônica conforme a janela recente encolhe (100 → 200 → 500); as oscilações de posição observadas são consistentes com variação amostral, não com uma tendência real de melhora ou piora ao longo do tempo, já que cada concurso da Lotofácil é sorteado de forma independente dos anteriores.

---

## 7. Verificação estatística das maiores diferenças observadas

Para não superinterpretar rankings baseados em diferenças pequenas, os dois métodos nos extremos do ranking geral (M2_mais_frequentes, no topo, e M8_repeticao_controlada, na última posição) foram comparados diretamente:

- Diferença de média de acertos (M2 − M8): 9,0388 − 8,9881 = **0,0507**, equivalente a **z ≈ 4,0** (erro padrão combinado ≈ 0,0127, com n=18.630 jogos por método).
- Diferença de % de 11+ acertos (M2 − M8): 11,331% − 10,134% = **1,197 pontos percentuais**, equivalente a **z ≈ 3,7** (teste de duas proporções, n=18.630 cada).

Esses valores de z indicam que a diferença entre o melhor e o pior método **não é puro acaso de arredondamento** dentro deste recorte específico de 3.726 concursos — mas isso não deve ser confundido com vantagem preditiva real: cada sorteio da Lotofácil é independente dos anteriores, e a esperança matemática de 9,0 acertos por jogo de 15 dezenas é idêntica para qualquer conjunto de dezenas, seja ele escolhido por frequência, atraso, paridade ou qualquer outro critério. A diferença observada reflete apenas o encaixe específico de cada heurística com a sequência de resultados já sorteados no histórico disponível — não há garantia estatística ou matemática de que ela se repita nos próximos concursos.

---

## 8. Conclusões

**Qual método apresentou o melhor desempenho geral?**
Pelos indicadores empíricos do backtest, **M2_mais_frequentes** lidera tanto em média de acertos (9,0388) quanto em % de jogos com 11+ acertos (11,331%), e é o único método que se mantém em 1º lugar em média nos três recortes recentes (100, 200 e 500 concursos) além do ranking geral.

**Qual método foi mais estável?**
Considerando desvio padrão e amplitude juntos, **M4_par_impar_balanceado** tem o perfil mais estável: é um dos dois métodos com a menor amplitude observada (8, entre mínimo 5 e máximo 13) e tem desvio padrão abaixo da mediana do grupo (1,2231). **M7_cobertura_pares** tem o menor desvio padrão isolado (1,2186), mas com amplitude igual à maioria dos outros métodos (9).

**Existe algum método que se destaca em acertos mais altos (13+)?**
Sim. **M5_soma_faixa_comum** tem a maior taxa de 13+ acertos (0,252%), bem acima dos demais — mais que o dobro da taxa dos métodos nas últimas posições dessa métrica (M3: 0,097%, M2: 0,102%). Vale notar que M5 não se destaca nas demais métricas (7º lugar em média geral, 7º em % de 11+), o que mostra que "acertar mais alto às vezes" e "ter média/consistência melhor" são propriedades distintas dos dados.

**Algum método deve ser priorizado ou descartado com base nos dados?**
Não. Apesar de existir uma diferença estatisticamente perceptível entre o método no topo (M2) e o método na base (M8) do ranking geral (z ≈ 3,7–4,0, ver seção 7), essa diferença **não constitui vantagem preditiva real** para concursos futuros: a matemática da Lotofácil (distribuição hipergeométrica, sorteios independentes) garante a mesma esperança de 9,0 acertos para qualquer conjunto de 15 dezenas, independentemente do critério usado para escolhê-lo. Todos os 8 métodos permanecem a menos de 0,04 acerto de média da esperança teórica, e nenhum registrou um único jogo com 15 acertos em 149.040 jogos simulados. Priorizar ou descartar um método com base nesses números seria interpretar ruído amostral de um histórico já sorteado como sinal preditivo — o que contraria a própria natureza do jogo.
