# Fechamento combinatório 21 → 15

Este módulo monta e valida carteiras de jogos de 15 dezenas a partir de uma base fixa de 21 dezenas.

## O que ele mede

Para uma base de 21 dezenas existem exatamente **54.264** resultados internos possíveis de 15 dezenas.

O validador compara cada um desses cenários com todos os jogos da carteira e informa:

- garantia mínima condicional;
- quantidade e percentual de cenários com 15 pontos;
- quantidade e percentual de cenários com 14 ou mais;
- quantidade e percentual de cenários com 13 ou mais;
- quantidade e percentual de cenários com 12 ou mais;
- distribuição completa do melhor acerto.

A condição é sempre a mesma: **as 15 dezenas sorteadas precisam estar dentro das 21 dezenas da base**.

## Fechamento completo

O único fechamento que garante 15 pontos em todos os cenários internos possui os 54.264 jogos possíveis.

Uma carteira reduzida pode alcançar 15 em alguns cenários, mas sua garantia real deve ser calculada pelo validador.

## Executar

No diretório raiz do projeto:

```bash
python scripts/fechamento_21.py \
  --base "01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21" \
  --jogos 120 \
  --seed 21 \
  --saida dados/fechamento_21.json
```

A base aceita dezenas separadas por vírgula, espaço ou hífen.

## Como o gerador reduz a carteira

O gerador usa busca gulosa e prioriza:

1. distância e diversidade entre os jogos;
2. ganho de cobertura de 14+;
3. ganho de cobertura de 13+;
4. filtros de soma, paridade, primos e moldura somente como desempate suave.

A busca usa uma amostra para selecionar os jogos, mas o relatório final percorre os **54.264 cenários sem amostragem**.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os testes verificam:

- validação da base;
- ausência de jogos duplicados;
- garantia mínima de uma carteira unitária;
- garantia de 15 pontos no fechamento completo.

## Limites e interpretação

Este módulo não prevê sorteios e não aumenta a probabilidade individual de uma combinação. Seu objetivo é distribuir uma quantidade definida de jogos e medir matematicamente a cobertura obtida dentro da base escolhida.
