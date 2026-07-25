# Motor Estatístico Lotofácil v4

Módulo isolado para selecionar bases de 15 a 21 dezenas, gerar fechamentos completos ou reduzidos, executar backtests cronológicos e manter memória adaptativa.

## Experiência incorporada

- soma entre 180 e 220;
- 6 a 9 pares;
- mínimo de 5 primos;
- pelo menos 8 dezenas da moldura;
- no mínimo 4 linhas;
- sequência máxima de 6 dezenas;
- repetição equilibrada do concurso anterior;
- frequência dos últimos 10 e 30 concursos;
- atraso equilibrado e ciclo aberto;
- diversidade entre jogos;
- eliminação de resultados históricos idênticos;
- registro de jogos com 13 ou mais acertos;
- recalibração conservadora dos pesos após volume mínimo.

## Instalação

```bash
cd motor_python_v4
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows:

```powershell
.venv\Scripts\activate
```

## API

```bash
uvicorn api:app --reload
```

Documentação: `http://127.0.0.1:8000/docs`

Exemplo para uma base de 18 dezenas e 120 jogos:

```bash
curl -X POST http://127.0.0.1:8000/gerar-fechamento \
  -H "Content-Type: application/json" \
  -d '{"tamanho_base":18,"quantidade_jogos":120}'
```

## Backtest sem vazamento

```bash
python backtest.py historico_real.json --inicio 60 --base 18 --jogos 120
```

Cada concurso-alvo é analisado usando somente concursos anteriores. Uma base de 18 dezenas possui exatamente 816 combinações simples de 15 dezenas. Um fechamento reduzido não mantém a mesma garantia do fechamento completo; a API informa a cobertura nominal e distribui os jogos buscando diversidade.

## Integração futura

O módulo foi colocado em pasta própria para não interferir no Worker, no D1 e na governança Champion × Challenger existentes. A etapa seguinte é ligar o resultado do backtest deste motor ao pipeline de candidatos Challenger, permitindo promoção apenas após evidência histórica suficiente.
