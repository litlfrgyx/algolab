# Kontrakt systému AlgoLab

Rozhranie medzi kódom používateľa, sandboxom, API a frontendom. Implementácia:

- Pydantic schémy: [`backend/app/schemas.py`](backend/app/schemas.py)
- TypeScript typy: [`frontend/src/types.ts`](frontend/src/types.ts)
- Tracker (zaznamenáva kroky): [`runner/algolab_sandbox/tracker.py`](runner/algolab_sandbox/tracker.py)
- Vstavaný katalóg: [`backend/app/catalog/`](backend/app/catalog/)

## 1. Návrhové rozhodnutia

| # | Rozhodnutie | Dôvod |
|---|---|---|
| D1 | Formát JSON je snake_case na oboch stranách | Medzi Pydantic a TypeScriptom netreba prevod |
| D2 | Každý krok nesie úplný snímok stavu | Vizualizácia beží na malom vstupe, krokovanie vpred aj vzad je jednoduché |
| D3 | Počet operácií počíta tracker | Meranie nezávisí od hardvéru a rovnaký kód slúži na meranie aj vizualizáciu |
| D4 | Druh zobrazenia určuje pole `kind` v každom kroku | Frontend vyberie renderer jedným `switch` |
| D5 | Platí `solve(data)` aj `solve(data, tracker)` | Bez trackera sa algoritmus dá merať, s ním aj vizualizovať |
| D6 | Generátor aj experiment majú seed | Experiment sa dá zopakovať s rovnakými vstupmi |
| D7 | Kód používateľa beží v samostatnom procese a pri nasadení na samostatnom serveri bez hesiel | Chyba v sandboxe neodhalí databázu |
| D8 | Experiment beží po dávkach (`start` a opakované `step`) | Funguje rovnako lokálne aj v serverless prostredí bez dlhých spojení |

## 2. Dátový model

```
Problem 1───* Algorithm          (jeden môže byť referenčný)
   │     1───* InputGenerator
   │
   └──* Experiment  (algorithm_ids[], generator_id, sizes[], repeats, seed, generator_params, variants[])
            │
            └──* ExperimentRun  (algoritmus × variant × veľkosť × opakovanie: čas, pamäť, operácie, správnosť)
Meta  (schema_version, catalog_version)
```

Polia pridané pri rozšírení (podrobne v `docs/ZMENY-rozsirenie.md`):

- `Problem`: `summary`, `input_type`, `renderer`, `checker_code`, `tags`, `is_builtin`, `sort_order`
- `Algorithm`: `description`, `paradigm`, `complexity_time_best/avg/worst`, `complexity_space`,
  `complexity_note`, `complexity_param`, `properties`, `is_builtin`, `sort_order`
- `InputGenerator`: `description`, `viz_size`, `is_builtin`
- `Experiment`: `variants`, `total_cases`, `done_cases`, `is_builtin`
- `ExperimentRun`: `variant_index`, `variant_label`, `check_message`

Vstavané záznamy (`is_builtin = true`) sa nedajú meniť ani mazať. Tlačidlo Duplikovať vytvorí
upraviteľnú kópiu.

## 3. Kód používateľa

### Algoritmus

```python
def solve(data, tracker):
    ...
    return vysledok
```

### Generátor vstupov

```python
def generate(n, **params):     # params obsahuje aj seed
    ...
    return vstup
```

Parametre generátora popisuje `param_spec` (typ `enum`, `number` alebo `boolean`, popisy
hodnôt v `option_labels`). Neznáme parametre sa funkcii neodovzdajú.

### Kontrola správnosti

```python
def check(input, output, expected=None):
    return True                      # alebo (False, "správa pre študenta")
```

`expected` je výsledok referenčného algoritmu na tom istom vstupe. Ak úloha nemá `check`,
výstup sa porovná s `expected`. Algoritmus s vlastnosťou `intentionally_incorrect` slúži
na ukážku, že kontrola chybu odhalí.

### Obmedzenia sandboxu

- statická kontrola (AST): zakázané moduly `os`, `sys`, `subprocess`, `socket`, `importlib`
  a ďalšie, funkcie `eval`, `exec`, `open`, `getattr`, `__import__` a atribúty s dvoma
  podčiarkovníkmi okrem bezpečných
- samostatný proces s prázdnym prostredím, časový limit, na Linuxe limit pamäte a CPU
- výstup `print` sa zachytí a vráti v poli `stdout`
- prenos cez JSON: n-tice sa zmenia na zoznamy, kľúče slovníka na reťazce

## 4. Tracker

| Skupina | Metódy |
|---|---|
| meranie | `count(nazov, k=1)` |
| všeobecné | `step(typ, payload)`, `snapshot(label)`, `highlight(indexy, rola)`, `pointer(meno, index)` |
| pole | `array(pole, labels)`, `compare(i, j)`, `swap(i, j)`, `set(i, hodnota)`, `pivot(i)`, `mark_sorted(indexy)` |
| tabuľka | `grid(r, s, row_labels, col_labels, fill)`, `set_cell(r, s, hodnota, role)`, `read_cell(r, s)` |
| graf | `graph(n, hrany, directed, weighted)`, `visit(v)`, `edge(u, v, rola)`, `relax(u, v, hodnota)`, `node_label(v, text)`, `node_role(v, rola)`, `frontier(prvky, meno)` |
| strom | `tree(koreň, label, extra)`, `tree_arrays(values, left, right, root)`, `focus(id, rola)`, `mark_node(id, rola)`, `clear_marks()` |
| text | `string(text, vzorka)`, `match(i, j)`, `mismatch(i, j)`, `shift(posun)`, `found(i)` |

Všetky metódy, ktoré vytvárajú krok, majú voliteľný `label` a `code_line`. Pri meraní
(`max_steps = 0`) tracker kroky nezaznamenáva, len počíta operácie, a snímky stromu ani
obsah frontu nekopíruje.

Roly zvýraznenia: `compare`, `swap`, `pivot`, `active`, `match`, `sorted`, `visited`,
`tree`, `path`.

## 5. Krok vizualizácie

Spoločné polia: `kind`, `index`, `type`, `label`, voliteľne `code_line`.

| kind | Ďalšie polia |
|---|---|
| `array` | `array`, `highlights[{index, role}]`, `pointers{meno: index}`, `labels[]` |
| `grid` | `grid[][]`, `highlights[{row, col, role}]`, `row_labels`, `col_labels` |
| `graph` | `node_roles{v: rola}`, `edge_roles[{u, v, role}]`, `labels{v: text}`, `frontier{name, items}` a štruktúra grafu v `trace.structure` |
| `tree` | `nodes[{id, label, children[], extra}]`, `root`, `highlights[{id, role}]` |
| `string` | `value`, `pattern`, `offset`, `highlights`, `pattern_highlights` |

Limity veľkosti vstupu pre vizualizáciu (`/api/info`, `viz_limits`): pole 60, tabuľka 15,
graf 25 vrcholov, strom 31 uzlov, text 80 znakov.

## 6. REST API

| Metóda a cesta | Účel |
|---|---|
| `GET /api/info` | počty, limity, či sú úpravy chránené heslom |
| `GET /api/problems`, `GET /api/problems/{id}` | katalóg úloh |
| `GET /api/algorithms`, `GET /api/problems/{id}/algorithms`, `GET /api/algorithms/{id}` | algoritmy |
| `POST /api/problems/{id}/algorithms`, `PUT`, `DELETE /api/algorithms/{id}`, `POST .../duplicate` | vlastné algoritmy |
| `GET /api/generators`, `GET /api/problems/{id}/generators`, `PUT`, `DELETE`, `POST .../duplicate` | generátory |
| `POST /api/generators/{id}/preview`, `POST /api/generators/preview-code` | náhľad vstupu |
| `GET`, `POST /api/experiments`, `GET`, `DELETE /api/experiments/{id}` | experimenty |
| `POST /api/experiments/{id}/start`, `POST .../step`, `POST .../cancel`, `POST .../run` | vykonanie |
| `GET /api/experiments/{id}/runs`, `GET .../results`, `GET .../export?format=csv\|json` | výsledky |
| `POST /api/visualize` | stopa krokov pre algoritmus a vstup |
| `POST /api/code/validate` | kontrola kódu bez spustenia |

Ak je nastavené `EDIT_PASSWORD`, vytváranie a úprava vlastného kódu a spustenie neuloženého
kódu vyžaduje hlavičku `X-Edit-Password`. Čítanie, vizualizácia vstavaných algoritmov
a experimenty sú verejné.

## 7. Výsledky a odhad zložitosti

`GET /api/experiments/{id}/results` vráti pre každý algoritmus a variant body
(priemer, minimum a maximum času, priemer operácií, počty chýb) a odhad:

- `operations` a `time`: najlepšia trieda, druhá trieda, normalizovaná chyba, exponent k
  z log-log regresie, istota `high`, `medium` alebo `low`
- `declared`, `declared_case`: deklarovaná trieda a prípad (najlepší, priemerný, najhorší),
  s ktorým sa odhad zhoduje
- `agreement`: `match`, `mismatch` alebo `unknown`

Postup je opísaný v `backend/app/analysis/complexity.py` a v `docs/ZMENY-rozsirenie.md`.
