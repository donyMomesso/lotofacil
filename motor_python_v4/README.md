# Cérebro Python — Lotofácil v4 / v2 unificado

Módulo **fonte única da verdade** para o Laboratório Estatístico Lotofácil.

## O que este pacote é

- `metodos.py` — métodos de estudo M1–M9 (hipóteses neutras)
- `engine.py` — pontuação de dezenas, bases 15–21, fechamentos, memória adaptativa
- `audit_core.py` — walk-forward histórico (Brier, log-loss, top-21), checkpoints de 5
- `cerebro.py` — fachada única para scripts, API e ciclo diário
- `checkpoint.py` — checkpoint de auditoria (sem campos acionáveis)
- `api.py` — FastAPI de auditoria histórica

**Propósito:** estudo de matemática, estatística e probabilidade com dados reais.  
**Não** prevê sorteios e **não** recomenda apostas. Esperança teórica por jogo de 15 dezenas: **9,0**.

## Instalação

```bash
cd motor_python_v4
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso rápido — fachada Cerebro

```python
from cerebro import Cerebro, saude
from engine import Concurso

print(saude())

historico = [
    Concurso.criar(1, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]),
    # ... mais concursos
]
c = Cerebro(historico, seed=42)

# Um jogo de estudo por método (M1–M9)
jogos = c.gerar_metodos()

# Checkpoint operacional (ciclo diário / Worker)
ck = c.checkpoint_operacional(concurso_alvo=100)

# Fechamento a partir de base pontuada
geracao = c.gerar_fechamento(tamanho_base=18, quantidade=120)

# Auditoria histórica (sem ranking/jogos públicos)
relatorio = c.auditoria_historica()
```

## Export CLI

Na raiz do repositório:

```bash
python scripts/exportar_checkpoint_cerebro.py
python scripts/exportar_checkpoint_cerebro.py --fechamento --base 18 --jogos 30
```

Gera:
- `dados/checkpoint_cerebro.json`
- `motor_python_v4/checkpoints/operacional.json`

## API HTTP (auditoria)

```bash
uvicorn api:app --reload
```

- `GET /saude`
- `GET /auditoria-historica`
- `GET /checkpoint-5`
- `POST /auditoria-historica`

## Testes

```bash
pytest -q
```

## Arquitetura

Ver `docs/ARQUITETURA_CEREBRO.md` na raiz do repositório.

## Integração com o Worker

O `worker_python_bridge.js` já expõe export de resultados e checkpoint de auditoria.  
O checkpoint **operacional** (`checkpoints/operacional.json`) é o próximo passo de consumo no ciclo do Worker: registrar jogos de sistema a partir de `jogos_estudo` sem recalcular métodos em JavaScript.

## Experiência embutida no engine

- soma 180–220; 6–9 pares; ≥5 primos; moldura; linhas; sequência máx. 6
- repetição equilibrada; frequência 10/30; atraso e ciclo
- diversidade entre jogos; eliminação de resultados históricos idênticos
- recalibração conservadora dos pesos após volume mínimo
