# Robustez Histórica do Motor de Aprendizado

## Escopo

O módulo avalia somente concursos encerrados. Para cada concurso `N`, o cálculo usa exclusivamente resultados com número menor que `N`. A condição obrigatória é:

```text
treino_ate < concurso
```

O painel não publica ranking futuro, seleção de dezenas ou combinações.

## Versão atual

`historical-audit-v1.1.0`

Cada alteração do algoritmo cria uma nova versão. A chave única dos registros históricos continua sendo concurso, modelo e versão, preservando comparações antigas.

## Camadas de avaliação

### Walk-forward

Reconstitui cada concurso como se o resultado ainda não fosse conhecido. Os modelos Estável e Adaptativo recebem exatamente o mesmo histórico disponível naquele ponto.

### Intervalos de confiança

O sistema usa bootstrap determinístico para calcular IC de 95% da média do Brier e do top 21. A semente inclui modelo, versão, amostra e último concurso, permitindo reprodução.

### Teste por permutação

O top 21 observado é comparado com rankings neutros simulados pela distribuição hipergeométrica da Lotofácil. O valor-p é unilateral: mede a frequência com que a referência neutra alcança média igual ou maior.

### Calibração

Cada registro calcula:

- erro esperado de calibração (ECE);
- sharpness, medida da dispersão das probabilidades.

Probabilidades mais separadas não são automaticamente melhores; precisam permanecer calibradas.

### Janelas móveis

São mostradas as janelas mais recentes de 8, 16 e 24 concursos para detectar dependência de período.

### Drift

A janela recente de oito concursos é comparada com os oito anteriores. O alerta considera piora no Brier e queda no top 21.

## Força da evidência

- **Amostra insuficiente:** menos de 20 concursos.
- **Sem evidência de vantagem:** intervalos ainda incluem as referências neutras.
- **Sinal exploratório:** uma métrica supera a referência.
- **Sinal histórico moderado:** Brier e top 21 superam as referências com IC de 95%, valor-p menor que 0,05 e pelo menos 50 concursos.

Esses rótulos descrevem apenas dados históricos e não garantem repetição.

## Persistência D1

### `aprendizado_historico`

Guarda cada avaliação fora da amostra e seu hash SHA-256.

### `aprendizado_resumos`

Guarda snapshots de robustez por modelo, versão, tamanho de amostra e último concurso. O resumo inclui intervalos, permutação, calibração, janelas, drift e classificação da evidência.

## Integridade

Ao carregar a API, a versão atual é verificada em três pontos:

1. ausência de vazamento temporal;
2. soma das probabilidades igual a 15;
3. reconstrução do hash SHA-256.

A rota pública é:

```text
GET /api/aprendizado/historico
```

A resposta contém apenas métricas históricas e registros já avaliados.
