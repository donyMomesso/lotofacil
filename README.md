# Laboratório Estatístico Lotofácil

Laboratório educativo para estudar matemática, estatística e probabilidade usando os resultados **reais** da Lotofácil como base de dados.

## Importante

Este projeto **não promete acertos, não recomenda apostas e não deve ser usado como ferramenta para apostar.** O objetivo é estudar frequência, distribuição, soma, pares/ímpares e os limites reais de padrões históricos. A Lotofácil é um sorteio aleatório: nenhum método aqui é avaliado como "mais perto" de 14 ou 15 acertos — isso não existe matematicamente antes do sorteio acontecer.

Toda comparação de método usa como referência a **esperança teórica de 9 acertos** por jogo de 15 dezenas (distribuição hipergeométrica: você escolhe 15 de 25 números, 15 são sorteados — o resultado esperado por acaso é 9).

## Acesso rápido

- `painel_mobile.html` — painel otimizado para celular.
- `painel.html` — painel clássico completo.
- `painel_jogos.html` / `painel_jogos_v2.html` — painel avançado de jogos, registro, conferência, aprendizado e combinação inteligente.
- `dados/banco_projeto.json` — banco de leitura do projeto inteiro.
- `reports/relatorio_estatistico.md` — relatório estatístico em Markdown.
- `reports/analise_comparativa_metodos.md` — análise comparativa profunda dos 8 métodos (rankings, estabilidade, desempenho por período).
- `diario_estatistico.md` — diário educativo das execuções.

## Visão geral do sistema

O projeto hoje funciona como um fluxo completo de laboratório estatístico:

1. **Gerar** jogos por métodos estatísticos (M1 a M8), sugestões por IA do painel, jogo manual, IA Direto ou combinação inteligente.
2. **Registrar** os jogos escolhidos em "Jogos registrados", vinculando concurso, dezenas, origem/método e regra de retenção.
3. **Conferir** automaticamente os jogos registrados quando um novo resultado entra no sistema.
4. **Aprender** com o histórico real de conferências, calculando ranking, pesos, tendência, confiança e penalizações por origem.
5. **Sugerir combinação** para o próximo sorteio, distribuindo a quantidade de jogos entre origens/perfis diferentes, sem concentrar tudo em um único método.

Esse fluxo não muda a natureza aleatória da Lotofácil. Ele organiza o estudo: tudo que o sistema gera, registra e confere vira dado para análise posterior.

## Funcionalidades principais

- **Geração por 8 métodos de estudo (M1 a M8):** métodos básicos e avançados para comparar filtros, frequências, atraso, soma, paridade, repetição controlada e cobertura de pares.
- **Registro automático dos jogos do sistema:** no painel avançado, o botão "Registrar todos os jogos do sistema" salva os jogos exibidos no desdobramento em "Jogos registrados", com origem clara (`Sistema M1`, `Sistema M2`, etc.).
- **Jogos manuais, IA Direto e Combo Inteligente:** o usuário pode salvar jogos escolhidos manualmente, pedir geração automática pela IA do painel ou gerar a carteira recomendada pelo aprendizado.
- **Conferência automática com histórico detalhado:** cada jogo registrado pode ser conferido contra novos concursos, salvando dezenas jogadas, dezenas sorteadas, quantidade de acertos, dezenas acertadas, concurso e origem/método.
- **Retenção configurável dos jogos:** jogos podem ser mantidos até exclusão manual ou descartados após 2 rodadas conferidas.
- **Aprendizado por origem:** o sistema calcula ranking por origem/método, pesos, estabilidade, tendência, confiança e penalizações.
- **Combinação inteligente de perfis:** o painel recomenda uma distribuição prática de jogos entre até 5 origens, limitando concentração e respeitando os pesos do aprendizado.
- **Backtest completo M1-M8:** simulação retroativa com 5 jogos por método em cada concurso histórico, sem usar dados futuros na geração.

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
5. Gera os jogos fictícios do próximo concurso para os métodos M1-M8 (`dados/jogos_gerados.csv`).
6. Recalcula frequência/atraso das dezenas e desempenho comparado dos métodos.
7. Gera `reports/relatorio_estatistico.md`.
8. Gera `dados/banco_projeto.json`.
9. Gera `painel.html`, `painel_jogos.html` e `painel_mobile.html`.
10. Registra um bloco educativo em `diario_estatistico.md`.

O workflow comita e envia essas atualizações usando o token padrão do GitHub Actions — não precisa de senha ou chave configurada.

Além do workflow do repositório, o `worker.js` também possui ciclo operacional no Cloudflare (`POST /api/ciclo/rodar` e agenda configurada no `wrangler.jsonc`) para manter o painel avançado sincronizado: registra resultados no D1, confere jogos pendentes, atualiza o histórico de conferências, descarta jogos expirados e gera jogos do sistema para o próximo concurso.

## Os 8 métodos (hipóteses de estudo, não estratégias)

| Método | O que faz |
|---|---|
| M1_aleatorio_puro | 15 dezenas sorteadas aleatoriamente, sem critério. É o controle do experimento. |
| M2_mais_frequentes | As 15 dezenas que mais saíram no histórico até aquele momento. |
| M3_mais_atrasadas | As 15 dezenas há mais concursos sem sair. |
| M4_par_impar_balanceado | Aleatório, forçando 8 pares e 7 ímpares. |
| M5_soma_faixa_comum | Aleatório, só aceita jogos cuja soma caia entre 180 e 210. |
| M6_filtros_combinados | Aleatório, filtrando por soma (185–215), pares (7 a 9) e repetições em relação ao concurso anterior (8 a 11) ao mesmo tempo. |
| M7_cobertura_pares | Aleatório, ranqueado pela cobertura de duplas de dezenas que mais co-ocorreram recentemente. |
| M8_repeticao_controlada | Aleatório, mantém só jogos com 9, 10 ou 11 dezenas repetidas em relação ao concurso anterior. |

A expectativa estatística é que, com o tempo, **todos convirjam para uma média de acertos parecida, perto de 9**. Se algum destoar por um tempo, isso é dado interessante para estudar variância e tamanho de amostra, não sinal de que funciona. Ver `reports/analise_comparativa_metodos.md` para o detalhamento completo dos 8 métodos (rankings, estabilidade, desempenho por período e conclusões).

## Como o aprendizado funciona

O aprendizado do painel usa a tabela `conferencias`, que guarda o resultado real de cada jogo registrado contra cada concurso conferido. A análise é feita por origem/método, por exemplo `Sistema M2`, `Sistema M7`, `IA Direto`, `Manual` ou `Combo Inteligente`.

O cálculo atual considera:

- **Janela recente:** ranking calculado com base nos últimos 60 concursos conferidos.
- **Ponderação temporal:** conferências mais recentes têm peso maior que conferências antigas.
- **Média de acertos e frequência de 11+/12+:** mede desempenho observado no histórico registrado.
- **Estabilidade:** desvio padrão dos acertos, usado para identificar origens menos oscilantes.
- **Tendência:** comparação entre desempenho recente e anterior dentro da janela.
- **Confiança:** amostras maiores são tratadas como mais confiáveis; amostras pequenas recebem menor peso.
- **Penalizações:** origens com média baixa, pouca frequência de 11+ ou poucos jogos conferidos têm o peso reduzido.

A geração por IA usa esses pesos como orientação: perfis associados a origens melhores recebem bônus, enquanto perfis penalizados têm menor influência. A "Combinação recomendada para o próximo sorteio" usa o mesmo aprendizado para distribuir jogos entre até 5 origens, limitando concentração e mantendo diversidade.

Importante: isso é um mecanismo de organização e estudo do histórico registrado, não uma previsão. Mesmo com ranking e pesos, cada novo sorteio continua independente.

## Estrutura

```txt
lotofacil/
├─ dados/
│  ├─ resultados_lotofacil.csv   # histórico real de concursos
│  ├─ banco_projeto.json         # banco de leitura do projeto inteiro
│  ├─ jogos_gerados.csv          # jogos fictícios por método/dia
│  ├─ conferencia.csv            # acertos de cada jogo fictício
│  ├─ frequencia_dezenas.csv     # frequência e atraso por dezena
│  ├─ estatisticas_metodos.csv   # desempenho comparado dos métodos (jogos fictícios diários)
│  ├─ simulacao_metodos.csv      # backtest completo M1-M8, jogo a jogo (149.040 linhas)
│  └─ estatisticas_simulacao.csv # resumo estatístico do backtest completo, por método
├─ scripts/
│  ├─ lotofacil_lib.py             # funções compartilhadas
│  ├─ buscar_resultado.py          # busca via requests
│  ├─ registrar_resultado.py       # grava um concurso já obtido
│  ├─ gerar_jogos.py               # gera os jogos fictícios do dia (M1-M8)
│  ├─ gerar_jogos_avancados.py     # lógica dos métodos M6-M8
│  ├─ conferir_jogos.py            # confere jogos contra um resultado real
│  ├─ atualizar_estatisticas.py    # recalcula frequência/atraso/desempenho
│  ├─ simular_backtest.py          # motor do backtest retroativo M1-M8
│  ├─ executar_backtest_completo.py # roda o backtest completo e valida os CSVs gerados
│  ├─ gerar_banco_projeto.py       # gera dados/banco_projeto.json
│  ├─ gerar_relatorio.py           # gera reports/relatorio_estatistico.md
│  ├─ gerar_painel.py              # gera painel.html
│  ├─ gerar_painel_jogos.py        # gera painel_jogos.html
│  ├─ gerar_painel_mobile.py       # gera painel_mobile.html
│  ├─ diario.py                    # monta o bloco de texto do diário
│  └─ ciclo_diario.py              # orquestra tudo no GitHub Actions
├─ reports/
│  ├─ relatorio_estatistico.md          # relatório geral, atualizado a cada ciclo diário
│  └─ analise_comparativa_metodos.md    # análise comparativa profunda dos 8 métodos (backtest completo)
├─ analises/    # análises estatísticas futuras, ainda não consolidadas em reports/
├─ graficos/    # imagens e gráficos gerados a partir dos dados (ainda vazia)
├─ backups/     # versões antigas de arquivos importantes (não servidas no site)
├─ docs/        # documentação adicional (ex.: LEIA-ME.md legado)
├─ painel.html
├─ painel_jogos.html / painel_jogos_v2.html
├─ painel_mobile.html
├─ worker.js                    # Cloudflare Worker: API, autenticação, D1 e assets
├─ migrations/                  # schema do banco D1 usado pelo painel avançado
├─ wrangler.jsonc               # configuração Cloudflare Workers / D1 / assets
├─ diario_estatistico.md
├─ requirements.txt
└─ .github/workflows/
   ├─ analise-diaria.yml       # ciclo diário (busca resultado, gera jogos, painéis, diário)
   └─ backtest-completo.yml    # roda o backtest completo M1-M8 sob demanda
```

`analises/`, `graficos/`, `backups/` e `docs/` estão listadas em `.assetsignore` — não são servidas pelo site publicado (Cloudflare Workers Assets), da mesma forma que `scripts/` e `reports/` já não eram.

## Estrutura técnica do painel avançado

O painel avançado (`painel_jogos_v2.html`) é servido pelo Cloudflare Workers Assets e conversa com a API implementada em `worker.js`. O banco operacional do painel fica no Cloudflare D1 (`lotofacil-db`), com migrations em `migrations/`.

Tabelas principais:

- `usuarios`: cadastro simples de acesso ao painel.
- `sessoes`: tokens/sessões de autenticação.
- `jogos`: jogos registrados pelo usuário ou pelo sistema, com concurso, método/origem, dezenas, observação, status, regra de retenção (`manter_salvo`, `descartar_apos_rodadas`) e datas.
- `conferencias`: histórico detalhado de conferência por jogo e concurso, com dezenas jogadas, dezenas sorteadas, dezenas acertadas, quantidade de acertos e método/origem.
- `resultados`: resultados reais registrados no banco do Worker.
- `jogos_sistema`: jogos gerados automaticamente pelo ciclo do Worker para o próximo concurso.
- `execucoes_ciclo`: auditoria das execuções automáticas do ciclo diário no Worker.

Rotas principais da API:

- `GET /api/health`: checagem simples do serviço.
- `GET /api/sistema/status`, `GET /api/resultados/status` e `GET /api/ciclo/status`: estado público do sistema, resultados e última execução.
- `POST /api/auth/register` e `POST /api/auth/login`: cadastro e login.
- `POST /api/auth/logout`: encerra a sessão.
- `GET /api/me`: valida a sessão atual.
- `GET /api/jogos`: lista jogos registrados, conferências, indicadores da rodada, aprendizado por origem e combinação recomendada.
- `POST /api/jogos`: registra um novo jogo em "Jogos registrados".
- `PATCH /api/jogos/:id`: atualiza dados de um jogo registrado.
- `DELETE /api/jogos/:id`: remove/cancela um jogo do usuário.
- `POST /api/jogos/conferir-duas-rodadas`: confere jogos registrados contra até duas rodadas disponíveis.
- `POST /api/jogos/conferir-pendentes`: confere automaticamente jogos pendentes contra resultados ainda não processados.
- `POST /api/ciclo/rodar`: executa o ciclo do Worker, registrando resultados, conferindo jogos pendentes, descartando jogos expirados e gerando jogos do próximo concurso.

## Simulação retroativa (backtest completo M1-M8)

`scripts/executar_backtest_completo.py` (que chama `scripts/simular_backtest.py`) roda os 8 métodos contra TODO o histórico real, a partir do 2º concurso, usando só dados disponíveis antes de cada concurso, sem olhar o futuro. Resultado atual, com **3.726 concursos simulados** e **149.040 jogos avaliados** (18.630 por método):

| Método | Média de acertos | Diferença vs. esperança (9,0) | % com 11+ acertos |
|---|---|---|---|
| M1_aleatorio_puro | 8,9966 | -0,0034 | 10,510% |
| M2_mais_frequentes | 9,0388 | +0,0388 | 11,331% |
| M3_mais_atrasadas | 9,0158 | +0,0158 | 10,832% |
| M4_par_impar_balanceado | 9,0005 | +0,0005 | 10,617% |
| M5_soma_faixa_comum | 8,9946 | -0,0054 | 10,494% |
| M6_filtros_combinados | 9,0010 | +0,0010 | 10,902% |
| M7_cobertura_pares | 8,9983 | -0,0017 | 10,601% |
| M8_repeticao_controlada | 8,9881 | -0,0119 | 10,134% |

Nenhum jogo teve 15 acertos nos 149.040 jogos simulados. As diferenças entre métodos são pequenas frente ao desvio padrão individual (~1,22) e não indicam vantagem preditiva real — ver `reports/analise_comparativa_metodos.md` para o detalhamento estatístico completo (rankings, estabilidade, desempenho por período). Resultados em `dados/simulacao_metodos.csv` e `dados/estatisticas_simulacao.csv`.

Para rodar o backtest completo novamente:

```bash
cd scripts
python executar_backtest_completo.py
```

## Como rodar manualmente

```bash
pip install -r requirements.txt
cd scripts
python ciclo_diario.py
```

Isso só funciona com acesso livre à internet, porque `buscar_resultado.py` usa `requests`. Em ambientes com rede restrita, use `registrar_resultado.py` para gravar um resultado já obtido por outro meio, e depois rode `conferir_jogos.py`, `gerar_jogos.py` e `atualizar_estatisticas.py` na sequência.

## Fonte dos dados

O histórico foi importado inicialmente a partir de planilha fornecida pelo usuário em 03/07/2026 (`scripts/importar_historico_excel.py`), começando no concurso 1, de 29/09/2003. A partir do workflow diário e do ciclo do Worker, o histórico cresce automaticamente, concurso a concurso, buscando na API pública que espelha os resultados oficiais da Caixa (`loteriascaixa-api`).

## Observação final

Resultados passados não garantem resultados futuros. Este laboratório serve para estudar estatística, validar hipóteses e enxergar os limites de padrões históricos, não para prever sorteios ou recomendar apostas.
