# Laboratório Estatístico Lotofácil

Laboratório educativo para estudar matemática, estatística e probabilidade
usando os resultados **reais** da Lotofácil como base de dados.

## Importante

Este projeto **não promete acertos, não recomenda apostas e não deve ser
usado como ferramenta para apostar.** O objetivo é estudar frequência,
distribuição, soma, pares/ímpares e os limites reais de padrões
históricos. A Lotofácil é um sorteio aleatório: nenhum método aqui é
avaliado como "mais perto" de 14 ou 15 acertos — isso não existe
matematicamente antes do sorteio acontecer.

Toda comparação de método usa como referência a **esperança teórica de
9 acertos** por jogo de 15 dezenas (distribuição hipergeométrica: você
escolhe 15 de 25 números, 15 são sorteados — o resultado esperado por
acaso é 9).

## O que roda todo dia (sozinho, via GitHub Actions)

Ver `.github/workflows/analise-diaria.yml` — roda às 10h de Brasília:

1. Busca o(s) resultado(s) real(is) mais recente(s) (fonte pública que
   espelha os dados da Caixa).
2. Registra no histórico (`dados/resultados_lotofacil.csv`).
3. Confere os jogos fictícios do dia anterior contra o resultado real
   (`dados/conferencia.csv`).
4. Gera os jogos fictícios do próximo concurso, um por método
   (`dados/jogos_gerados.csv`).
5. Recalcula frequência/atraso das dezenas e desempenho comparado dos
   métodos.
6. Gera `reports/relatorio_estatistico.md` e `painel.html` (painel
   visual, abre em qualquer navegador).
7. Registra um bloco educativo em `diario_estatistico.md`.

O workflow comita e envia essas atualizações usando o token padrão do
GitHub Actions — não precisa de nenhuma senha ou chave configurada.

## Os 5 métodos (hipóteses de estudo, não estratégias)

| Método | O que faz |
|---|---|
| M1_aleatorio_puro | 15 dezenas sorteadas aleatoriamente, sem critério. É o "controle" do experimento. |
| M2_mais_frequentes | As 15 dezenas que mais saíram no histórico até aquele momento. |
| M3_mais_atrasadas | As 15 dezenas há mais concursos sem sair. |
| M4_par_impar_balanceado | Aleatório, forçando 8 pares e 7 ímpares. |
| M5_soma_faixa_comum | Aleatório, só aceita jogos cuja soma caia entre 180 e 210. |

A expectativa estatística é que, com o tempo, **todos convirjam para
uma média de acertos parecida, perto de 9**. Se algum destoar muito por
um tempo, isso também é dado interessante para estudar (variância,
tamanho de amostra), não sinal de que "funciona".

## Estrutura

```txt
lotofacil/
├─ dados/
│  ├─ resultados_lotofacil.csv   # histórico real de concursos
│  ├─ jogos_gerados.csv          # jogos fictícios por método/dia
│  ├─ conferencia.csv            # acertos de cada jogo fictício
│  ├─ frequencia_dezenas.csv     # frequência e atraso por dezena
│  └─ estatisticas_metodos.csv   # desempenho comparado dos métodos
├─ scripts/
│  ├─ lotofacil_lib.py           # funções compartilhadas (sem rede)
│  ├─ buscar_resultado.py        # busca via requests (roda no GitHub Actions)
│  ├─ registrar_resultado.py     # grava um concurso já obtido
│  ├─ gerar_jogos.py             # gera os 5 jogos fictícios do dia
│  ├─ conferir_jogos.py          # confere jogos contra um resultado real
│  ├─ atualizar_estatisticas.py  # recalcula frequência/atraso/desempenho
│  ├─ gerar_relatorio.py         # gera reports/relatorio_estatistico.md
│  ├─ gerar_painel.py            # gera painel.html
│  ├─ diario.py                  # monta o bloco de texto do diário (5 pontos)
│  └─ ciclo_diario.py            # orquestra tudo (usado pelo GitHub Actions)
├─ reports/
│  └─ relatorio_estatistico.md
├─ painel.html                   # painel visual, abrir no navegador
├─ diario_estatistico.md         # diário educativo, um bloco por dia
├─ requirements.txt
└─ .github/workflows/analise-diaria.yml
```

## Simulação retroativa (backtest)

`scripts/simular_backtest.py` roda os 5 métodos contra TODO o histórico
real (a partir do 2º concurso), usando só dados disponíveis antes de
cada concurso (sem "olhar o futuro"). Resultado atual, com 3724
concursos simulados por método:

| Método | Média de acertos | Diferença vs. esperança (9,0) |
|---|---|---|
| M1_aleatorio_puro | 9,0003 | +0,0003 |
| M2_mais_frequentes | 9,0336 | +0,0336 |
| M3_mais_atrasadas | 9,0263 | +0,0263 |
| M4_par_impar_balanceado | 8,9817 | -0,0183 |
| M5_soma_faixa_comum | 8,9936 | -0,0064 |

Nenhum jogo teve 15 acertos nos 18620 jogos simulados. As diferenças
entre métodos são pequenas demais para significar qualquer coisa além
de variação estatística — ver `diario_estatistico.md` para a análise
completa. Resultados em `dados/simulacao_metodos.csv` (linha a linha) e
`dados/estatisticas_simulacao.csv` (agregado).

## Como rodar manualmente

```bash
pip install -r requirements.txt
cd scripts
python ciclo_diario.py
```

Isso só funciona com acesso livre à internet (a `buscar_resultado.py`
usa `requests` direto). Em ambientes com rede restrita, use
`registrar_resultado.py` para gravar um resultado já obtido por outro
meio, e depois rode `conferir_jogos.py`, `gerar_jogos.py` e
`atualizar_estatisticas.py` na sequência.

## Fonte dos dados

Histórico completo (concurso 1, 29/09/2003, até o concurso 3725,
02/07/2026 — 3725 concursos reais) importado de planilha fornecida
pelo usuário em 03/07/2026 (`scripts/importar_historico_excel.py`).
A partir do workflow diário, o histórico cresce automaticamente,
concurso a concurso, buscando na API pública que espelha os
resultados oficiais da Caixa (`loteriascaixa-api`).

## Observação final

Resultados passados 