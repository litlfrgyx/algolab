# Backend AlgoLab

Kompletný prehľad technológií a štruktúry serverovej časti. Backend tvoria dve
samostatné služby: **API** (FastAPI s databázou) a **runner** (sandbox, ktorý
spúšťa kód používateľa a nemá prístup k databáze). Verzie sú pripnuté v
`backend/requirements.txt` a `requirements.txt` (stav k 29. 10. 2026).

## Stack

| Oblasť | Technológia | Verzia | Na čo slúži |
|---|---|---|---|
| Jazyk | Python | 3.12 na Verceli (`.python-version`), 3.13 v Dockeri | celý backend aj runner |
| Webový framework | FastAPI (nad Starlette) | 0.115.6 (Starlette 0.41.3) | REST API, validácia, OpenAPI dokumentácia na `/docs` |
| ASGI server | Uvicorn | 0.34.0 | lokálny vývoj a Docker |
| ORM | SQLAlchemy | 2.0.36 | modely, dotazy, vytvorenie tabuliek |
| Validácia a schémy | Pydantic | 2.10.4 | vstupy a výstupy API |
| Ovládač Postgresu | psycopg (binary) | 3.2.3 | pripojenie k Supabase |
| Databáza lokálne | SQLite | súčasť Pythonu | súbor `backend/algoanalyzer.db` |
| Databáza po nasadení | PostgreSQL (Supabase) | | schéma `algolab`, rola `algolab_app` |
| HTTP klient v testoch | httpx | 0.28.1 | len `smoke_test.py` a `experiments_report.py` |
| Hosting | Vercel Python Functions | | API aj runner ako serverless funkcie |
| Kontajner (voliteľne) | Docker, docker compose | | lokálny beh s limitmi sandboxu na Linuxe |

Runner nemá žiadne závislosti mimo štandardnej knižnice Pythonu (`subprocess`,
`resource`, `ast`, `json`, `http.server`). Odhad zložitosti tiež nepoužíva NumPy
ani SciPy, metóda najmenších štvorcov je napísaná priamo.

## Architektúra

```
prehliadač
   │  /api/*
   ▼
API (Vercel projekt algolab, api/index.py → backend/app)
   │  SQLAlchemy                 │  HTTP POST /api/run, hlavička X-Runner-Token
   ▼                             ▼
Supabase Postgres           runner (Vercel projekt algolab-runner)
schéma algolab              nový proces Pythonu pre každé spustenie
```

- API kód používateľa nikdy nespúšťa samo, ak je nastavené `RUNNER_URL`. Úlohu
  pošle runneru a ten vráti výsledok, kroky vizualizácie a počty operácií.
- Bez `RUNNER_URL` (lokálny vývoj) volá API ten istý balík `runner/algolab_sandbox`
  priamo, takže sa správa rovnako.
- Experiment beží po dávkach: `POST /api/experiments/{id}/start` a potom opakovane
  `POST /api/experiments/{id}/step`. Jedna dávka spracuje toľko prípadov, koľko sa
  zmestí do 15 sekúnd (`STEP_BUDGET_S`). Serverless funkcia tak nikdy nebeží dlho
  a nedrží otvorené spojenie (preto nie WebSocket).

## Štruktúra

```
api/index.py                 vstupný bod Vercel funkcie, importuje backend/app/main.py
requirements.txt             závislosti pre Vercel
vercel.json                  build frontendu, funkcia api/index.py (maxDuration 60 s), presmerovania
backend/
  app/
    main.py                  FastAPI aplikácia, CORS, inicializácia databázy raz za proces
    config.py                nastavenia z premenných prostredia
    db.py                    engine, schéma v Postgrese, NullPool pre pooler Supabase
    models.py                tabuľky, SCHEMA_VERSION
    schemas.py               Pydantic schémy API
    seed.py                  naplnenie vstavaného katalógu, verzia katalógu ako hash
    deps.py                  heslo na úpravy, zákaz zmeny vstavaných položiek, kontrola kódu
    executor.py              experiment po dávkach, prípady, reprodukovateľný seed
    tracker.py               opis kontraktu trackera (Protocol) pre autorov algoritmov
    analysis/complexity.py   odhad triedy zložitosti z meraní
    sandbox/runner.py        výber medzi lokálnym spustením a vzdialeným runnerom
    routers/                 problems, algorithms, generators, experiments, visualize
    catalog/                 vstavaný katalóg úloh (basics, dp, structures, trees,
                             sorting, graphs, sets, extra, common)
  catalog_test.py            overí všetky algoritmy katalógu
  smoke_test.py              test API od začiatku po export
  experiments_report.py      spustí pripravené experimenty a zapíše docs/OVERENIE-zlozitosti.md
  Dockerfile, docker-compose.yml
runner/
  api/index.py               HTTP handler runnera na Verceli, overenie tokenu
  vercel.json                funkcia runnera (maxDuration 60 s)
  algolab_sandbox/
    safety.py                statická kontrola kódu (AST)
    execute.py               spustenie v novom procese s prázdnym prostredím a timeoutom
    child.py                 kód bežiaci v detskom procese: generate, solve, check, meranie
    limits.py                limit procesora a pamäte cez setrlimit
    tracker.py               implementácia trackera (kroky a počty operácií)
```

## Dátový model

Tabuľky v `models.py`. Po zmene modelu treba zvýšiť `SCHEMA_VERSION` (teraz `3`).

| Tabuľka | Obsah |
|---|---|
| `meta` | verzia schémy a verzia vstavaného katalógu |
| `problems` | úloha: názov, popis, kategória, typ vstupu, druh zobrazenia (`renderer`), referenčný algoritmus, kód kontroly (`checker_code`) |
| `algorithms` | algoritmus úlohy: kód, paradigma, zložitosť v najlepšom, priemernom a najhoršom prípade, pamäťová zložitosť, vlastnosti, podpora vizualizácie |
| `generators` | generátor vstupov: kód, predvolené veľkosti, veľkosť pre vizualizáciu, opis parametrov |
| `experiments` | experiment: úloha, algoritmy, generátor, veľkosti, opakovania, timeout, seed, varianty vstupu, stav a priebeh |
| `experiment_runs` | jedno meranie: algoritmus, variant, veľkosť, opakovanie, čas, pamäť, počty operácií, správnosť, chyba |

Vstavané položky majú `is_builtin = true`, cez API sa nedajú meniť ani mazať a dajú sa
duplikovať. Pri štarte `seed.py` porovná hash katalógu s hodnotou v `meta` a ak sa
katalóg zmenil, vstavané položky aktualizuje. Vlastné položky používateľov ostanú.

Aktuálny katalóg: 27 úloh, 85 algoritmov, 27 generátorov, 34 pripravených experimentov.
Druhy zobrazenia: `array`, `grid`, `graph`, `tree`, `string` a `none` (úlohy bez vizualizácie).

## Kontrakt kódu používateľa

- Algoritmus: `solve(data)` alebo `solve(data, tracker)`.
- Generátor: `generate(n, **params)`.
- Kontrola výsledku: `check(input, output, expected=None)`.

Tracker ponúka metódy pre každé zobrazenie. Všeobecné sú `count`, `step`, `snapshot`,
`highlight` a `pointer`. Pre pole `array`, `compare`, `swap`, `set`, `pivot` a
`mark_sorted`, pre tabuľku `grid`, `set_cell` a `read_cell`, pre graf `graph`, `visit`,
`edge`, `relax`, `node_label`, `node_role` a `frontier`, pre strom `tree`, `tree_arrays`,
`focus` a `mark_node` a pre text `string`, `match`, `mismatch`, `shift` a `found`.
Pri meraní tracker kroky nezaznamenáva a len počíta operácie, aby meranie nespomaľoval.
Podrobný opis je v [CONTRACT.md](../CONTRACT.md).

## Bezpečnosť spúšťania kódu

Ochrana má viac vrstiev, lebo statická kontrola sa dá obísť.

1. **Statická kontrola** (`safety.py`) pred uložením aj pred spustením odmietne
   importy modulov s prístupom k súborom, sieti a procesom (`os`, `sys`, `subprocess`,
   `socket` a ďalšie), volania `eval`, `exec`, `open`, `__import__`, `getattr` a
   prístup k interným atribútom interpretera.
2. **Samostatný proces** pre každé spustenie s prázdnym prostredím, takže kód nevidí
   heslá ani premenné servera.
3. **Limity:** timeout procesu (predvolene 5 s, najviac 10 s), na Linuxe limit
   procesora a pamäte 512 MB cez `setrlimit`, limit hĺbky rekurzie 20 000.
4. **Oddelený runner** pri nasadení. Je to samostatný Vercel projekt, ktorý pozná len
   `RUNNER_TOKEN` a nemá prístup k databáze. Token sa porovnáva cez `hmac.compare_digest`.
5. **Heslo na úpravy** (`EDIT_PASSWORD`). Ak je nastavené, vytváranie a úprava kódu
   vyžaduje hlavičku `X-Edit-Password`.

## Meranie a odhad zložitosti

- Čas sa meria vnútri detského procesu, takže štart interpretera sa nezapočíta.
- Pamäť sa odhaduje z maxima rezidentnej pamäte procesu (`ru_maxrss`). `tracemalloc`
  sa nepoužíva, lebo výrazne skresľoval čas.
- Seed prípadu je seed experimentu plus index opakovania. Všetky algoritmy v prípade
  dostanú rovnaký vstup a beh sa dá zopakovať.
- `analysis/complexity.py` pre každú kandidátnu triedu (O(1), O(log log n), O(log n),
  O(n), O(n log n), O(n²), O(n³), O(φⁿ), O(2ⁿ), O(3ⁿ)) nájde metódou najmenších štvorcov
  priamku y ≈ a·g(n) + b a vyberie triedu s najmenšou normalizovanou chybou. Doplnkom je
  exponent zo sklonu v log-log súradniciach. Výsledok má istotu vysokú, strednú alebo
  nízku. Odhad sa robí zvlášť pre počet operácií a pre čas. Exponenciálne triedy sa
  skúšajú len pre n ≤ 60. Postup vychádza z Goldsmith, Aiken, Wilkerson (ESEC/FSE 2007).

## API

Všetky adresy začínajú `/api`. Interaktívna dokumentácia je na `/docs`.

| Oblasť | Endpointy |
|---|---|
| Stav | `GET /health`, `GET /info` (počty, limity, či je zapnuté heslo a vzdialený runner) |
| Úlohy | `GET /problems`, `POST /problems`, `GET`, `PUT`, `DELETE /problems/{id}` |
| Algoritmy | `GET /algorithms`, `GET`, `POST /problems/{id}/algorithms`, `GET`, `PUT`, `DELETE /algorithms/{id}`, `POST /algorithms/{id}/duplicate` |
| Generátory | `GET /generators`, `GET`, `POST /problems/{id}/generators`, `GET`, `PUT`, `DELETE /generators/{id}`, `POST /generators/{id}/duplicate`, `POST /generators/{id}/preview`, `POST /generators/preview-code` |
| Vizualizácia | `POST /visualize` (kroky pre prehrávanie), `POST /code/validate` |
| Experimenty | `GET`, `POST /experiments`, `GET`, `DELETE /experiments/{id}`, `POST .../start`, `POST .../step`, `POST .../run`, `POST .../cancel`, `GET .../runs`, `GET .../results`, `GET .../export?format=csv` alebo `json` |

## Premenné prostredia

| Premenná | Predvolená hodnota | Význam |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./algoanalyzer.db` | pripojenie k databáze, po nasadení Postgres cez pooler Supabase |
| `DB_SCHEMA` | `algolab` | schéma v Postgrese |
| `CORS_ORIGINS` | localhost porty 5173, 5174, 5180 | povolené pôvody pri vývoji |
| `RUNNER_URL`, `RUNNER_TOKEN` | prázdne | adresa a token vzdialeného runnera |
| `EDIT_PASSWORD` | prázdne | heslo na úpravy vlastného kódu |
| `SANDBOX_TIMEOUT_MS`, `SANDBOX_MAX_TIMEOUT_MS` | 5000, 10000 | timeout jedného spustenia |
| `STEP_BUDGET_S` | 15 | čas na jednu dávku experimentu |
| `MAX_ALGORITHMS` | 8 | najviac algoritmov v experimente (toľko farieb má paleta grafov) |

Heslá a tokeny sú len v premenných prostredia na Verceli, nie v repozitári.

## Pripojenie k Supabase

- Pooler `aws-0-eu-west-1.pooler.supabase.com:6543` v transakčnom režime.
- Na strane aplikácie `NullPool`, lebo spojenia drží pooler a serverless funkcia
  nemá dlho žijúci pool.
- `prepare_threshold=None`, lebo transakčný pooler nepodporuje pripravené dotazy.
- Tabuľky sú v schéme `algolab` (cez `schema_translate_map`), takže nezasahujú do
  iných dát projektu. Rola `algolab_app` má práva len na túto schému.

## Testy

```
cd backend
python catalog_test.py [id_úlohy]   všetky algoritmy katalógu na viacerých vstupoch (3517 kontrol)
python smoke_test.py                API od vytvorenia po export (50 kontrol), aj proti Postgresu
python experiments_report.py        overenie odhadu zložitosti, výstup docs/OVERENIE-zlozitosti.md
```

## Spustenie

Lokálne na Windows:

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

V Dockeri (Linux, tu reálne platia limity procesora a pamäte):

```
docker compose -f backend/docker-compose.yml up --build
```

## Nasadenie

| Časť | Adresa a nastavenie |
|---|---|
| Aplikácia a API | https://algolab-kpi.vercel.app, Vercel projekt `algolab`, funkcia `api/index.py` |
| Runner | https://algolab-runner.vercel.app, Vercel projekt `algolab-runner`, koreň `runner/` |
| Región funkcií | `dub1` (Dublin), blízko databázy |
| Databáza | Supabase projekt v `eu-west-1`, schéma `algolab`, rola `algolab_app` |

Oba Vercel projekty sú prepojené s repozitárom `litlfrgyx/algolab` na GitHube. Každý push
do vetvy `main` ich nasadí znova. Podrobný postup je v [RUN.md](RUN.md).
