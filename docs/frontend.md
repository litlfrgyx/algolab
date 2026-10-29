# Frontend AlgoLab

Kompletný prehľad technológií a štruktúry webového rozhrania. Verzie sú tie, ktoré
sú nainštalované podľa `frontend/package-lock.json` (stav k 29. 10. 2026).

## Stack

| Oblasť | Technológia | Verzia | Na čo slúži |
|---|---|---|---|
| Jazyk | TypeScript | 6.0.3 | typová kontrola celého rozhrania (`tsc -b` pred buildom) |
| UI knižnica | React a React DOM | 19.2.5 | komponenty, stav, lazy načítanie stránok |
| Smerovanie | React Router DOM | 7.14.1 | adresy stránok, filtre uložené v URL |
| Build a dev server | Vite | 8.0.8 | vývojový server, proxy na API, produkčný balík |
| Plugin pre React | @vitejs/plugin-react | 6.0.1 | JSX a rýchle obnovenie pri vývoji |
| Štýly | Tailwind CSS | 4.2.2 | utility triedy |
| Integrácia Tailwindu | @tailwindcss/postcss, PostCSS, Autoprefixer | 4.2.2, 8.5.10, 10.5.0 | spracovanie CSS cez PostCSS |
| Grafy | Recharts | 3.8.1 | čiarové grafy výsledkov experimentov |
| Editor kódu | Monaco Editor, @monaco-editor/react | 0.52.2, 4.7.0 | editor Pythonu so zvýraznením syntaxe |
| Ikony | lucide-react | 1.8.0 | ikony v rozhraní |
| Písmo | IBM Plex Sans, IBM Plex Mono (Google Fonts) | | text a kód, so slovenskou diakritikou (`latin-ext`) |
| Lint | ESLint, typescript-eslint, eslint-plugin-react-hooks, eslint-plugin-react-refresh | 9.39.4, 8.58.2, 7.1.1, 0.5.2 | kontrola kódu (`npm run lint`) |

Vizualizácie (pole, tabuľka, graf, strom, text) nepoužívajú žiadnu ďalšiu knižnicu.
Sú to vlastné komponenty, ktoré kreslia SVG a HTML priamo z krokov, ktoré vráti API.
Rozloženie grafu aj stromu počíta aplikácia sama.

## Dôležité rozhodnutia

- **Tailwind v4 cez PostCSS.** Plugin `@tailwindcss/vite` s Vite 8 nefunguje, preto
  `postcss.config.js` obsahuje `@tailwindcss/postcss` a `autoprefixer`.
- **Vlastné základné štýly sú v `@layer base`** v `src/index.css`. Mimo vrstvy by
  prebili utility triedy Tailwindu (napríklad okraje).
- **Monaco je súčasťou balíka.** Nenačítava sa z CDN, takže editor funguje aj
  v sieti, ktorá CDN blokuje. Načíta sa len jazyk Python a jeden web worker.
  Editor sa načíta až na stránke, ktorá ho potrebuje.
- **API je na tej istej adrese ako stránka (`/api`).** Pri vývoji ho presmeruje
  proxy vo `vite.config.ts` na `http://127.0.0.1:8000` (dá sa zmeniť premennou
  `VITE_API_PROXY`). Po nasadení ho presmeruje Vercel. CORS preto netreba riešiť.
- **Stránky sa načítavajú lenivo** (`React.lazy`). Úvodná stránka je v hlavnom
  balíku, ostatné sa stiahnu až pri prvej návšteve.
- **Žiadna knižnica na správu stavu.** Stav drží React, dáta sa načítavajú cez
  vlastný hook `useAsync`. Filtre zoznamov sú v parametroch URL, aby sa dali
  zdieľať odkazom.

## Vizuálny systém

Všetky farby sú tokeny v `src/index.css`. Komponenty nepoužívajú priame hex hodnoty.

- **Plochy a text:** `--ground`, `--surface`, `--surface-2`, `--surface-3`, `--line`,
  `--line-strong`, `--ink`, `--ink-2`, `--ink-3`.
- **Akcent:** `--accent` (#1e5aa8 vo svetlej téme, #6aaee8 v tmavej), `--accent-soft`.
- **Roly vo vizualizácii**, rovnaké vo všetkých piatich zobrazeniach: porovnanie
  (`--role-compare`), výmena (`--role-swap`), pivot (`--role-pivot`), aktívny prvok
  (`--role-active`), hotovo (`--role-done`), navštívené (`--role-visited`).
- **Stavy:** `--ok`, `--warn`, `--bad`.
- **Paleta grafov** `--series-1` až `--series-8` má pevné poradie. Farba patrí
  algoritmu, takže ten istý algoritmus má rovnakú farbu na dlaždici experimentu,
  v grafe aj v legende.
- **Tmavá téma** sa zapne podľa `prefers-color-scheme`. Dá sa vynútiť atribútom
  `data-theme` na koreňovom prvku.
- **Logo** je obrázok PNG v `public/brand/` v dvoch variantoch (svetlý a tmavý).
  Komponent `components/Logo.tsx` vloží oba a CSS triedy `theme-light` a
  `theme-dark` zobrazia ten, ktorý zodpovedá téme. `favicon.svg` obsahuje obe
  ikony a prepína ich tiež podľa témy.

Pri návrhu rozhrania sa použili skilly z `.claude/skills`: impeccable, taste-skill,
interface-design a playwright-cli (kontrola stránok v prehliadači).

## Štruktúra

```
frontend/
  index.html            písma, favicony, koreňový prvok
  vite.config.ts        plugin React, proxy /api
  postcss.config.js     Tailwind 4 a Autoprefixer
  eslint.config.js      pravidlá lintu
  public/
    favicon.svg
    brand/              logo, značka a nápis vo svetlom a tmavom variante, ikony
  src/
    main.tsx            vstupný bod
    App.tsx             smerovanie a lazy načítanie stránok
    api.ts              klient REST API, heslo na úpravy v localStorage
    types.ts            typy dát z API
    index.css           tokeny, témy, základné štýly
    lib/
      auth.tsx          kontext pre heslo na úpravy (EditAuthProvider)
      hooks.ts          useAsync, useStoredState
      labels.ts         slovenské a anglické popisy, témy, formátovanie čísel
    components/
      Layout.tsx        bočná navigácia, rozloženie, pätička
      Logo.tsx          logo pre svetlú a tmavú tému
      ui.tsx            Button, Input, Select, Tag, Notice, Panel, Segmented, PageHeader, Skeleton, Empty
      AlgorithmTile.tsx dlaždica algoritmu
      AlgorithmTable.tsx
      ComplexityLadder.tsx  rebrík tried zložitosti
      ResultsChart.tsx  graf výsledkov, paleta seriesColor
      StatusTag.tsx     stav experimentu
      CodeView.tsx      zobrazenie kódu so zvýraznením aktuálneho riadku
      CodeEditor.tsx, MonacoEditor.tsx  editor kódu
      ParamsForm.tsx    formulár parametrov generátora
      viz/
        StepView.tsx    výber zobrazenia podľa typu kroku, legenda rolí
        ArrayView.tsx   pole
        GridView.tsx    tabuľka (dynamic programming)
        GraphView.tsx   graf, rozloženie vrcholov, front a zásobník
        TreeView.tsx    strom
        StringView.tsx  text a vzorka
        roles.ts        mapovanie rolí na tokeny farieb
    pages/              stránky (pozri nižšie)
```

## Stránky

| Adresa | Stránka | Obsah |
|---|---|---|
| `/` | Landing | úvod, živá ukážka piatich zobrazení (pole, tabuľka, graf, strom, text) so skutočnými krokmi z API, ukážka experimentu, prehľad tém |
| `/problems` | Problems | úlohy ako dlaždice zoskupené podľa tém |
| `/problems/:id` | ProblemDetail | zadanie, vstup a výstup, algoritmy a generátory úlohy |
| `/problems/:id/new` | NewAlgorithm | nový vlastný algoritmus |
| `/algorithms` | Algorithms | algoritmy ako dlaždice, filtre v URL |
| `/algorithms/:id` | AlgorithmDetail | kód, zložitosť, vlastnosti, duplikovanie vstavaného algoritmu |
| `/generators/:id` | GeneratorDetail | kód generátora, parametre, náhľad vstupu |
| `/visualizer` | Visualizer | prehrávanie krokov, rýchlosť, ovládanie šípkami, kód s aktuálnym riadkom |
| `/experiments` | Experiments | dlaždice experimentov s farbami algoritmov, hľadanie, filter tém, priama akcia |
| `/experiments/new` | ExperimentNew | výber úlohy, algoritmov, generátora, veľkostí a variantov vstupu |
| `/experiments/:id` | ExperimentDetail | priebeh po dávkach, graf (operácie alebo čas, logaritmická alebo lineárna mierka), odhad zložitosti, export CSV a JSON |
| `/guide` | Guide | návod na písanie vlastného kódu a použitie trackera |

## Príkazy

Na Windows s Node 24 `npm run dev` nefunguje, preto sa dev server spúšťa priamo:

```
cd frontend
npm ci
node_modules\.bin\vite.cmd      http://localhost:5173, /api ide na port 8000
npm run build                   tsc -b a vite build do frontend/dist
npm run lint
```

## Nasadenie

Frontend je súčasťou hlavného projektu na Verceli (`vercel.json` v koreni repozitára).
Vercel spustí `cd frontend && npm ci` a `npm run build` a zverejní `frontend/dist`.
Požiadavky na `/api/*` presmeruje na Python funkciu backendu, všetky ostatné adresy
(okrem `/assets/`) na `index.html`, aby fungovalo smerovanie v prehliadači. Každý push
do vetvy `main` na GitHube spustí nové nasadenie. Verejná adresa:
https://algolab-kpi.vercel.app
