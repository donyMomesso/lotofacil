# Governança Champion × Challenger

## Escopo

O módulo avalia somente concursos encerrados. Para cada concurso `N`, o cálculo usa exclusivamente resultados com número menor que `N`.

```text
treino_ate < concurso
```

O painel não publica ranking futuro, seleção de dezenas ou combinações.

## Versões

Modelo estatístico atual:

```text
historical-audit-v1.1.0
```

Governança atual:

```text
champion-governance-v1.0.0
```

A versão do modelo identifica como as pontuações históricas foram produzidas. A versão da governança identifica as regras usadas para comparar modelos e decidir uma promoção.

## Champion e Challenger

O Champion é o modelo ativo persistido no D1. O Challenger é comparado com ele usando exatamente os mesmos concursos encerrados.

A comparação é pareada por concurso:

- ganho de Brier = Brier do Champion menos Brier do Challenger;
- ganho de top 21 = top 21 do Challenger menos top 21 do Champion.

Valores positivos favorecem o Challenger.

## Correção de múltiplos testes

Os testes pareados de Brier e top 21 recebem correção Benjamini–Hochberg. A promoção exige valor-q do Brier menor ou igual a `0,05`.

Isso reduz o risco de promover um modelo apenas porque várias métricas foram testadas ao mesmo tempo.

## Regras obrigatórias para promoção

O Challenger só é promovido quando todas as regras abaixo passam simultaneamente:

1. pelo menos 30 concursos pareados;
2. integridade temporal, probabilística e de hashes sem falhas;
3. intervalo mínimo de 12 concursos desde a última promoção;
4. ausência de drift moderado ou alto no Challenger;
5. ganho médio de Brier positivo;
6. limite inferior do IC de 95% do ganho de Brier acima de zero;
7. valor-q Benjamini–Hochberg do Brier menor ou igual a `0,05`;
8. limite inferior do IC de 95% do ganho de top 21 não inferior a `-0,15`;
9. estabilidade nas janelas de 8, 16 e 24 concursos.

Uma falha de integridade bloqueia a decisão. As demais falhas mantêm o Champion atual.

## Janelas móveis

As janelas de 8, 16 e 24 concursos precisam mostrar:

- ganho de Brier positivo;
- ganho de top 21 não inferior a `-0,125`.

Essa regra impede promoção baseada apenas na média completa quando o desempenho recente é inconsistente.

## Persistência D1

### `aprendizado_historico`

Guarda cada avaliação fora da amostra e seu hash SHA-256.

### `aprendizado_resumos`

Guarda snapshots de robustez por modelo, versão, amostra e último concurso.

### `aprendizado_campeoes`

Guarda o Champion ativo por versão do modelo e versão da governança, o concurso desde o qual está ativo e o último concurso já avaliado pela governança.

### `aprendizado_decisoes`

Guarda cada decisão Champion × Challenger, incluindo:

- concurso mais recente incluído;
- Champion anterior;
- Challenger;
- decisão `promote`, `hold` ou `blocked`;
- modelo promovido, quando aplicável;
- comparação completa;
- regras aprovadas e reprovadas;
- hash SHA-256.

A chave única impede que a mesma decisão seja recriada para o mesmo concurso, Champion e Challenger.

## Ciclo automático

A governança é atualizada:

- ao abrir `GET /api/aprendizado/historico`;
- depois de uma execução manual bem-sucedida do ciclo;
- depois do ciclo agendado do Cloudflare.

Sem concurso novo, a decisão anterior é reutilizada. O sistema não troca o Champion repetidamente com os mesmos dados.

## Interpretação

A promoção indica apenas que, dentro das avaliações históricas disponíveis, o Challenger cumpriu regras estatísticas mais rígidas que o Champion. Isso não elimina a aleatoriedade dos sorteios nem garante desempenho futuro.
