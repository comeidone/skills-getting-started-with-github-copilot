"""Pytest configuration and shared fixtures for API tests"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture that provides a TestClient for making requests to the FastAPI app"""
    return TestClient(app)
