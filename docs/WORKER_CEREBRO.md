# Worker + Cérebro Python

## Objetivo

Quando `motor_python_v4/checkpoints/operacional.json` existir (gerado pelo ciclo diário), o Worker deve **gravar jogos de sistema a partir desse arquivo** em vez de recalcular M1–M9 em JavaScript.

## Patch em `worker.js`

No topo de `worker.js` (ES module):

```js
import { loadGamesFromCerebroCheckpoint, persistSystemGames } from './worker_cerebro_games.js';
```

Substituir o início de `generateNextContestGames` por:

```js
async function generateNextContestGames(env, concurso) {
  const fromCerebro = await loadGamesFromCerebroCheckpoint(env, concurso);
  if (fromCerebro) {
    return persistSystemGames(env, concurso, fromCerebro);
  }
  // ... resto do código atual (fallback JS)
```

## Fluxo

1. GitHub Actions / `ciclo_diario.py` → `exportar_checkpoint_cerebro.py`
2. Commit de `motor_python_v4/checkpoints/operacional.json`
3. Deploy Cloudflare Assets
4. `runAutoCycle` → `generateNextContestGames` lê o checkpoint

## Endpoint

`GET /api/aprendizado/checkpoint-operacional` (worker_python_bridge.js)
