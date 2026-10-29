# Frontend AlgoLab

React 19, TypeScript, Vite 8, Tailwind 4 (cez PostCSS), Recharts, Monaco (zabalený v aplikácii, bez CDN).

```
src/
  api.ts                 klient REST API, heslo na úpravy v hlavičke X-Edit-Password
  types.ts               typy zodpovedajúce backend/app/schemas.py
  index.css              farebné tokeny pre svetlú a tmavú tému, základné štýly
  lib/                   popisy pre rozhranie, hooky, kontext odomknutia úprav
  components/
    ui.tsx               tlačidlá, polia, panely, hlásenia
    ComplexityLadder.tsx rebrík zložitosti (deklarovaná trieda a odhad z merania)
    ResultsChart.tsx     graf výsledkov experimentu
    viz/                 zobrazenia krokov: pole, tabuľka, graf, strom, text
  pages/                 úlohy, algoritmy, vizualizácia, experimenty, príručka
```

Spustenie na Windows (Node 24): `node_modules\.bin\vite.cmd`. Vite presmeruje `/api` na
`http://127.0.0.1:8000`, iný backend sa nastaví premennou `VITE_API_PROXY`.

Kontrola: `npm run build` a `npm run lint`.
