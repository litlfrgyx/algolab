# Fáza 0 — narovnanie základov

Cieľ Fázy 0: zaviesť typovú + dátovú vrstvu za rozhraním, prepojiť vlajkovú
funkciu na kontrakt a spraviť projekt buildovateľným. Backend sa zatiaľ
nestavia — dáta poskytuje `MockApiClient`.

Súvisí s: [`../CONTRACT.md`](../CONTRACT.md) (kontrakt) a recenziou frontendu.

## Hotovo

- [x] **Kontrakt** — `frontend/src/types/` (`domain`, `steps`, `api`) + Pydantic
      zrkadlo `backend/app/schemas.py` + `tracker.py`. Pozri `CONTRACT.md`.
- [x] **Dátová vrstva** — `frontend/src/api/` (`MockApiClient implements ApiClient`,
      seed dáta, tracery, generátor). Pozri `frontend/src/api/README.md`.
- [x] **Visualizer prepojený na kontrakt** — konzumuje `api.visualize()` →
      `VisualizationTrace`; generický renderer riadený `highlights` + `pointers`
      + `ROLE_COLOR`. Odstránené klientske `computeBubble/computeQuick`
      (architektonická oprava: vizualizér je nezávislý od algoritmu).
      Pridané: počty operácií v hlavičke panela, zvýraznenie riadku kódu
      (`code_line`), strop veľkosti vstupu (`MAX_VIZ_N`), ošetrenie záporných
      hodnôt, stav „načítavam".
- [x] **Opravené bugy** — `bfs.py` zobrazoval BubbleSort (teraz reálny BFS);
      nepoužité importy (`motion`, `AnimatePresence`, `i`) → build je zelený.
- [x] **Build overený** — `tsc --noEmit` exit 0, `vite build` exit 0.

## Stránky prepojené na `api` (hotovo)

Všetkých 5 stránok teraz ťahá dáta z dátovej vrstvy (žiadne hardcoded `const`):

- [x] **Problems** — `api.listProblems()` + reálne počty algoritmov/generátorov, loading stav
- [x] **Algorithms** — `api.listAlgorithms('prob_sorting')`; reálne sorting algoritmy
      s `solve(data, tracker)` (namiesto grafových demo súborov); inšpektor podľa
      zvoleného algoritmu; „Spustiť vizualizér" navigujе na `/visualizer`
- [x] **Generator** — `api.previewGenerator()`; živý náhľad reaguje na n / mód / seed
- [x] **Experiments** — `api.getExperiment()` + `getResults()`; reálne namerané časy
      a počty porovnaní per (algoritmus × veľkosť)
- [x] **Results** — `api.getResults()`; 3 grafy (čas, **počet porovnaní**, pamäť),
      tabuľka min/avg/max, stav korektnosti, **funkčný export CSV/JSON**

### Ešte v rámci Fázy 1 (nie iba wiring)

- [ ] **Experiment setup formulár** (zatiaľ sa zobrazuje seedovaný dokončený experiment)
- [ ] PNG export grafov (`canvas.toBlob`)
- [ ] Detail problému, tlačidlá „Nový problém / Algoritmus / Detail" (zatiaľ dekoratívne)

## Mimo Fázy 0 (ďalšie fázy)

- Fáza 1: chýbajúce moduly (Problem Detail, Experiment setup, korektnosť, error/timeout stavy)
- Fáza 2: grid + string renderer, výber dvojice algoritmov, **prediction režim**
- Fáza 3: komponentová knižnica namiesto inline štýlov, responzivita, prístupnosť, i18n

## Ako spustiť

```
cd frontend
node_modules\.bin\vite.cmd        # dev server (Windows / Node 24 — pozri CLAUDE.md)
npm run build                     # tsc -b && vite build
```
