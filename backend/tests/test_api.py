import os
import tempfile
import tempfile
"""Integration tests for the Mintab Web API."""

import pytest
import json
import base64
from tests.conftest import client, sample_csv_file


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "datasets_count" in data


def test_upload_csv(client, sample_csv_file):
    """Test uploading a CSV file."""
    with open(sample_csv_file, "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test.csv", f, "text/csv")},
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "dataset_id" in data
    assert data["filename"] == "test.csv"
    assert data["rows"] == 5
    assert len(data["columns"]) == 5  # name, age, salary, department, score
    # Check that we have a preview
    assert len(data["preview"]) == 5  # 5 rows preview
    
    # Store dataset_id for use in other tests
    return data["dataset_id"]


def test_upload_excel(client):
    """Test uploading an Excel file (if available)."""
    pytest.importorskip("pandas")
    import pandas as pd
    import tempfile
    import os
    
    # Create a simple Excel file
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        tmp.flush()
        
        with open(tmp.name, "rb") as f:
            response = client.post(
                "/upload",
                files={"file": ("test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "dataset_id" in data
        assert data["filename"] == "test.xlsx"
        assert data["rows"] == 3
        
        # Cleanup
        os.unlink(tmp.name)


def test_upload_invalid_file_type(client):
    """Test uploading an invalid file type."""
    # Create a plain text file
    content = "This is not a CSV or Excel file."
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        
        with open(tmp.name, "rb") as f:
            response = client.post(
                "/upload",
                files={"file": ("test.txt", f, "text/plain")},
            )
        
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]
        
        # Cleanup
        os.unlink(tmp.name)


def test_analyze_endpoint(client, sample_csv_file):
    """Test the analysis endpoint."""
    # First upload a file to get a dataset_id
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/upload",
            files={"file": ("test.csv", f, "text/csv")},
        )
    assert upload_response.status_code == 200
    dataset_id = upload_response.json()["dataset_id"]
    
    # Now analyze the dataset
    response = client.post(
        "/analyze",
        json={"dataset_id": dataset_id},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_id"] == dataset_id
    assert "statistics" in data
    stats = data["statistics"]
    
    # Check that we have statistics for the numeric columns
    assert "age" in stats
    assert "salary" in stats
    assert "score" in stats
    # Check that categorical columns are marked as such
    assert stats["department"]["type"] == "categorical"
    assert stats["name"]["type"] == "categorical"
    
    # Check some known values for the sample data
    # age: [25,30,35,40,45] -> mean 35, median 35
    assert stats["age"]["mean"] == 35.0
    assert stats["age"]["median"] == 35.0
    # salary: [50000,60000,70000,80000,90000] -> mean 70000
    assert stats["salary"]["mean"] == 70000.0
    # score: [85.5,90.0,78.5,92.0,88.5] -> mean 86.9
    assert abs(stats["score"]["mean"] - 86.9) < 0.1


def test_analyze_nonexistent_dataset(client):
    """Test analyzing a dataset that doesn't exist."""
    response = client.post(
        "/analyze",
        json={"dataset_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 404
    assert "Dataset not found" in response.json()["detail"]


def test_plot_scatter(client, sample_csv_file):
    """Test generating a scatter plot."""
    # Upload a file
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/upload",
            files={"file": ("test.csv", f, "text/csv")},
        )
    dataset_id = upload_response.json()["dataset_id"]
    
    # Request a scatter plot
    response = client.post(
        "/plot",
        json={
            "dataset_id": dataset_id,
            "plot_type": "scatter",
            "x_col": "age",
            "y_col": "salary",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "image" in data
    assert data["format"] == "png"
    # Check that the image is a base64 encoded string
    image_data = data["image"]
    # Try to decode it
    try:
        decoded = base64.b64decode(image_data)
        # Check that it's a PNG file (starts with \x89PNG)
        assert decoded[:8] == b'\x89PNG\r\n\x1a\n'
    except Exception:
        pytest.fail("Image data is not valid base64 or not a PNG")


def test_plot_histogram(client, sample_csv_file):
    """Test generating a histogram."""
    # Upload a file
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/upload",
            files={"file": ("test.csv", f, "text/csv")},
        )
    dataset_id = upload_response.json()["dataset_id"]
    
    # Request a histogram
    response = client.post(
        "/plot",
        json={
            "dataset_id": dataset_id,
            "plot_type": "histogram",
            "column": "age",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "image" in data
    assert data["format"] == "png"
    # Validate the image
    try:
        decoded = base64.b64decode(data["image"])
        assert decoded[:8] == b'\x89PNG\r\n\x1a\n'
    except Exception:
        pytest.fail("Image data is not valid base64 or not a PNG")


def test_plot_boxplot(client, sample_csv_file):
    """Test generating a boxplot."""
    # Upload a file
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/upload",
            files={"file": ("test.csv", f, "text/csv")},
        )
    dataset_id = upload_response.json()["dataset_id"]
    
    # Request a boxplot
    response = client.post(
        "/plot",
        json={
            "dataset_id": dataset_id,
            "plot_type": "boxplot",
            "column": "salary",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "image" in data
    assert data["format"] == "png"
    # Validate the image
    try:
        decoded = base64.b64decode(data["image"])
        assert decoded[:8] == b'\x89PNG\r\n\x1a\n'
    except Exception:
        pytest.fail("Image data is not valid base64 or not a PNG")


def test_plot_heatmap(client, sample_csv_file):
    """Test generating a heatmap."""
    # Upload a file
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/upload",
            files={"file": ("test.csv", f, "text/csv")},
        )
    dataset_id = upload_response.json()["dataset_id"]
    
    # Request a heatmap
    response = client.post(
        "/plot",
        json={
            "dataset_id": dataset_id,
            "plot_type": "heatmap",
            "method": "pearson",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "image" in data
    assert data["format"] == "png"
    # Validate the image
    try:
        decoded = base64.b64decode(data["image"])
        assert decoded[:8] == b'\x89PNG\r\n\x1a\n'
    except Exception:
        pytest.fail("Image data is not valid base64 or not a PNG")


def test_plot_invalid_type(client, sample_csv_file):
    """Test requesting an invalid plot type."""
    # Upload a file
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/upload",
            files={"file": ("test.csv", f, "text/csv")},
        )
    dataset_id = upload_response.json()["dataset_id"]
    
    # Request an invalid plot type
    response = client.post(
        "/plot",
        json={
            "dataset_id": dataset_id,
            "plot_type": "invalid",
        },
    )
    
    assert response.status_code == 400
    assert "Unsupported plot_type" in response.json()["detail"]


def test_plot_missing_parameters(client, sample_csv_file):
    """Test requesting a plot with missing required parameters."""
    # Upload a file
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post(
            "/upload",
            files={"file": ("test.csv", f, "text/csv")},
        )
    dataset_id = upload_response.json()["dataset_id"]
    
    # Request a scatter plot without x_col and y_col
    response = client.post(
        "/plot",
        json={
            "dataset_id": dataset_id,
            "plot_type": "scatter",
        },
    )
    
    assert response.status_code == 400
    assert "Scatter plot requires 'x_col' and 'y_col'" in response.json()["detail"]


def test_plot_nonexistent_dataset(client):
    """Test requesting a plot for a dataset that doesn't exist."""
    response = client.post(
        "/plot",
        json={
            "dataset_id": "00000000-0000-0000-0000-000000000000",
            "plot_type": "scatter",
            "x_col": "age",
            "y_col": "salary",
        },
    )
    
    assert response.status_code == 404
    assert "Dataset not found" in response.json()["detail"]