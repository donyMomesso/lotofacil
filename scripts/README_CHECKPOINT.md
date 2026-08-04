# Checkpoint operacional (automático)

## O que faz

1. Sincroniza `dados/resultados_lotofacil.csv` com a API da Caixa  
2. Valida histórico (sem buracos/duplicados)  
3. Exporta `dados/checkpoint_cerebro.json` + espelho  
   `motor_python_v4/checkpoints/operacional.json`  
4. `concurso_alvo` = último concurso + 1  

## Automação (GitHub Actions)

Workflow: `.github/workflows/checkpoint-operacional.yml`

- Agenda: **01:00 BRT** e **09:00 BRT** todos os dias  
- Também: **Actions → Checkpoint operacional → Run workflow**  

### Deploy automático no Cloudflare

No repositório GitHub → **Settings → Secrets and variables → Actions**, crie:

| Secret | Valor |
|--------|--------|
| `CLOUDFLARE_API_TOKEN` | Token com permissão de Workers/Assets |
| `CLOUDFLARE_ACCOUNT_ID` | ID da conta Cloudflare |

Sem esses secrets o bot **só commita** o checkpoint; o deploy continua manual:

```bash
git pull origin main
npx wrangler deploy
```

## Manual (sempre funciona)

```powershell
cd C:\Users\donyc\Documents\Lotofacil
python scripts/publicar_checkpoint.py
git add dados/resultados_lotofacil.csv dados/checkpoint_cerebro.json motor_python_v4/checkpoints/operacional.json
git commit -m "chore: checkpoint operacional"
git push origin main
npx wrangler deploy
```

## Conferir

- https://lotofacil.donyconfcargo.workers.dev/api/sistema/gate → `status: active`  
- https://lotofacil.donyconfcargo.workers.dev/api/sistema/sugestao → prioritários  
