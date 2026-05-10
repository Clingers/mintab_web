# Mintab Web

* Updated front‑end: React + TypeScript + Vite + Tailwind + DaisyUI, modern tech UI, state managed by Zustand.

A web application for industrial quality data analysis and statistics.


## Overview

Mintab Web is a full-stack web application designed for analyzing industrial quality data. It provides tools for uploading CSV/Excel files, performing statistical analysis, and generating various types of plots to help visualize data patterns and quality metrics.

## Features

- **File Upload**: Support for CSV and Excel (.xlsx, .xls) files
- **Data Analysis**: Calculate basic statistics for numeric columns (mean, median, std, min, max, etc.)
- **Data Visualization**: Generate scatter plots, histograms, boxplots, and heatmaps
- **Industrial Quality Focus**: Tailored for manufacturing and quality control data analysis
- **Responsive Design**: Works on desktop and mobile devices
- **Chinese Language Support**: Interface and documentation in Chinese

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Data Processing**: Pandas
- **Statistics**: Custom statistical utilities
- **Plotting**: Matplotlib and Seaborn
- **Containerization**: Docker

### Frontend
- **Language**: TypeScript
- **Framework**: React-like vanilla JS with custom UI components
- **Styling**: CSS3
- **Build**: Native TypeScript compilation

### DevOps
- **Container Orchestration**: Docker Compose
- **Reverse Proxy**: Nginx
- **API Communication**: RESTful JSON APIs

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Git (for cloning the repository)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Clingers/mintab_web.git
cd mintab_web
```

2. Build and start the services:
```bash
docker-compose up --build
```

3. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs (Swagger UI)

### Development Mode

For development without Docker:

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
# Install dependencies if needed (project uses native TS compilation)
# Open index.html in a browser or use a simple static server
```

## API Endpoints

### POST `/upload`
Upload a CSV or Excel file for analysis.

**Parameters:**
- `file`: CSV or Excel file (required)

**Response:**
```json
{
  "dataset_id": "uuid-string",
  "filename": "uploaded_file.csv",
  "rows": 1000,
  "columns": [
    {
      "name": "column_name",
      "type": "numeric|categorical",
      "non_null": 950,
      "null_pct": 5.0,
      "unique_values": 50
    }
  ],
  "preview": [
    {"column1": "value1", "column2": "value2"},
    ...
  ]
}
```

### POST `/analyze`
Perform statistical analysis on an uploaded dataset.

**Parameters:**
```json
{
  "dataset_id": "uuid-string"
}
```

**Response:**
```json
{
  "dataset_id": "uuid-string",
  "statistics": {
    "column_name": {
      "count": 1000,
      "mean": 50.5,
      "median": 50.0,
      "std": 15.2,
      "min": 10.0,
      "max": 90.0,
      "q1": 30.0,
      "q3": 70.0
    }
  }
}
```

### POST `/plot`
Generate a plot for the dataset.

**Parameters:**
```json
{
  "dataset_id": "uuid-string",
  "plot_type": "scatter|histogram|boxplot|heatmap",
  "x_col": "column_name", // required for scatter
  "y_col": "column_name", // required for scatter
  "column": "column_name", // required for histogram/boxplot
  "columns": ["col1", "col2"], // optional for boxplot
  "method": "pearson|kendall|spearman" // optional for heatmap, default: pearson
}
```

**Response:**
```json
{
  "image": "base64_encoded_png_string",
  "format": "png"
}
```

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "datasets_count": 0
}
```

## Project Structure

```
mintab_web/
├── backend/                 # Python/FastAPI backend
│   ├── main.py              # FastAPI application entrypoint
│   ├── stats_utils.py       # Statistical calculation functions
│   ├── plot_utils.py        # Plotting functions (matplotlib/seaborn)
│   ├── tests/               # Unit tests
│   │   ├── test_stats.py    # Tests for stats_utils
│   │   └── test_plots.py    # Tests for plot_utils
│   └── requirements.txt     # Python dependencies
├── frontend/                # TypeScript frontend
│   ├── src/
│   │   ├── main.ts          # Application entrypoint
│   │   ├── api.ts           # API communication layer
│   │   ├── ui.ts            # UI component functions
│   │   ├── types.ts         # TypeScript type definitions
│   │   └── style.css        # Styling
│   ├── public/              # Static assets
│   ├── index.html           # HTML entrypoint
│   ├── package.json         # npm dependencies
│   └── tsconfig.json        # TypeScript configuration
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile.backend       # Backend Dockerfile
├── Dockerfile.frontend      # Frontend Dockerfile
├── nginx.conf               # Nginx configuration
└── README.md                # This file
```

## Configuration

### Environment Variables
The backend can be configured using environment variables:
- `CORS_ORIGINS`: Comma-separated list of allowed origins for CORS (default: "*")
- Other configurations can be added as needed

### Docker Configuration
The Docker Compose file defines two services:
- **backend**: Runs the FastAPI API on port 8000
- **frontend**: Serves the static frontend on port 80

Nginx is used as a reverse proxy to route `/api` requests to the backend and serve static files for the frontend.

## Testing

### Backend Tests
Run the backend unit tests:
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Testing
The frontend can be tested by:
1. Manual testing through the browser interface
2. Automated tests can be added using frameworks like Jest or Vitest

## Deployment

### Production Deployment
For production use, consider:
1. Using a proper SSL certificate
2. Setting environment-specific configurations
3. Implementing authentication and authorization
4. Adding rate limiting and security headers
5. Using a production-grade WSGI server (like Gunicorn) instead of Uvicorn directly
6. Setting up logging and monitoring

### Scaling
The application can be scaled by:
1. Running multiple backend instances behind a load balancer
2. Using external storage for datasets instead of in-memory storage
3. Offloading plot generation to worker queues for heavy computations

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by Minitab's statistical analysis capabilities
- Built with FastAPI for high-performance API endpoints
- Uses Pandas for efficient data manipulation
- Plotting powered by Matplotlib and SeabornAPI documentation is available at http://localhost:8000/docs (Swagger UI) when the backend is running.

## API Documentation

The backend provides a RESTful API with automatic OpenAPI/Swagger documentation.

When the backend is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

These documents are automatically generated from the FastAPI application and provide:
- Detailed endpoint descriptions
- Request/response schemas
- Interactive API testing
- Code examples in multiple languages
