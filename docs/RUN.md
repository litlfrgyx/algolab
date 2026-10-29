# Spustenie AlgoLab

## Lokálne na Windows

Backend (terminál A):

```
cd backend
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend (terminál B):

```
cd frontend
npm install
node_modules\.bin\vite.cmd
```

Otvor http://localhost:5173. Vite presmeruje `/api` na backend na porte 8000
(`vite.config.ts`), takže netreba nastavovať CORS ani adresu API.

Databáza je súbor `backend/algoanalyzer.db`. Pri zmene schémy alebo katalógu sa doplní sama.
Vymazaním súboru sa začne odznova.

## Lokálne v Dockeri

Na Linuxe v kontajneri platia aj limity pamäte a CPU sandboxu:

```
docker compose -f backend/docker-compose.yml up --build
```

## Testy

```
cd backend
python catalog_test.py          # všetky algoritmy katalógu na všetkých druhoch vstupu
python smoke_test.py            # API cez TestClient: katalóg, ochrana, experiment, vizualizácia
python experiments_report.py > ..\docs\OVERENIE-zlozitosti.md   # odhad zložitosti na všetkých experimentoch
cd ..\frontend
npm run build                   # kontrola typov a zostavenie
npm run lint
```

`smoke_test.py` sa dá spustiť aj proti PostgreSQL: nastav `DATABASE_URL=postgresql://...`.

## Nasadenie (Vercel a Supabase)

1. Supabase: schéma `algolab` a rola `algolab_app` s heslom, ktorá má na schému právo
   `USAGE, CREATE`. Tabuľky vytvorí aplikácia sama pri prvej požiadavke.
2. Vercel projekt `algolab-runner` s koreňovým priečinkom `runner`, premenná `RUNNER_TOKEN`.
3. Vercel projekt `algolab` z koreňa repozitára (`vercel.json`), premenné:
   - `DATABASE_URL=postgresql://algolab_app.<ref>:<heslo>@<pooler>:6543/postgres`
   - `DB_SCHEMA=algolab`
   - `RUNNER_URL=https://<runner>.vercel.app`
   - `RUNNER_TOKEN` rovnaký ako v runneri
   - `EDIT_PASSWORD` heslo na vlastný kód, prázdne znamená bez ochrany
4. Po nasadení over `/api/info` a spusti jeden experiment.

## Aktuálne nasadenie

| Časť | Adresa |
|---|---|
| Aplikácia | https://algolab-kpi.vercel.app |
| Runner (sandbox) | https://algolab-runner.vercel.app, prijíma len požiadavky s `RUNNER_TOKEN` |
| Vercel tím | `algolab`, projekty `algolab` a `algolab-runner`, región funkcií `dub1` |
| Databáza | Supabase projekt v `eu-west-1`, schéma `algolab`, rola `algolab_app`, pooler `aws-0-eu-west-1.pooler.supabase.com:6543` |

Každý push do vetvy `main` nasadí oba projekty znova. Heslá sú len v premenných prostredia
na Verceli, nie v repozitári.
