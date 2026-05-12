# Mintab Web

Industrial quality data analysis console — upload datasets, compute statistics, and generate visualizations in the browser.

![Dark Theme](https://img.shields.io/badge/theme-dark-0a0e14) ![React](https://img.shields.io/badge/React-19-61dafb) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688) ![License](https://img.shields.io/badge/license-MIT-green)

## Overview

Mintab Web is a full-stack web application designed for engineers and researchers who need quick statistical analysis of tabular data. Upload a CSV or Excel file, get descriptive statistics instantly, and generate publication-ready plots — all from a single dark-themed console interface.

## Features

- **File Upload** — Drag-and-drop or click to upload `.csv`, `.xlsx`, `.xls` files
- **Auto Analysis** — Descriptive statistics computed immediately after upload (count, mean, median, std, min, max, Q1, Q3)
- **Data Preview** — Tabular preview of uploaded data with column type indicators
- **Visualization** — Generate scatter plots, histograms, boxplots, and correlation heatmaps
- **Export** — Download statistics as CSV, plots as PNG
- **Dark Console UI** — Technical Product Console design with emerald signal green accent

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS v4 |
| State | Zustand |
| Backend | FastAPI (Python) |
| Data | Pandas + Matplotlib + Seaborn |
| Deployment | Docker + Nginx reverse proxy |

## Architecture

```
┌─────────────────────────────────────────────┐
│  Browser (React SPA)                        │
│  ┌─────────┐ ┌──────────┐ ┌─────────────┐  │
│  │ Upload  │ │  Stats   │ │    Plot     │  │
│  │ Panel   │ │  Table   │ │   Viewer    │  │
│  └────┬────┘ └────┬─────┘ └──────┬──────┘  │
│       │            │              │          │
│       └────────────┼──────────────┘          │
│                    │                         │
└────────────────────┼─────────────────────────┘
                     │ HTTP (port 80)
┌────────────────────┼─────────────────────────┐
│  Nginx             │                         │
│  /        → static │files (React build)      │
│  /api/*   → proxy  │to backend:8000          │
└────────────────────┼─────────────────────────┘
                     │ port 8000
┌────────────────────┼─────────────────────────┐
│  FastAPI Backend                             │
│  ┌────────┐ ┌───────────┐ ┌──────────────┐  │
│  │/upload │ │ /analyze  │ │   /plot      │  │
│  └────────┘ └───────────┘ └──────────────┘  │
└──────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose (or Docker with manual commands)
- Node.js 18+ (for local development)
- Python 3.11+ (for local backend development)

### Deploy with Docker

```bash
git clone https://github.com/Clingers/mintab_web.git
cd mintab_web

# Build and start both services
docker build -t mintab_web_backend -f Dockerfile.backend .
docker build -t mintab_web_frontend -f Dockerfile.frontend .

# Create network
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

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check, returns `{"status": "ok", ...}` |
| `/upload` | POST | Upload file (multipart/form-data), returns dataset info |
| `/analyze` | POST | Compute statistics for a dataset |
| `/plot` | POST | Generate a plot image (base64 PNG) |

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
  "columns": [{"name": "col1", "type": "numeric", "non_null": 100, ...}],
  "preview": [{"col1": 1.5, "col2": 2.3}, ...]
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
- `boxplot` — requires `column`
- `heatmap` — optional `method` (pearson/kendall/spearman)

Response:
```json
{"image": "<base64 PNG>", "format": "png"}
```

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
│   ├── main.py              # FastAPI app, routes
│   ├── stats_utils.py       # Statistical computation
│   ├── plot_utils.py        # Plot generation (matplotlib)
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main layout
│   │   ├── index.css        # Design system tokens
│   │   ├── components/
│   │   │   ├── UploadPanel.tsx
│   │   │   ├── DatasetInfo.tsx
│   │   │   ├── StatsTable.tsx
│   │   │   └── PlotViewer.tsx
│   │   ├── services/api.ts  # HTTP client
│   │   ├── store/index.ts   # Zustand state
│   │   └── types.ts         # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
├── nginx.conf
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
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
- `backend` — FastAPI on port 8000 (internal)
- `mintab_frontend` — Nginx serving static files on port 80, proxying `/api/*` to backend

## License

MIT
