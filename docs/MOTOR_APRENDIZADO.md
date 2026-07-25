# Motor de aprendizado — avaliação histórica

Este módulo mede modelos estatísticos apenas em concursos já encerrados.

## Fluxo

1. O Worker lê resultados armazenados no D1.
2. Para cada concurso-alvo encerrado, usa somente concursos anteriores.
3. Os modelos Estável e Adaptativo produzem pontuações probabilísticas para fins de avaliação.
4. O resultado real é comparado com a pontuação produzida pelo histórico anterior.
5. Métricas e hash SHA-256 são gravados em `aprendizado_historico`.
6. O painel exibe somente desempenho histórico agregado e por concurso.

## Métricas

- Brier Score, com referência neutra de 0,2400.
- Log Loss.
- Acertos dentro das faixas top 15, 18, 19, 20 e 21.
- Média top 21, com referência neutra de 12,60.
- Alerta de possível sobreajuste quando a janela recente piora de modo relevante.

## Proteção temporal

Cada registro exige `treino_ate < concurso`. O Worker interrompe o processamento caso detecte vazamento temporal.

## Persistência

A tabela é criada de forma idempotente pelo Worker. A migração SQL equivalente está em `migrations/0002_aprendizado_historico.sql`.

A chave única é composta por:

- concurso;
- modelo;
- versão do modelo.

Isso permite comparar versões sem sobrescrever avaliações anteriores.

## Integração com o ciclo

O arquivo histórico é atualizado:

- depois do ciclo agendado do Cloudflare;
- depois de uma execução manual bem-sucedida do ciclo;
- ao abrir `/api/aprendizado/historico`, caso existam concursos encerrados ainda não registrados.

## Limite de uso

O módulo não publica ranking para concurso futuro, não seleciona bases e não exporta combinações. Seu objetivo é auditar se os métodos apresentam sinal estatístico fora da amostra.
