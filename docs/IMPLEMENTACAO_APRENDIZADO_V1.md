# Implementação do aprendizado v1

Esta entrega adiciona a primeira camada auditável sem alterar o `worker.js`, o painel unificado, o laboratório automático ou o fechamento existente.

## Dados consumidos

A página consulta `/api/sistema/status` e utiliza:

- `resultados_recentes`;
- `jogos_gerados` dos métodos M1–M9;
- `laboratorio_acumulado`;
- `laboratorio_semana_atual`;
- `proximo_concurso` e último resultado.

## Por que a primeira etapa é no navegador

O núcleo pode ser testado e publicado sem risco de quebrar o ciclo agendado do Cloudflare ou as tabelas D1 existentes. O Livro de Previsões usa `localStorage` e exportação JSON.

A etapa seguinte deve mover congelamento, assinatura e avaliação para o D1, executados automaticamente pelo `runAutoCycle` antes da busca do resultado seguinte.
