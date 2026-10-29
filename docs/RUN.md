# Spustenie celého systému (frontend + backend)

Frontend je teraz napojený na **reálny backend** (`HttpApiClient`). Treba bežať
oboje. Predvolený base URL backendu je `http://localhost:8000`.

## 1. Backend (terminál A)

```
cd backend
.venv\Scripts\activate                # venv je už vytvorený a nainštalovaný
uvicorn app.main:app --reload --port 8000
```

API: `http://localhost:8000` · dokumentácia: `http://localhost:8000/docs`

> Pre reálnu izoláciu sandboxu (Linux limity): `docker compose up --build`.

## 2. Frontend (terminál B)

```
cd frontend
node_modules\.bin\vite.cmd --port 5180
```

Otvor `http://localhost:5180`. CORS na backende povoľuje porty 5173, 5174, 5180.

## 3. Čo otestovať

| Stránka | Reálne volá backend |
|---|---|
| Problems / Algorithms / Generator | zoznamy + **živý náhľad generátora** (sandbox spustí `generate`) |
| **Visualizer** | `/api/visualize` → **reálne spustený Python** s trackerom |
| **Experiments** | seedovaný `exp_sort` je „pending" → klikni **Spustiť experiment** (odbehne v sandboxe) |
| **Results** | po spustení → grafy (čas / porovnania / pamäť), tabuľka, export CSV/JSON |

## Prepínače (voliteľné)

- **Offline/demo bez backendu:** vytvor `frontend/.env.local` s `VITE_USE_MOCK=true`
  → použije sa `MockApiClient`.
- **Iný backend URL:** `VITE_API_BASE=http://host:port` v `frontend/.env.local`.

## Overené (E2E)

- CORS (allow-origin pre 5180, preflight OPTIONS) ✓
- cross-origin `POST /api/visualize` → reálna stopa ✓
- frontend `tsc` + `vite build` zelené ✓
- backend `smoke_test.py` 19/19 ✓
