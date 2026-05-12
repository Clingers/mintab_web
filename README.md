# Mintab Web

Industrial quality data analysis console — upload datasets, compute statistics, generate visualizations, run SPC control charts, and design experiments — all in the browser.

![Dark Theme](https://img.shields.io/badge/theme-dark-0a0e14) ![React](https://img.shields.io/badge/React-19-61dafb) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688) ![License](https://img.shields.io/badge/license-MIT-green)

## Overview

Mintab Web is a full-stack web application designed for engineers and researchers who need quick statistical analysis of tabular data. Upload a CSV or Excel file, get descriptive statistics instantly, generate publication-ready plots, monitor process stability with SPC control charts, and plan experiments with DOE — all from a single dark-themed console interface.

## Features

- **File Upload** — Drag-and-drop or click to upload `.csv`, `.xlsx`, `.xls` files
- **Auto Analysis** — Descriptive statistics computed immediately after upload (count, mean, median, std, min, max, Q1, Q3)
- **Data Preview** — Tabular preview of uploaded data with column type indicators
- **Visualization** — Generate scatter plots, histograms, boxplots, and correlation heatmaps
- **Export** — Download statistics as CSV, plots as PNG
- **SPC Control Charts** — 5 chart types: X̄-R (均值-极差), X̄-S (均值-标准差), I-MR (单值-移动极差), p (不合格品率), u (单位缺陷数) — with control limits, violation markers, and Western Electric rules detection
- **DOE Design of Experiments** — 4 design types: Full Factorial (全因子设计), Plackett-Burman (筛选设计), Central Composite (中心复合/响应曲面), Taguchi (正交表设计 L4/L8/L9/L16/L18)
- **Dark Console UI** — Technical Product Console design with emerald signal green accent

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS v4 |
| State | Zustand |
| Backend | FastAPI (Python) |
| Data | Pandas + Matplotlib + Seaborn + SciPy |
| Statistics | Statsmodels (for advanced SPC calculations) |
| Deployment | Docker + Nginx reverse proxy |

## Architecture

```
┌─────────────────────────────────────────────┐
│  Browser (React SPA)                        │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │  Upload  │ │  Stats   │ │   Plot     │  │
│  │  Panel   │ │  Table   │ │  Viewer    │  │
│  └────┬─────┘ └────┬─────┘ └─────┬──────┘  │
│  ┌─────┴──────┐ ┌──┴────────┐    │          │
│  │  SPC       │ │  DOE      │    │          │
│  │  Control   │ │  Design   │    │          │
│  └─────┬──────┘ └────┬──────┘    │          │
│        │              │           │          │
└────────┼──────────────┼───────────┼──────────┘
         │              │           │ HTTP (port 80)
┌────────┼──────────────┼───────────┼──────────┐
│  Nginx │              │           │          │
│  /          → static │files (React build)    │
│  /api/*     → proxy  │to backend:8000        │
│  /health    → proxy  │to backend:8000        │
└─────────────┼──────────┼─────────────────────┘
              │          │ port 8000
┌─────────────┼──────────┼─────────────────────┐
│  FastAPI Backend                              │
│  ┌────────┐ ┌───────────┐ ┌──────────────┐   │
│  │/upload │ │ /analyze  │ │   /plot      │   │
│  └────────┘ └───────────┘ └──────────────┘   │
│  ┌────────┐ ┌───────────┐                     │
│  │ /spc   │ │  /doe     │                     │
│  └────────┘ └───────────┘                     │
└───────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose (or Docker with manual commands)
- Node.js 18+ (for local development)
- Python 3.11+ (for local backend development)

### Deploy with Docker

> **Note:** `docker-compose` v1 is incompatible with Docker 29+ on certain platforms.  
> Use manual `docker build` + `docker run` commands as shown below.

```bash
git clone https://github.com/Clingers/mintab_web.git
cd mintab_web

# Build images
docker build -t mintab_web_backend -f Dockerfile.backend .
docker build -t mintab_web_frontend -f Dockerfile.frontend .

# Create shared network
docker network create mintab_web_default 2>/dev/null || true

# Start backend
docker run -d --name backend \
  --network mintab_web_default \
  -p 8000:8000 \
  --restart unless-stopped \
  mintab_web_backend

# Start frontend (Nginx)
docker run -d --name mintab_frontend \
  --network mintab_web_default \
  -p 80:80 \
  --restart unless-stopped \
  mintab_web_frontend
```

Access at `http://localhost` (or your server IP).

> **Important:** The backend container **must** be named `backend` for Nginx upstream resolution.  
> Always start the backend container **before** the frontend.

### Local Development

**Backend:**

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server runs at `http://localhost:5173` with API proxy to `:8000`.

## API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check, returns `{"status": "ok", ...}` |
| `/upload` | POST | Upload file (multipart/form-data), returns dataset info and preview |
| `/analyze` | POST | Compute descriptive statistics for a dataset |
| `/plot` | POST | Generate a plot image (base64 PNG) |
| `/spc` | POST | Generate SPC control charts with control limits and violation detection |
| `/doe` | POST | Generate Design of Experiments matrices and visualizations |

### POST /upload

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@data.csv;type=text/csv"
```

Response:
```json
{
  "dataset_id": "uuid",
  "filename": "data.csv",
  "rows": 100,
  "columns": [{"name": "col1", "type": "numeric", "non_null": 100, "null_pct": 0.0, "unique_values": 50}],
  "preview": [{"col1": 1.5, "col2": 2.3}]
}
```

### POST /analyze

```json
{"dataset_id": "uuid"}
```

Response:
```json
{
  "dataset_id": "uuid",
  "statistics": {
    "col1": {"count": 100, "mean": 5.2, "median": 5.0, "std": 1.3, "min": 1, "max": 10, "q1": 3, "q3": 7}
  }
}
```

### POST /plot

```json
{
  "dataset_id": "uuid",
  "plot_type": "histogram",
  "column": "col1"
}
```

Plot types and required parameters:
- `scatter` — requires `x_col`, `y_col`
- `histogram` — requires `column`
- `boxplot` — optional `columns` (list)
- `heatmap` — optional `method` (pearson/kendall/spearman)

Response:
```json
{"image": "<base64 PNG>", "format": "png"}
```

### POST /spc

Generate SPC control charts with control limits and violation detection.

```json
{
  "dataset_id": "uuid",
  "chart_type": "xbar_r",
  "column": "measurement",
  "group_col": null,
  "group_size": 5,
  "nsigma": 3.0
}
```

Supported `chart_type` values:
| Chart Type | Description | Requires |
|-----------|-------------|----------|
| `xbar_r` | X̄-R Chart (均值-极差) | `column`, optional `group_col`/`group_size` |
| `xbar_s` | X̄-S Chart (均值-标准差) | `column`, optional `group_col`/`group_size` |
| `i_mr` | I-MR Chart (单值-移动极差) | `column` |
| `p` | p-Chart (不合格品率) | `defect_col`, optional `total_col`/`constant_sample_size` |
| `u` | u-Chart (单位缺陷数) | `defect_col`, optional `sample_size_col`/`constant_unit_size` |

Response includes:
```json
{
  "chart_type": "xbar_r",
  "images": {
    "combined": "<base64 PNG>",
    "xbar": "<base64 PNG>",
    "r": "<base64 PNG>"
  },
  "chart_data": {
    "xbar_limits": {"ucl": 10.5, "cl": 9.2, "lcl": 7.9},
    "r_limits": {"ucl": 3.1, "cl": 1.5, "lcl": 0.0},
    "violations": [/* points violating Western Electric rules */],
    "subgroups": [/* data points with group statistics */]
  }
}
```

### POST /doe

Generate Design of Experiments matrices and visualizations.

**Full Factorial:**
```json
{
  "design_type": "full_factorial",
  "n_factors": 3,
  "levels": 2,
  "center_points": 1,
  "factor_names": ["Temp", "Pressure", "Catalyst"]
}
```

**Plackett-Burman:**
```json
{
  "design_type": "plackett_burman",
  "n_factors": 7,
  "n_runs": 12
}
```

**Central Composite (CCD):**
```json
{
  "design_type": "central_composite",
  "n_factors": 2,
  "face": "circumscribed",
  "alpha": 1.414,
  "center_points": 5
}
```

**Taguchi Orthogonal Array:**
```json
{
  "design_type": "taguchi",
  "table_name": "L9",
  "n_factors": 4
}
```

Supported `design_type` values: `full_factorial`, `plackett_burman`, `central_composite`, `taguchi`

Supported Taguchi tables: `L4`, `L8`, `L9`, `L16`, `L18`

Response includes design matrix, parameter summaries, and base64-encoded visualizations (cube plot, factor distribution, design matrix heatmap).

## Design System

The UI follows the **Technical Product Console** archetype:

- **Background**: Near-black (`#0a0e14`) with layered surfaces (`#111820`, `#1a2332`)
- **Accent**: Emerald Signal Green (`#10b981`) with glow effects
- **Typography**: Inter for UI, JetBrains Mono for data
- **Components**: `.panel`, `.data-table`, `.btn-primary`, `.btn-ghost`, `.select-field`
- **Borders**: Subtle (`#1e2d3d`) with hover state transitions

## Project Structure

```
mintab_web/
├── backend/
│   ├── main.py              # FastAPI app, all API routes
│   ├── stats_utils.py       # Descriptive statistics computation
│   ├── plot_utils.py        # Plot generation (matplotlib/seaborn)
│   ├── spc_utils.py         # SPC control chart calculations
│   ├── spc_plot.py          # SPC chart rendering (matplotlib)
│   ├── doe_utils.py         # DOE design matrix generation
│   ├── doe_plot.py          # DOE visualization (cube, grid, heatmap)
│   ├── requirements.txt
│   └── tests/
│       ├── test_api.py
│       ├── test_stats.py
│       ├── test_plots.py
│       └── conftest.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Main layout + navigation
│   │   ├── main.tsx               # Entry point
│   │   ├── index.css              # Design system tokens
│   │   ├── types.ts               # TypeScript interfaces
│   │   ├── store/index.ts         # Zustand state
│   │   ├── services/api.ts        # HTTP client
│   │   └── components/
│   │       ├── UploadPanel.tsx    # File upload (CSV/Excel)
│   │       ├── DatasetInfo.tsx    # Dataset metadata
│   │       ├── StatsTable.tsx     # Statistics table
│   │       ├── PlotViewer.tsx     # Scatter, histogram, boxplot, heatmap
│   │       ├── SpcControl.tsx     # SPC control chart UI
│   │       └── DoeDesign.tsx      # DOE experiment design UI
│   ├── package.json
│   └── vite.config.ts
├── nginx.conf                     # Nginx reverse proxy config
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml             # (docker-compose v3.8, for reference only)
└── README.md
```

## Running Tests

```bash
# Backend
cd backend && pytest -v tests/

# Frontend
cd frontend && npm run test
```

## Deployment

Currently deployed at: `http://192.3.161.201`

The application runs as two Docker containers behind Nginx:
- `backend` — FastAPI on port 8000 (internal, **must** be named `backend` for Nginx upstream resolution)
- `mintab_frontend` — Nginx serving static files on port 80, proxying `/api/*` and `/health` to backend

> **Note:** This deployment uses manual `docker build` + `docker run` (not `docker-compose`) because `docker-compose` v1 is incompatible with Docker 29 on the target VPS. The backend must be started **before** the frontend.

## License

MIT