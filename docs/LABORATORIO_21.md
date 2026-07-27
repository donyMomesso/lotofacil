# Laboratório 21 → 15

Página independente para análise combinatória de carteiras de 15 dezenas dentro de uma base fixa de 21 dezenas.

## Objetivo

Preservar integralmente o fechamento existente de 16 a 20 dezenas e oferecer um ambiente separado para:

- gerar uma carteira experimental otimizada;
- comparar com uma carteira aleatória da mesma quantidade;
- testar exatamente os 54.264 cenários internos;
- medir garantia mínima e coberturas 12+, 13+, 14+ e 15;
- reproduzir resultados usando uma semente numérica.

## Algoritmo

1. Gera todos os `C(21,15) = 54.264` cenários como máscaras de bits.
2. Cria um conjunto de candidatos equilibrando filtros suaves e diversidade.
3. Seleciona a carteira por busca gulosa, priorizando ganho de cobertura 14+, 13+ e 12+.
4. Valida a carteira final sem amostragem, percorrendo os 54.264 cenários.
5. Repete a validação com uma carteira aleatória de controle.

Os filtros individuais são usados apenas como desempate. A métrica principal é a cobertura da carteira completa.

## Condição

Toda cobertura é condicional a as 15 dezenas do cenário estarem dentro da base de 21 dezenas. O laboratório não prevê resultados futuros.

## Teste

```bash
node tests/test_lab21_core.js
```
