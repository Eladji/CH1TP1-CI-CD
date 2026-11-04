"""Fixtures partagees: un client HTTP et des donnees remises a zero."""

import pytest
from fastapi.testclient import TestClient

from ch1tp.app import app
from ch1tp.data import reset_data


@pytest.fixture(autouse=True)
def fresh_data():
    """Chaque test repart des donnees initiales: les tests sont independants."""
    reset_data()
    yield
    reset_data()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_student():
    return {
        "firstName": "Sofia",
        "lastName": "Lambert",
        "email": "sofia.lambert@edtech.io",
        "grade": 16.5,
        "field": "mathématiques",
    }
