# Arquitetura do Cérebro Python

## Princípio

**Python é a única fonte da verdade** para matemática, métodos de estudo, pontuação, fechamentos e checkpoints.

O Cloudflare Worker permanece como borda: autenticação, D1, assets e orquestração. Ele **não** reimplementa métodos estatísticos.

```
┌──────────────────────────────────────────────┐
│  CÉREBRO PYTHON (motor_python_v4/)           │
│  metodos.py  → M1–M9                         │
│  engine.py   → base, fechamento, memória     │
│  audit_core  → walk-forward / Brier / top21  │
│  cerebro.py  → fachada única                 │
└──────────────────┬───────────────────────────┘
                   │ checkpoint JSON
                   ▼
┌──────────────────────────────────────────────┐
│  GitHub Actions / scripts locais             │
│  exportar_checkpoint_cerebro.py              │
│  ciclo_diario.py (consome o mesmo núcleo)    │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  Cloudflare Worker (borda fina)              │
│  auth · D1 · painéis · governança decision   │
│  lê checkpoint / não recalcula métodos       │
└──────────────────────────────────────────────┘
```

## Versões

| Componente | Versão |
|---|---|
| Cérebro (fachada) | `cerebro-python-v2.0.0` |
| Auditoria histórica | `python-historical-brain-v1.0.0` |
| Propósito | `historical_education_only` |

## Módulos

### `metodos.py`
Implementação canônica de M1–M9. Qualquer script, backtest ou painel deve obter jogos de estudo daqui (diretamente ou via `Cerebro`).

### `engine.py`
Pontuação de dezenas, seleção de base 15–21, fechamento com diversidade, memória adaptativa e filtros estruturais.

### `audit_core.py`
Avaliação fora da amostra (Brier, log-loss, top-21), checkpoints de 5 concursos, sem campos acionáveis (ranking de dezenas / jogos proibidos no relatório público de auditoria).

### `cerebro.py`
Fachada:

```python
from cerebro import Cerebro

c = Cerebro.de_json("historico.json")
jogos = c.gerar_metodos(seed=42)
ck = c.checkpoint_operacional(concurso_alvo=3728)
audit = c.auditoria_historica()
fechamento = c.gerar_fechamento(tamanho_base=18, quantidade=120)
```

### Checkpoint operacional

Gerado por:

```bash
python scripts/exportar_checkpoint_cerebro.py
python scripts/exportar_checkpoint_cerebro.py --fechamento --base 18 --jogos 30
```

Arquivos:
- `dados/checkpoint_cerebro.json`
- `motor_python_v4/checkpoints/operacional.json` (espelho para o bridge)

Contém jogos de estudo por método, pesos da memória, ranking interno de estudo e hash. **Não é previsão.**

## Integração com `lotofacil_lib.py`

Na próxima etapa, `scripts/lotofacil_lib.py` deve delegar `gerar_todos_metodos` e helpers para `motor_python_v4.metodos`, eliminando duplicação. Até lá, manter compatibilidade de nomes de métodos (M1–M9).

## Regras de evolução

1. Novo método = só em `metodos.py` + teste unitário + entrada no backtest.
2. Promoção de hipótese (ex.: Tese V2) só via governança Champion×Challenger com amostra suficiente.
3. Worker nunca recalcula M1–M9; apenas consome checkpoint / D1.
4. Relatórios públicos de auditoria continuam sem campos acionáveis.

## Testes

```bash
cd motor_python_v4
pip install -r requirements.txt
pytest -q
```
