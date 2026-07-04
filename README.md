# Laboratório Estatístico Lotofácil

Laboratório educativo para estudar matemática, estatística e probabilidade usando os resultados **reais** da Lotofácil como base de dados.

## Importante

Este projeto **não promete acertos, não recomenda apostas e não deve ser usado como ferramenta para apostar.** O objetivo é estudar frequência, distribuição, soma, pares/ímpares e os limites reais de padrões históricos. A Lotofácil é um sorteio aleatório: nenhum método aqui é avaliado como "mais perto" de 14 ou 15 acertos — isso não existe matematicamente antes do sorteio acontecer.

Toda comparação de método usa como referência a **esperança teórica de 9 acertos** por jogo de 15 dezenas (distribuição hipergeométrica: você escolhe 15 de 25 números, 15 são sorteados — o resultado esperado por acaso é 9).

## Acesso rápido

- `painel_mobile.html` — painel otimizado para celular.
- `painel.html` — painel clássico completo.
- `painel_jogos.html` — painel de jogos e conferências.
- `dados/banco_projeto.json` — banco de leitura do projeto inteiro.
- `reports/relatorio_estatistico.md` — relatório estatístico em Markdown.
- `diario_estatistico.md` — diário educativo das execuções.

## Banco do projeto

O arquivo `dados/banco_projeto.json` funciona como um banco de dados simples em JSON. Ele centraliza o estado do laboratório para acesso por painel mobile, automações futuras ou outras integrações.

Ele contém:

- metadados do projeto;
- total de concursos;
- último concurso registrado;
- próximo concurso;
- últimos resultados;
- frequência e atraso das dezenas;
- jogos de estudo do próximo concurso;
- últimas conferências;
- estatísticas dos métodos;
- links internos para os principais arquivos.

O gerador fica em:

```bash
python scripts/gerar_banco_projeto.py
```

## O que roda todo dia (sozinho, via GitHub Actions)

Ver `.github/workflows/analise-diaria.yml` — roda às **22h de Brasília**, depois do horário comum do sorteio:

1. Busca o(s) resultado(s) real(is) mais recente(s) em fonte pública que espelha os dados da Caixa.
2. Registra no histórico (`dados/resultados_lotofacil.csv`).
3. Importa jogos manuais de `dados/meus_jogos.csv`, se existir.
4. Confere os jogos fictícios do dia anterior contra o resultado real (`dados/conferencia.csv`).
5. Gera os jogos fictícios do próximo concurso, um por método (`dados/jogos_gerados.csv`).
6. Recalcula frequência/atraso das dezenas e desempenho comparado dos métodos.
7. Gera `reports/relatorio_estatistico.md`.
8. Gera `dados/banco_projeto.json`.
9. Gera `painel.html`, `painel_jogos.html` e `painel_mobile.html`.
10. Registra um bloco educativo em `diario_estatistico.md`.

O workflow comita e envia essas atualizações usando o token padrão do GitHub Actions — não precisa de senha ou chave configurada.

## Os 5 métodos (hipóteses de estudo, não estratégias)

| Método | O que faz |
|---|---|
| M1_aleatorio_puro | 15 dezenas sorteadas aleatoriamente, sem critério. É o controle do experimento. |
| M2_mais_frequentes | As 15 dezenas que mais saíram no histórico até aquele momento. |
| M3_mais_atrasadas | As 15 dezenas há mais concursos sem sair. |
| M4_par_impar_balanceado | Aleatório, forçando 8 pares e 7 ímpares. |
| M5_soma_faixa_comum | Aleatório, só aceita jogos cuja soma caia entre 180 e 210. |

A expectativa estatística é que, com o tempo, **todos convirjam para uma média de acertos parecida, perto de 9**. Se algum destoar por um tempo, isso é dado interessante para estudar variância e tamanho de amostra, não sinal de que funciona.

## Estrutura

```txt
lotofacil/
├─ dados/
│  ├─ resultados_lotofacil.csv   # histórico real de concursos
│  ├─ banco_projeto.json         # banco de leitura do projeto inteiro
│  ├─ jogos_gerados.csv          # jogos fictícios por método/dia
│  ├─ conferencia.csv            # acertos de cada jogo fictício
│  ├─ frequencia_dezenas.csv     # frequência e atraso por dezena
│  └─ estatisticas_metodos.csv   # desempenho comparado dos métodos
├─ scripts/
│  ├─ lotofacil_lib.py           # funções compartilhadas
│  ├─ buscar_resultado.py        # busca via requests
│  ├─ registrar_resultado.py     # grava um concurso já obtido
│  ├─ gerar_jogos.py             # gera os 5 jogos fictícios do dia
│  ├─ conferir_jogos.py          # confere jogos contra um resultado real
│  ├─ atualizar_estatisticas.py  # recalcula frequência/atraso/desempenho
│  ├─ gerar_banco_projeto.py     # gera dados/banco_projeto.json
│  ├─ gerar_relatorio.py         # gera reports/relatorio_estatistico.md
│  ├─ gerar_painel.py            # gera painel.html
│  ├─ gerar_painel_jogos.py      # gera painel_jogos.html
│  ├─ gerar_painel_mobile.py     # gera painel_mobile.html
│  ├─ diario.py                  # monta o bloco de texto do diário
│  └─ ciclo_diario.py            # orquestra tudo no GitHub Actions
├─ reports/
│  └─ relatorio_estatistico.md
├─ painel.html
├─ painel_jogos.html
├─ painel_mobile.html
├─ diario_estatistico.md
├─ requirements.txt
└─ .github/workflows/analise-diaria.yml
```

## Simulação retroativa (backtest)

`scripts/simular_backtest.py` roda os 5 métodos contra TODO o histórico real, a partir do 2º concurso, usando só dados disponíveis antes de cada concurso, sem olhar o futuro. Resultado atual, com 3724 concursos simulados por método:

| Método | Média de acertos | Diferença vs. esperança (9,0) |
|---|---|---|
| M1_aleatorio_puro | 9,0003 | +0,0003 |
| M2_mais_frequentes | 9,0336 | +0,0336 |
| M3_mais_atrasadas | 9,0263 | +0,0263 |
| M4_par_impar_balanceado | 8,9817 | -0,0183 |
| M5_soma_faixa_comum | 8,9936 | -0,0064 |

Nenhum jogo teve 15 acertos nos 18620 jogos simulados. As diferenças entre métodos são pequenas demais para significar qualquer coisa além de variação estatística. Resultados em `dados/simulacao_metodos.csv` e `dados/estatisticas_simulacao.csv`.

## Como rodar manualmente

```bash
pip install -r requirements.txt
cd scripts
python ciclo_diario.py
```

Isso só funciona com acesso livre à internet, porque `buscar_resultado.py` usa `requests`. Em ambientes com rede restrita, use `registrar_resultado.py` para gravar um resultado já obtido por outro meio, e depois rode `conferir_jogos.py`, `gerar_jogos.py` e `atualizar_estatisticas.py` na sequência.

## Fonte dos dados

Histórico completo do concurso 1, em 29/09/2003, até o concurso 3725, em 02/07/2026, com 3725 concursos reais, importado de planilha fornecida pelo usuário em 03/07/2026 (`scripts/importar_historico_excel.py`). A partir do workflow diário, o histórico cresce automaticamente, concurso a concurso, buscando na API pública que espelha os resultados oficiais da Caixa (`loteriascaixa-api`).

## Observação final

Resultados passados não garantem resultados futuros. Este laboratório serve para estudar estatística, validar hipóteses e enxergar os limites de padrões históricos, não para prever sorteios ou recomendar apostas.
