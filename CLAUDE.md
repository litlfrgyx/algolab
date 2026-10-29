# CLAUDE.md

Pokyny pre Claude Code pri práci v tomto repozitári.

## Projekt

**AlgoLab**, webová aplikácia k diplomovej práci „Systém pre podporu návrhu a analýzy
algoritmov“ (FEI TUKE, KPI). Študent si vyberie úlohu, pozrie vizualizáciu algoritmu krok
po kroku, porovná algoritmy v experimente na vstupoch rastúcej veľkosti a dostane odhad
triedy zložitosti z merania. Cieľová skupina: študenti informatiky, ktorí sa učia algoritmy.

Kontrakt systému: [CONTRACT.md](CONTRACT.md). Kompletný stack: [docs/frontend.md](docs/frontend.md)
a [docs/backend.md](docs/backend.md). Zmeny rozšírenia pre text práce:
[docs/ZMENY-rozsirenie.md](docs/ZMENY-rozsirenie.md). Spustenie: [docs/RUN.md](docs/RUN.md).

## Architektúra

```
frontend/   React 19, TypeScript, Vite 8, Tailwind 4 (cez PostCSS), Recharts, Monaco
backend/    FastAPI, SQLAlchemy 2, Pydantic 2, katalóg úloh v app/catalog
runner/     sandbox: tracker, statická kontrola, spustenie v samostatnom procese
api/        vstupný bod Vercel funkcie pre backend
```

- Kód používateľa: `solve(data[, tracker])`, `generate(n, **params)`, `check(input, output, expected=None)`.
- Tracker (`runner/algolab_sandbox/tracker.py`) zaznamenáva kroky pre vizualizáciu a počíta
  operácie. Pri meraní kroky nezaznamenáva.
- Experiment beží po dávkach: `POST /start`, potom opakovane `POST /step`.
- Pri nasadení beží runner ako samostatný Vercel projekt bez prístupu k databáze.

## Príkazy

Backend (Windows):

```
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
python catalog_test.py         # overí všetky algoritmy katalógu
python smoke_test.py           # test API
```

Frontend (Windows, Node 24: `npm run dev` nefunguje, použi .cmd):

```
cd frontend
node_modules\.bin\vite.cmd     # http://localhost:5173, /api ide na port 8000
npm run build
npm run lint
```

## Pravidlá

- Tailwind v4 len cez `@tailwindcss/postcss`. Plugin `@tailwindcss/vite` nefunguje s Vite 8.
- Vlastné základné štýly v `src/index.css` patria do `@layer base`, inak prebijú utility.
- Farby sú tokeny v `src/index.css` (`--ground`, `--surface`, `--ink`, `--accent`, roly
  `--role-*`, paleta grafov `--series-1` až `--series-8`). Žiadne priame hex hodnoty v komponentoch.
- Farba v rozhraní patrí dátam a stavom. Paleta grafov má pevné poradie, farba patrí algoritmu.
- Texty v rozhraní sú po slovensky, krátko a vecne.
- Po zmene katalógu spusti `python catalog_test.py <id_úlohy>`.
- Po zmene modelu zvýš `SCHEMA_VERSION` v `backend/app/models.py`.
- Skilly na dizajn rozhrania sú v `.claude/skills` (impeccable, taste-skill, interface-design, playwright-cli).
- Aplikácia sa nesmie odvolávať na konkrétny predmet (žiadne cvičenia ani skratky predmetov).
- Názvy algoritmov a techník (divide and conquer, greedy, dynamic programming) sú anglické, popisy po slovensky.
- Logo sú obrázky PNG v `frontend/public/brand/` (svetlý a tmavý variant), vkladá ich `frontend/src/components/Logo.tsx`.
