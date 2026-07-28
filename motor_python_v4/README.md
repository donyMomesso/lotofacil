# Cérebro Python — Auditoria Histórica

Este diretório concentra a fonte única de auditoria retrospectiva do projeto.

O objetivo é comparar, em concursos já encerrados, os métodos Estável, Adaptativo e Python v4 usando exatamente o mesmo histórico disponível em cada ponto do tempo.

## Escopo

O relatório público contém somente:

- Brier Score;
- Log Loss;
- média histórica dentro do top 21;
- comparação com referências neutras;
- métricas acumuladas;
- métricas dos últimos 5 concursos;
- drift entre dois blocos consecutivos;
- integridade temporal;
- hashes reproduzíveis.

O relatório não contém dezenas, jogos, bases, previsões, recomendação de método ou seleção para concursos futuros.

## Checkpoints de 5 concursos

O Python executa walk-forward cronológico e fecha um checkpoint apenas quando existe um novo bloco completo de 5 concursos avaliados.

Exemplo:

```bash
cd motor_python_v4
python checkpoint.py historico_real.json --saida checkpoints/latest.json --min-training 30
```

Se ainda não existir um novo bloco completo, o arquivo anterior permanece inalterado.

## Proteção temporal

Para cada concurso avaliado, vale obrigatoriamente:

```text
treino_ate < concurso_avaliado
```

O resultado do concurso-alvo nunca participa do próprio cálculo.

## API educativa

```bash
cd motor_python_v4
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --reload
```

No Windows:

```powershell
.venv\Scripts\activate
```

Rotas:

```text
GET  /saude
GET  /auditoria-historica
GET  /checkpoint-5
POST /auditoria-historica
```

A API não possui rota de geração de jogos ou ranking futuro.

## Integração

O Cloudflare Worker:

1. exporta os resultados encerrados do D1;
2. serve o último relatório Python publicado;
3. mantém as demais rotas do sistema pelo Worker principal.

O GitHub Actions consulta o histórico, executa o Python e publica `checkpoints/latest.json` somente quando fecha um novo grupo de 5 avaliações.

## Testes

```bash
cd motor_python_v4
python -m unittest -v test_audit_core.py
```

Os testes verificam:

- ausência de vazamento temporal;
- rejeição de concurso duplicado;
- fechamento somente em múltiplos de 5;
- reprodutibilidade dos hashes;
- ausência de campos acionáveis no relatório público.
