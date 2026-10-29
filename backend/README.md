# ALGO_ANALYZER — Backend (tenký vertikálny rez)

FastAPI + SQLite + sandboxovaný executor. Realizuje kontrakt z
[`../CONTRACT.md`](../CONTRACT.md). Frontend sa naň napojí výmenou
`MockApiClient` → `HttpApiClient` (jeden riadok v `frontend/src/api/index.ts`).

## Štruktúra

```
app/
  main.py          FastAPI app, CORS, štart (create_all + seed)
  config.py        nastavenia (DATABASE_URL, CORS, limity)
  db.py            SQLAlchemy engine + session
  models.py        ORM tabuľky (Problem, Algorithm, Generator, Experiment, Run)
  schemas.py       Pydantic DTO (zrkadlo TS typov)
  seed.py          demo sorting problém (rovnaké id ako frontend)
  executor.py      orchestrácia experimentu → ExperimentRun
  sandbox/
    runner.py      spustenie kódu v izolovanom procese (spawn) + timeout
    tracker_impl.py  produkuje kroky (Step) + počíta operácie
    limits.py      setrlimit (CPU/pamäť) — len Linux/Docker
  routers/         problems, algorithms, generators, experiments, visualize
smoke_test.py      overenie sandboxu + executora bez servera
```

## Spustenie — lokálne (Windows/macOS/Linux, vývoj)

```
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API beží na `http://localhost:8000`, dokumentácia na `http://localhost:8000/docs`.

> **Pozor (bezpečnosť):** `resource.setrlimit` (CPU/pamäťový limit) funguje len na
> Linuxe. Na Windows pri vývoji chráni iba timeout + izolácia procesu + zoznam
> zakázaných importov. **Pre reálnu izoláciu používaj Docker.**

## Spustenie — Docker (odporúčané, reálna izolácia)

```
cd backend
docker compose up --build
```

## Overenie

```
python smoke_test.py        # sandbox + executor (rýchle, bez HTTP)
```

## Kľúčové endpointy

| Endpoint | Popis |
|---|---|
| `POST /api/visualize` | spustí algoritmus s trackerom → `VisualizationTrace` |
| `POST /api/experiments/{id}/run` | odbehne experiment (synchrónne) → uloží behy |
| `GET /api/experiments/{id}/results` | agregované výsledky (min/avg/max, počty operácií) |
| `POST /api/generators/{id}/preview` | reprodukovateľný náhľad vstupu |
| `POST /api/code/validate` | statická kontrola (odmietne `import os` a pod.) |

## Bezpečnostný model sandboxu

1. **Statická AST kontrola** — zakázané importy (`os`, `sys`, `subprocess`, `socket`, …) a volania (`eval`, `open`, `__import__`).
2. **Izolovaný proces** (`multiprocessing`, kontext `spawn`).
3. **Timeout** → `terminate`.
4. **Resource limity** (`setrlimit` CPU/pamäť) — Linux/Docker.
5. **Docker** — izolácia FS a siete (primárna vrstva).

## TODO (ďalšie kroky)

- WebSocket progres počas behu (`/ws/experiments/{id}`) — teraz synchrónne.
- `HttpApiClient` na frontende + prepnutie `src/api/index.ts`.
- Grid/string tracker metódy (Fáza 2).
