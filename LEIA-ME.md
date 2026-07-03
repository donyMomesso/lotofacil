> Nota: o `README.md` (na raiz do projeto) agora é a documentação
> principal, incluindo a automação via GitHub Actions e o painel visual
> (`painel.html`). Este arquivo continua válido como referência
> detalhada dos scripts locais.

# Laboratório Estatístico Lotofácil

Este é um projeto de **estudo de matemática, estatística e probabilidade**
usando os resultados reais da Lotofácil como base de dados. Ele **não é**
um sistema de apostas, não recomenda jogos e não promete acertos.

## Regra principal (não é opcional)

A Lotofácil é um sorteio aleatório. Nenhum método aqui é avaliado como
"mais perto de 14 ou 15 acertos" — isso não existe matematicamente antes
do sorteio acontecer. O que este laboratório faz é comparar, de forma
honesta, como diferentes formas de montar um jogo de 15 dezenas se
comportam ao longo de muitos concursos, sempre contra o valor teórico
esperado (**9 acertos em média**, calculado pela distribuição
hipergeométrica — não é opinião, é matemática).

## O que o sistema faz todo dia

1. Busca o resultado oficial mais recente da Lotofácil (fonte pública).
2. Registra esse resultado no histórico (`dados/resultados_lotofacil.csv`).
3. Confere os jogos fictícios que tinham aquele concurso como alvo e
   grava quantas dezenas cada um acertou (`dados/conferencia.csv`).
4. Gera os jogos fictícios do próximo concurso, um por método
   (`dados/jogos_gerados.csv`).
5. Recalcula frequência/atraso das dezenas e o desempenho comparado de
   cada método (`dados/frequencia_dezenas.csv` e
   `dados/estatisticas_metodos.csv`).
6. Registra um resumo educativo do dia em `diario_estatistico.md`.

Nenhum desses jogos é para jogar de verdade. São 5 dezenas fictícias por
dia, uma por método, só para observar o comportamento estatístico.

## Os 5 métodos (hipóteses de estudo, não estratégias)

| Método | O que faz |
|---|---|
| M1_aleatorio_puro | 15 dezenas sorteadas aleatoriamente, sem nenhum critério. É o "controle" do experimento. |
| M2_mais_frequentes | As 15 dezenas que mais saíram no histórico até aquele momento. |
| M3_mais_atrasadas | As 15 dezenas que estão há mais concursos sem sair. |
| M4_par_impar_balanceado | Sorteio aleatório, mas forçando 8 pares e 7 ímpares (proporção próxima da mais comum historicamente). |
| M5_soma_faixa_comum | Sorteio aleatório, mas só aceita jogos cuja soma das dezenas caia na faixa 180–210 (faixa historicamente mais frequente). |

A expectativa estatística é que, com o tempo, **todos os métodos
convirjam para uma média de acertos parecida, perto de 9** — porque a
frequência passada de uma dezena não muda a probabilidade dela sair no
próximo sorteio independente. Se algum método aparentar destoar muito,
isso também é um dado interessante para estudar (tamanho de amostra,
variância, viés de confirmação), não um sinal de que "funciona".

## Estrutura de arquivos

```
dados/
  resultados_lotofacil.csv   # histórico real de concursos
  jogos_gerados.csv          # jogos fictícios gerados por método/dia
  conferencia.csv            # acertos de cada jogo fictício
  frequencia_dezenas.csv     # frequência e atraso de cada dezena
  estatisticas_metodos.csv   # desempenho comparado dos métodos
scripts/
  lotofacil_lib.py           # funções compartilhadas
  registrar_resultado.py     # grava um concurso real no histórico
  gerar_jogos.py             # gera os 5 jogos fictícios do dia
  conferir_jogos.py          # confere jogos contra um resultado real
  atualizar_estatisticas.py  # recalcula frequência/atraso/desempenho
diario_estatistico.md        # resumo educativo, um bloco por dia
```

## Fonte dos dados

Resultados oficiais buscados via API pública que espelha os dados da
Caixa (`loteriascaixa-api`). O histórico inicial (~17 concursos) foi
carregado manualmente em 03/07/2026; a partir da tarefa agendada diária,
o histórico cresce automaticamente, concurso a concurso.

## Sobre a tarefa agendada

Roda uma vez por dia. Se não houve sorteio 