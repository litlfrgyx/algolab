# Kontrakt systému — jediný zdroj pravdy

Tento dokument definuje rozhranie medzi **frontendom** (React/TS) a **backendom**
(FastAPI/Python). Je to prvý a najdôležitejší artefakt: pokiaľ platí, môžu obe
strany napredovať paralelne (frontend cez mock implementáciu `ApiClient`).

Implementačné zrkadlá:

- TypeScript typy: [`frontend/src/types/`](frontend/src/types/) — `domain.ts`, `steps.ts`, `api.ts`
- Pydantic schémy: [`backend/app/schemas.py`](backend/app/schemas.py)
- Kontrakt trackera (producent krokov): [`backend/app/tracker.py`](backend/app/tracker.py)

---

## 1. Návrhové rozhodnutia

| # | Rozhodnutie | Zdôvodnenie |
|---|-------------|-------------|
| D1 | **Drôtový formát je snake_case** na oboch stranách | Žiadna transformačná vrstva medzi Pydantic a TS → menej chýb |
| D2 | **Každý krok nesie plný snímok stavu** (nie delta) | Vizualizácia beží len pre malé `n` (~≤ 50); prehrávanie vpred/vzad je triviálne |
| D3 | **`operation_counts` je odvodené z počtu eventov trackera** | Jeden zdroj dát pre vizualizér aj meranie; hardvérovo nezávislá metrika (kap. 2.1.4) |
| D4 | **Renderer sa určuje raz na stope**, krok má diskriminant `kind` | Bezpečné zúženie typov v TS, jednoduchý `switch` na frontende |
| D5 | **`solve(data, tracker)` aj `solve(data)` sú platné** | Bez trackera funguje benchmark; tracker je voliteľný pre vizualizáciu |
| D6 | **Seed v generátore aj experimente** | Reprodukovateľnosť experimentov (opakovaná téma práce) |
| D7 | **Čas = ISO 8601 reťazec, ID = string** | Stabilné naprieč JSON; ID nezávisí od DB (UUID/slug) |

---

## 2. Dátový model (entity)

Podrobné polia: `domain.ts` / `schemas.py`. Prehľad vzťahov:

```
Problem 1───* Algorithm        (jeden z nich môže byť reference_algorithm)
   │     1───* InputGenerator
   │
   *
Experiment  (problem_id, algorithm_ids[], generator_id, sizes[], repeats, timeout_ms, seed)
   │
   1───* ExperimentRun  (algorithm_id × input_size × repeat_index → čas, pamäť, operation_counts, is_correct, status)
```

Kľúčové polia oproti pôvodnému návrhu (pridané):

- `Problem.category` + `Problem.reference_algorithm_id`
- `Algorithm.supports_visualization` (odvodené: volá kód `tracker`?)
- `InputGenerator.param_spec` (deklarácia parametrov pre formulár) + `default_sizes`
- `Experiment.seed`, `Experiment.generator_params`
- `ExperimentRun.operation_counts` (porovnania/výmeny…), `repeat_index`, `status` (ok/error/timeout)

---

## 3. REST endpointy

Base URL: `/api` · WebSocket: `/ws` · chyby: `{ "detail": "...", "code"?: "..." }`

### Problems
| Metóda | Cesta | Telo → Odpoveď |
|--------|-------|----------------|
| GET | `/api/problems` | → `Problem[]` |
| POST | `/api/problems` | `CreateProblemRequest` → `Problem` |
| GET | `/api/problems/{id}` | → `Problem` |
| PUT | `/api/problems/{id}` | `UpdateProblemRequest` → `Problem` |
| DELETE | `/api/problems/{id}` | → `204` |

### Algorithms
| Metóda | Cesta | Telo → Odpoveď |
|--------|-------|----------------|
| GET | `/api/problems/{problem_id}/algorithms` | → `Algorithm[]` |
| POST | `/api/problems/{problem_id}/algorithms` | `CreateAlgorithmRequest` → `Algorithm` |
| GET | `/api/algorithms/{id}` | → `Algorithm` |
| PUT | `/api/algorithms/{id}` | `UpdateAlgorithmRequest` → `Algorithm` |
| DELETE | `/api/algorithms/{id}` | → `204` |

### Generators
| Metóda | Cesta | Telo → Odpoveď |
|--------|-------|----------------|
| GET | `/api/problems/{problem_id}/generators` | → `InputGenerator[]` |
| POST | `/api/problems/{problem_id}/generators` | `CreateGeneratorRequest` → `InputGenerator` |
| GET | `/api/generators/{id}` | → `InputGenerator` |
| PUT | `/api/generators/{id}` | `UpdateGeneratorRequest` → `InputGenerator` |
| DELETE | `/api/generators/{id}` | → `204` |
| POST | `/api/generators/{id}/preview` | `GeneratorPreviewRequest` → `GeneratorPreviewResponse` |

### Experiments
| Metóda | Cesta | Telo → Odpoveď |
|--------|-------|----------------|
| GET | `/api/experiments` | → `Experiment[]` |
| POST | `/api/experiments` | `CreateExperimentRequest` → `Experiment` |
| GET | `/api/experiments/{id}` | → `Experiment` |
| DELETE | `/api/experiments/{id}` | → `204` |
| POST | `/api/experiments/{id}/run` | → `202` (priebeh cez WS) |
| POST | `/api/experiments/{id}/cancel` | → `202` |
| GET | `/api/experiments/{id}/runs` | → `ExperimentRun[]` |
| GET | `/api/experiments/{id}/results` | → `ExperimentResults` (agregované min/avg/max) |
| GET | `/api/experiments/{id}/export?format=csv\|json` | → súbor (CSV/JSON) |
| WS | `/ws/experiments/{id}` | server → klient: `ProgressMessage` |

> PNG export grafov je čisto klientský (`canvas.toBlob`), nepotrebuje endpoint.

### Vizualizácia + validácia
| Metóda | Cesta | Telo → Odpoveď |
|--------|-------|----------------|
| POST | `/api/visualize` | `VisualizeRequest` → `VisualizationTrace` |
| POST | `/api/code/validate` | `ValidateCodeRequest` → `ValidateCodeResponse` |

Split-screen porovnanie (dva algoritmy) = frontend zavolá `/api/visualize` dvakrát
na rovnakom vstupe (raz pre každý `algorithm_id`).

---

## 4. Schéma `Step` — jadro vizualizéra

Stopu (`VisualizationTrace`) produkuje `tracker`, konzumuje ju renderer na
frontende. `renderer` je na úrovni stopy; každý krok má `kind` pre zúženie typu.

Spoločné polia každého kroku: `index`, `type`, `label`, voliteľne `code_line`
(1-based riadok kódu na zvýraznenie). Roly zvýraznenia (`HighlightRole`):
`compare · swap · pivot · active · match · sorted · range · visited`.

### 4.1 Renderer `array` (sorting, vyhľadávanie, divide & conquer)

```json
{
  "kind": "array",
  "index": 12,
  "type": "swap",
  "label": "swap [2] ↔ [3]",
  "code_line": 6,
  "array": [3, 1, 4, 5, 2],
  "highlights": [
    { "index": 2, "role": "swap" },
    { "index": 3, "role": "swap" }
  ],
  "pointers": { "i": 2, "j": 3 }
}
```

### 4.2 Renderer `grid` (dynamické programovanie, matice, backtracking)

```json
{
  "kind": "grid",
  "index": 7,
  "type": "set",
  "label": "dp[1][2] = 1 (zhoda A==A)",
  "code_line": 9,
  "grid": [[0, 0, 0], [0, 1, null]],
  "highlights": [{ "row": 1, "col": 1, "role": "match" }],
  "row_labels": ["", "A"],
  "col_labels": ["", "A", "B"]
}
```

### 4.3 Renderer `string` (algoritmy na reťazcoch, vyhľadávanie vzoru)

```json
{
  "kind": "string",
  "index": 3,
  "type": "compare",
  "label": "text[3] vs pattern[1]",
  "value": "ABABCAB",
  "highlights": [{ "index": 3, "role": "compare" }],
  "pattern": "ABC",
  "pattern_highlights": [{ "index": 1, "role": "compare" }],
  "pointers": { "i": 3, "j": 1 }
}
```

Stopa potom vyzerá takto (skrátené):

```json
{
  "renderer": "array",
  "algorithm_id": "alg_bubble",
  "algorithm_name": "Bubble Sort",
  "input": [5, 3, 1, 4, 2],
  "steps": [ /* ... */ ],
  "operation_counts": { "compare": 10, "swap": 6 },
  "truncated": false,
  "max_steps": 2000
}
```

---

## 5. Kontrakt `tracker` (strana producenta)

Plné rozhranie: `backend/app/tracker.py`. Generická forma `tracker.step(type, payload)`
plus pohodlné skratky. Mapovanie skratiek na typy/roly krokov:

| Volanie trackera | `type` kroku | rola zvýraznenia |
|------------------|--------------|------------------|
| `tracker.compare(i, j)` | `compare` | `compare` |
| `tracker.swap(i, j)` | `swap` | `swap` |
| `tracker.pivot(i)` | `pivot` | `pivot` |
| `tracker.highlight(idx, role)` | `highlight` | podľa `role` |
| `tracker.mark_sorted(idx)` | `sorted` | `sorted` |
| `tracker.set_cell(r, c, v)` | `set` | `active`/zadaná |
| `tracker.match(i)` | `match` | `match` |
| `tracker.pointer(name, i)` | (upraví `pointers`) | — |

Executor po každom volaní doplní **plný snímok** aktuálneho `data` a po skončení
spočíta `operation_counts` z výskytov jednotlivých `type`. Tie isté počty putujú
aj do `ExperimentRun.operation_counts` → vizualizér a meranie zdieľajú zdroj dát.

---

## 6. Rozsah (čo kontrakt zámerne nerieši)

- **Grafové a rekurzívne algoritmy**: `CATEGORY_RENDERER` ich mapuje na `null`
  (benchmark áno, krok-za-krokom vizualizácia je budúce rozšírenie — kap. 3.1.3).
- **Multi-language**: `Algorithm.language` je zatiaľ pevne `"python"`, ale pole
  existuje pre budúce rozšírenie.
- **Bezpečnosť sandboxu**: kontrakt definuje len `status: error|timeout` a
  `error_message`; samotná izolácia (Docker, `setrlimit`) je vec executora.

---

## 7. Ďalší krok (Fáza 0)

1. `frontend/src/api/client.ts` — `MockApiClient implements ApiClient` (in-memory dáta).
2. Prepojiť stránky na `ApiClient` namiesto hardcoded `const` polí.
3. Backend „tenký vertikálny rez": jeden sorting problém, sandboxovaný executor
   pre jeden algoritmus, tracker → `/api/visualize` a `/api/experiments/{id}/run`.
