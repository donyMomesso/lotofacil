# Motor de Aprendizado Probabilístico

## Objetivo

Unificar os dados já produzidos pelo ecossistema do Lotofácil Lab em um ciclo auditável:

1. resultados históricos;
2. laboratório automático de 20 mil jogos;
3. agregado semanal;
4. jogos atuais dos métodos M1–M9;
5. ranking probabilístico das 25 dezenas;
6. seleção de uma base de 21 dezenas;
7. congelamento da previsão antes do resultado;
8. avaliação automática quando o resultado aparece.

O sistema não pressupõe que sorteios sejam previsíveis. A hipótese só ganha força quando supera referências neutras em dados futuros.

## Modelos

A primeira versão compara dois modelos:

- **Estável:** distribui mais peso entre janelas de 5, 10, 20 e 50 concursos;
- **Adaptativo:** reage mais à janela curta, aos votos M1–M9 e ao laboratório recente.

O Champion é escolhido por walk-forward, priorizando menor Brier Score e maior média de acertos no top 21.

## Calibração

Cada uma das 25 dezenas recebe uma probabilidade. Um ajuste de intercepto garante que a soma das probabilidades seja 15, preservando a restrição estrutural do sorteio.

A referência neutra por dezena é 60%. Para uma base de 21 dezenas, a referência de acertos esperados é 12,60.

## Walk-forward

Para prever o concurso `N`, o modelo usa apenas concursos anteriores a `N`. O concurso alvo nunca participa da construção de suas próprias características.

Métricas:

- Brier Score;
- Log Loss;
- acertos no top 15, 18, 19, 20 e 21;
- diferença do top 21 contra a referência 12,60.

## Livro de Previsões

O painel `aprendizado.html` congela no navegador:

- concurso-alvo;
- último concurso usado;
- versão e modelo Champion;
- probabilidades e ranking das 25 dezenas;
- top 15, 18, 19, 20 e 21;
- tamanho do laboratório utilizado;
- hash SHA-256 do conteúdo congelado.

Quando o resultado entra em `/api/sistema/status`, previsões pendentes são avaliadas automaticamente.

## Limitação da primeira etapa

O livro está no `localStorage` do navegador. Isso permite uso imediato e exportação JSON, mas não substitui uma assinatura no servidor. A próxima etapa deve persistir previsões no D1 durante o ciclo agendado do Cloudflare.
