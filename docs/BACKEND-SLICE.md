# Backend — tenký vertikálny rez (hotovo)

Cieľ: end-to-end Python backend, ktorý de-riskuje sandbox + tracker a dá prvé
reálne dáta. Realizuje kontrakt z [`../CONTRACT.md`](../CONTRACT.md).
Detaily a spustenie: [`../backend/README.md`](../backend/README.md).

## Čo je hotové

- [x] **FastAPI app** (`app/main.py`) — CORS, štart = `create_all` + seed sorting problému
- [x] **DB** — SQLAlchemy modely (Problem, Algorithm, Generator, Experiment, Run) + SQLite
- [x] **CRUD endpointy** — problems, algorithms, generators
- [x] **Reálny tracker** (`sandbox/tracker_impl.py`) — produkuje kroky (Step) + počíta operácie; rýchly režim merania (bez snímkov)
- [x] **Sandbox runner** (`sandbox/runner.py`) — izolovaný proces (spawn) + timeout + AST kontrola zakázaných importov + `setrlimit` (Linux)
- [x] **Executor** (`executor.py`) — experiment → behy s časom, pamäťou, počtami operácií, kontrolou korektnosti voči referencii; reprodukovateľný seed
- [x] **Endpointy** — `/api/visualize`, `/api/code/validate`, experiment run/results/runs/export, generator preview
- [x] **Deployment** — Dockerfile + docker-compose (Linux = reálne resource limity)

## Overené (19 smoke + HTTP)

`python smoke_test.py` → **19/19**: sandbox (vizualizácia, meranie, generátor, odmietnutie `import os`), executor (8 behov, všetky korektné, bubble > quick v porovnaniach).

HTTP (uvicorn + curl):
- `/api/visualize` (bubble) → 22 krokov, compare 10 / swap 7, zotriedené pole
- experiment create → run → results → export CSV: 8 behov, všetky ok+korektné
- **Bubble n=60 = 1770 porovnaní** (presne n·(n-1)/2), pomalší než Quick (330) — teória sedí
- multiprocessing-spawn funguje aj vnútri uvicorn na Windows

## Dôležité

- **Windows = len vývoj.** `setrlimit` (CPU/pamäť) je Linux-only; na Windows chráni timeout + izolácia procesu + AST guard. **Produkcia = Docker** (`docker compose up`).
- Beh experimentu je zatiaľ **synchrónny** (WebSocket progres je ďalší krok).

## Ďalší krok

- **`HttpApiClient implements ApiClient`** na frontende + prepnutie `frontend/src/api/index.ts` (mock → HTTP) → frontend beží na reálnom backende.
- Potom: WebSocket progres, experiment setup formulár (Fáza 1).
