"""Test configuration and fixtures for the Mintab Web backend tests."""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing."""
    content = """name,age,salary,department,score
John,25,50000,HR,85.5
Jane,30,60000,IT,90.0
Bob,35,70000,IT,78.5
Alice,40,80000,HR,92.0
Charlie,45,90000,IT,88.5"""
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(content)
        f.flush()
        yield f.name
    
    # Cleanup
    os.unlink(f.name)

@pytest.fixture
def sample_excel_file():
    """Create a sample Excel file for testing."""
    try:
        import pandas as pd
        df = pd.DataFrame({
            'name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'age': [25, 30, 35, 40, 45],
            'salary': [50000, 60000, 70000, 80000, 90000],
            'department': ['HR', 'IT', 'IT', 'HR', 'IT'],
            'score': [85.5, 90.0, 78.5, 92.0, 88.5]
        })
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            df.to_excel(f.name, index=False)
            f.flush()
            yield f.name
        
        # Cleanup
        os.unlink(f.name)
    except ImportError:
        # If pandas/openpyxl not available, skip this fixture
        pytest.skip("pandas or openpyxl not available")