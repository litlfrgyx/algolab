# Dátová vrstva (`src/api/`)

Jediný prístupový bod k dátam pre celý frontend. Stránky **nikdy** nedržia
hardcoded dáta — volajú `api`, ktoré implementuje rozhranie `ApiClient`
z [`../types/api.ts`](../types/api.ts).

```ts
import { api } from '../api'

const problems = await api.listProblems()
const trace = await api.visualize({ algorithm_id: 'alg_bubble', input: [5, 3, 1, 4, 2] })
```

## Štruktúra

| Súbor | Obsah |
|-------|-------|
| `index.ts` | Singleton `export const api: ApiClient` — **jediné miesto** výmeny mock → HTTP |
| `client.ts` | `MockApiClient implements ApiClient` — in-memory CRUD + reálna `visualize`/`previewGenerator` |
| `mock/seed.ts` | Seedované entity (1 sorting problém s 3 algoritmami, generátor, dokončený experiment) |
| `mock/sorting.ts` | Tracery (bubble/quick/insertion) → produkujú `VisualizationTrace` podľa kontraktu |
| `mock/generators.ts` | Seedovaný PRNG + `generateArray(n, mode, seed)` (reprodukovateľnosť) |

## Prečo mock za rozhraním

Kontrakt `ApiClient` je zhodný s budúcim FastAPI backendom (snake_case telá =
Pydantic schémy). Keď backend vznikne:

```ts
// src/api/index.ts — zmení sa JEDEN riadok, stránky sa nedotknú
export const api: ApiClient = new HttpApiClient('/api')
```

## Čo je „reálne" už teraz

- **`visualize()`** spúšťa skutočné tracery a vracia `VisualizationTrace`
  (`Step[]` + `operation_counts`) — kontrakt vizualizéra je overený end-to-end.
- **`previewGenerator()`** generuje seedovaný vstup → reprodukovateľný náhľad.
- **`getResults()`** počíta agregáciu min/avg/max z behov (nie hardcoded).
- **`validateCode()`** odmietne `import os` a pod. (scenár č. 8 z práce).
- **`exportExperiment()`** vyrobí reálny CSV/JSON Blob.

## Čo je simulované (kým nebude backend)

- Python sa v prehliadači nespúšťa → tracery sú JS porty seedovaných algoritmov;
  ad-hoc kód z editora `visualize` zatiaľ odmietne.
- `runExperiment()` výsledky „dopočíta" synchrónne namiesto streamovania cez WS.
- Merania času/pamäte sú syntetické, ale **interne konzistentné** (čas ∝ počet
  operácií; bubble ∝ n², quick ∝ n log n).
