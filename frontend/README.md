# Mintab Web Frontend

React 19 + TypeScript + Vite + Zustand + Tailwind CSS v4 — a dark-theme data analysis console UI.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 19 + TypeScript |
| Build | Vite 6 |
| State Management | Zustand |
| Styling | Tailwind CSS v4 |
| Chart Library | recharts / raw SVG compositing |
| Testing | Vitest |

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx                     # Main layout, header, error toast
│   ├── main.tsx                    # Entry point
│   ├── index.css                   # Tailwind + design system tokens
│   ├── types.ts                    # TypeScript interfaces
│   ├── store/
│   │   └── index.ts                # Zustand store (dataset, plots, UI state)
│   ├── services/
│   │   └── api.ts                  # HTTP client (upload, analyze, plot, spc, doe)
│   ├── components/
│   │   ├── UploadPanel.tsx         # File drag-and-drop / file picker
│   │   ├── DatasetInfo.tsx         # Dataset metadata summary
│   │   ├── StatsTable.tsx          # Descriptive statistics table
│   │   ├── PlotViewer.tsx          # Scatter / histogram / boxplot / heatmap
│   │   ├── SpcControl.tsx          # SPC control chart (X̄-R, X̄-S, I-MR, p, u)
│   │   └── DoeDesign.tsx           # DOE experiment design (full factorial, PB, CCD, Taguchi)
│   └── assets/                     # Static assets
├── public/
├── dist/                           # Production build output
├── index.html
├── package.json
├── vite.config.ts
└── nginx.conf                      (at project root)
```

## Components Overview

| Component | Purpose |
|-----------|---------|
| `UploadPanel` | Drag-and-drop or click to upload CSV/Excel files |
| `DatasetInfo` | Display dataset metadata (rows, columns, null stats) |
| `StatsTable` | Descriptive statistics with column type badges |
| `PlotViewer` | Scatter, histogram, boxplot, correlation heatmap |
| `SpcControl` | Statistical Process Control charts (5 types) |
| `DoeDesign` | Design of Experiments (4 design types) |

## Development

```bash
# Install dependencies
npm install

# Start dev server (HMR on localhost:5173, proxy API to localhost:8000)
npm run dev

# Run tests
npm run test

# Build for production
npm run build
```

The dev server proxies `/api/*` requests to `http://localhost:8000` (configured in `vite.config.ts`).

## Design System

- **Background**: Near-black (`#0a0e14`) with layered panels (`#111820`, `#1a2332`)
- **Accent**: Emerald Signal Green (`#10b981`) with glow effects
- **Typography**: Inter (UI labels), JetBrains Mono (data/tables)
- **Borders**: Subtle `#1e2d3d` with hover transitions

## Deployment

The frontend is built as a static bundle and served by Nginx in a Docker container.
See the project root `README.md` or `Dockerfile.frontend` for details.