#!/usr/bin/env python3
"""
FastAPI entrypoint for the Mintab‑Web data‑analysis service.
"""
import os
import tempfile
import uuid
from typing import List, Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
import pandas as pd
import stats_utils
import plot_utils

app = FastAPI(title="Mintab Web API", version="0.1.0")

# In‑memory storage for uploaded datasets: dataset_id -> file path
datasets: Dict[str, str] = {}


# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------
def _save_to_temp(file_obj: UploadFile) -> str:
    """Write uploaded file to a temporary file and return a dataset_id."""
    suffix = os.path.splitext(file_obj.filename)[1].lower()
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    # Copy chunks to avoid loading whole file into memory twice
    with tmp as tmpfile:
        for chunk in file_obj.file:
            tmpfile.write(chunk)
    # Generate a unique dataset_id and store the path
    dataset_id = str(uuid.uuid4())
    datasets[dataset_id] = tmp.name
    return dataset_id


def _infer_schema(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert DataFrame schema to a serialisable list of column meta."""
    schema = []
    for col_name, dtype in df.dtypes.items():
        schema.append(
            {
                "name": col_name,
                "type": "numeric" if pd.api.types.is_numeric_dtype(dtype) else "categorical",
                "non_null": int(df[col_name].notna().sum()),
                "null_pct": round(100 * df[col_name].isna().mean(), 2),
                "unique_values": df[col_name].nunique(),
            }
        )
    return schema


def _sample_df(df: pd.DataFrame, n: int = 5) -> List[Dict[str, Any]]:
    """Return the first *n* rows as a serialisable list of mapping."""
    sample = df.head(n)
    return sample.to_dict(orient="records")


# ----------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Accept a CSV or Excel file, parse it, and return basic meta‑information.
    Also generates a dataset_id for later analysis.
    """
    if not file.content_type.startswith(("text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save to temporary storage and get dataset_id
    dataset_id = _save_to_temp(file)

    try:
        tmp_path = datasets[dataset_id]
        # Load data according to extension
        if tmp_path.lower().endswith(".csv"):
            df = pd.read_csv(tmp_path)
        elif tmp_path.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="File must be .csv, .xlsx or .xls")

        # Basic sanity checks
        if df.empty:
            raise HTTPException(status_code=400, detail="File is empty")

        # Build meta payload
        payload = {
            "dataset_id": dataset_id,
            "filename": file.filename,
            "rows": int(df.shape[0]),
            "columns": _infer_schema(df),
            "preview": _sample_df(df, n=5),
        }
        return JSONResponse(content=payload)

    except Exception as e:
        # Clean up on error
        if dataset_id in datasets:
            del datasets[dataset_id]
            try:
                os.remove(tmp_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "ok", "datasets_count": len(datasets)}


@app.post("/analyze")
async def analyze_data(payload: Dict[str, Any]):
    """
    Analyze a previously uploaded dataset.
    Expects JSON body: {"dataset_id": "<id>"}
    Returns basic statistics for each numeric column.
    """
    dataset_id = payload.get("dataset_id")
    if not dataset_id or dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")

    tmp_path = datasets[dataset_id]
    try:
        # Load the dataset
        if tmp_path.lower().endswith(".csv"):
            df = pd.read_csv(tmp_path)
        elif tmp_path.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")

        # Calculate statistics for each column
        results = {}
        for col in df.columns:
            series = df[col]
            # Check if numeric
            if pd.api.types.is_numeric_dtype(series):
                try:
                    stats = stats_utils.calculate_basic_stats(series)
                    results[col] = stats
                except ValueError as e:
                    results[col] = {"error": str(e)}
            else:
                results[col] = {"type": "categorical", "unique": series.nunique()}

        return JSONResponse(content={"dataset_id": dataset_id, "statistics": results})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/plot")
async def generate_plot(request: Request):
    """
    Generate a plot based on a previously uploaded dataset.
    Expects JSON body: {
        "dataset_id": "<id>",
        "plot_type": "scatter" | "histogram" | "boxplot" | "heatmap",
        "x_col": optional for scatter,
        "y_col": optional for scatter,
        "column": optional for histogram/boxplot,
        "columns": optional for boxplot (list),
        "method": optional for heatmap (pearson/kendall/spearman)
    }
    Returns JSON: {"image": "<base64>", "format": "png"}
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    dataset_id = body.get("dataset_id")
    if not dataset_id or dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")

    plot_type = body.get("plot_type")
    if not plot_type:
        raise HTTPException(status_code=400, detail="Missing 'plot_type' parameter")

    tmp_path = datasets[dataset_id]
    try:
        # Load dataset
        if tmp_path.lower().endswith(".csv"):
            df = pd.read_csv(tmp_path)
        elif tmp_path.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")

        # Dispatch to appropriate plotting function
        if plot_type == "scatter":
            x_col = body.get("x_col")
            y_col = body.get("y_col")
            if not x_col or not y_col:
                raise HTTPException(status_code=400, detail="Scatter plot requires 'x_col' and 'y_col'")
            b64 = plot_utils.plot_scatter(df, x_col, y_col)
        elif plot_type == "histogram":
            column = body.get("column")
            if not column:
                raise HTTPException(status_code=400, detail="Histogram requires 'column' parameter")
            series = df[column]
            b64 = plot_utils.plot_histogram(series)
        elif plot_type == "boxplot":
            columns = body.get("columns")  # optional, list
            b64 = plot_utils.plot_boxplot(df, columns=columns)
        elif plot_type == "heatmap":
            method = body.get("method", "pearson")
            b64 = plot_utils.plot_heatmap(df, method=method)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported plot_type: {plot_type}")

        return JSONResponse(content={"image": b64, "format": "png"})

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plot generation failed: {str(e)}")


# ----------------------------------------------------------------------
# Run with: uvicorn backend.main:app --host 0.0.0.0 --port 8000
# ----------------------------------------------------------------------
