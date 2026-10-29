# Backend AlgoLab

FastAPI, SQLAlchemy 2, Pydantic 2. Kód používateľa spúšťa balík `runner/algolab_sandbox`.

```
app/
  main.py            aplikácia, CORS, inicializácia databázy
  config.py          premenné prostredia
  db.py              SQLite lokálne, PostgreSQL pri nasadení (schéma DB_SCHEMA, bez poolu)
  models.py          tabuľky, SCHEMA_VERSION
  schemas.py         kontrakt API (Pydantic)
  seed.py            vytvorenie databázy a doplnenie vstavaného katalógu
  deps.py            heslo na úpravy, ochrana vstavaných záznamov, kontrola kódu
  executor.py        experiment po dávkach (start, step)
  analysis/complexity.py   odhad triedy zložitosti z merania
  sandbox/runner.py  spustenie lokálne alebo na vzdialenom runneri (RUNNER_URL)
  catalog/           vstavané úlohy, algoritmy, generátory a experimenty
  routers/           problems, algorithms, generators, experiments, visualize
catalog_test.py      overenie celého katalógu
smoke_test.py        test API
experiments_report.py   tabuľka odhadu zložitosti pre všetky vstavané experimenty
```

## Premenné prostredia

| Premenná | Predvolená hodnota | Význam |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./algoanalyzer.db` | databáza |
| `DB_SCHEMA` | `algolab` | schéma v PostgreSQL |
| `RUNNER_URL` | prázdne | adresa vzdialeného runnera, prázdne znamená lokálne |
| `RUNNER_TOKEN` | prázdne | tajný token pre runner |
| `EDIT_PASSWORD` | prázdne | heslo na vlastný kód |
| `SANDBOX_TIMEOUT_MS` | 5000 | časový limit jedného behu |
| `SANDBOX_MAX_TIMEOUT_MS` | 10000 | najvyšší povolený limit |
| `STEP_BUDGET_S` | 15 | čas na jednu dávku experimentu |
| `MAX_ALGORITHMS` | 8 | najviac algoritmov v experimente |
| `CORS_ORIGINS` | localhost porty | povolené pôvody pri oddelenom frontende |

## Pridanie úlohy do katalógu

Úloha je slovník v niektorom súbore `app/catalog/*.py` so zoznamom algoritmov, generátorov
a experimentov. Po zmene stačí reštart, katalóg sa aktualizuje podľa odtlačku.
Potom spusti `python catalog_test.py <id_úlohy>`.
