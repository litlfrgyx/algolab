# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**ALGO_ANALYZER** — a diploma thesis web application for defining algorithm problems, implementing Python algorithms, running benchmarks, and visualizing execution step-by-step. Inspired by AlgaTor (algator.fri.uni-lj.si).

---

## Architecture

```
frontend/   React 18 + TypeScript + Vite 8 (SPA, currently all mock data)
backend/    FastAPI + SQLite + sandbox executor (not yet implemented)
```

Full-stack communication will use **REST API + WebSocket** (WebSocket only for experiment progress; the visualizer sends all steps at once and plays back locally on the frontend).

### Data flow for the Visualizer
1. User submits input array to backend
2. Backend runs the algorithm with a `tracker` object that records every step
3. All steps `[{type, payload, state_snapshot}]` are returned to frontend in one response
4. Frontend plays back steps locally (no streaming needed)

### Execution Engine (sandbox — not yet built)
- Runs inside Docker (Linux container) so `resource.setrlimit` is available
- Each algorithm run: `multiprocessing.Process` with CPU/memory limits + timeout
- Import blocking (`os`, `sys`, `subprocess`, `socket`, ...) as a secondary layer
- Primary security: Docker filesystem and network isolation

---

## Frontend

### Running the dev server

**IMPORTANT on Windows with Node v24 / npm 9:** `npm run dev` fails because the shell script wrapper breaks. Use the `.cmd` file directly:

```
cd frontend
node_modules\.bin\vite.cmd
```

Or with a specific port:

```
node_modules\.bin\vite.cmd --port 5174
```

Other commands work normally:

```
npm run build     # tsc -b && vite build
npm run lint      # eslint
npm run preview   # preview production build
```

### Tech stack (frontend)

| Package | Purpose |
|---|---|
| React 18 + TypeScript | UI framework |
| Vite 8 | Build tool |
| Tailwind CSS v4 | Utility classes (via PostCSS, NOT the Vite plugin) |
| React Router v6 | Client-side routing |
| Framer Motion | Page transitions + bar animations |
| `@monaco-editor/react` | Python code editor (VS Code engine) |
| Recharts | Performance line charts (log scale) |
| Material Symbols Outlined | Icons (loaded via CDN in `index.html`) |

### Tailwind v4 — PostCSS only (critical)

`@tailwindcss/vite` is **incompatible with Vite 8** (throws "Cannot read properties of undefined reading 'stdin'"). The project uses `@tailwindcss/postcss` instead. Do not add `@tailwindcss/vite` back to `vite.config.ts`.

Config files: `postcss.config.js` (uses `@tailwindcss/postcss` + `autoprefixer`), no `tailwind.config.js` needed for v4.

### Design system

Material You dark theme. All colors are CSS custom properties in `src/index.css`:

- `--primary-container: #f59e0b` — amber, primary interactive accent (buttons, active states)
- `--secondary: #4cd7f6` — cyan, data/QuickSort highlights, step counters
- `--tertiary: #56e5a9` — green, success/pass states
- `--surface-container-lowest` through `--surface-container-highest` — layered dark surfaces

Fonts loaded via Google Fonts CDN in `index.html`:
- **Space Grotesk** — headings, labels, buttons
- **Manrope** — body text (default `font-family` on `body`)
- **JetBrains Mono** — all code, numbers, metrics, monospace data

Global utility classes in `index.css`: `.bg-grid`, `.analog-grain`, `.animate-stripes`, `.amber-glow`, `.amber-glow-lg`.

### Routing and layout

`App.tsx` wraps all routes in `<Layout />`. The layout renders:
- `SideNav` (fixed, 240px left) — hex logo, NEW EXPERIMENT button, 6 nav links with Material Symbols icons, System Status/Settings footer
- `TopBar` (fixed, 64px, `calc(100% - 240px)` wide) — search input, Terminal/Docs/Telemetry links, icon buttons, SAVE_STATE + EXECUTE_RUN buttons
- `<Outlet />` inside `AnimatePresence` for page transitions (`marginLeft: 240`)

### Pages

| Route | File | Description |
|---|---|---|
| `/problems` | `pages/Problems.tsx` | Problem card grid with category badges |
| `/algorithms` | `pages/Algorithms.tsx` | 3-panel Monaco editor (file list + editor + inspector) |
| `/generator` | `pages/Generator.tsx` | Code editor + live preview panel, dataset size/mode controls |
| `/experiments` | `pages/Experiments.tsx` | Animated experiment runner with progress bars (mock auto-plays) |
| `/results` | `pages/Results.tsx` | Recharts LineCharts (log scale) + results comparison table |
| `/visualizer` | `pages/Visualizer.tsx` | Fully functional step-by-step visualizer (the crown feature) |

### Visualizer page details

`computeBubble(arr)` and `computeQuick(arr)` pre-compute all steps client-side. `AlgoPanel` renders bars with Framer Motion `layout` animations. The `TYPE_COLOR` map assigns colors to step types (`compare`/`swap`/`pivot`/`done`). Both panels share a single `step` state index that advances via `setInterval`.

---

## Backend (planned — not yet implemented)

Planned structure:
```
backend/
  app/
    main.py         # FastAPI app, CORS, WebSocket endpoint
    models.py       # SQLAlchemy: Problem, Algorithm, InputGenerator, Experiment, ExperimentRun
    routers/        # problems.py, algorithms.py, experiments.py
    sandbox.py      # safe Python execution
    executor.py     # experiment orchestration
  database.db
  requirements.txt
```

Algorithm interface contract:
```python
def solve(data, tracker):
    tracker.step("compare", {"i": j, "j": j+1})
    tracker.step("swap", {"i": j, "j": j+1})
    return data
```

Input generator interface:
```python
def generate(n, **params) -> data:
    ...
```

---

## Implementation phases

1. **Backend foundation** — FastAPI, SQLAlchemy models, SQLite, CRUD endpoints, sandbox, executor
2. **Frontend wiring** — replace mock data with real API calls, add `src/api/` fetch wrappers and `src/types/`
3. **Experiments** — WebSocket progress bar, results persistence
4. **Visualizer backend** — tracker object, step capture, API endpoint returning full step list
5. **Export** — CSV, JSON, PNG (canvas.toBlob)
6. **Polish** — built-in example problems (BubbleSort vs QuickSort), docs
