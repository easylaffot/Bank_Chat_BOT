"""Shared isolated fixtures for the compact application test suite."""

import sqlite3
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "CRITICAL")
    monkeypatch.setenv("SQLITE_DATABASE_PATH", str(tmp_path / "test.sqlite"))
    monkeypatch.setenv("CHROMA_PERSIST_DIRECTORY", str(tmp_path / "chroma"))
    monkeypatch.setenv("CHROMA_FAQ_COLLECTION_NAME", "pytest-faq")
    monkeypatch.setenv("OLLAMA_API_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("OLLAMA_API_KEY", "")
    monkeypatch.setenv("OLLAMA_MODEL", "pytest-no-network")
    return tmp_path


@pytest.fixture
def sample_products():
    return [
        {
            "id": "LAP-001",
            "brand": "Dell",
            "model_name": "Inspiron Test",
            "category": "Programming",
            "price": 39990,
            "ram_gb": 8,
            "processor": "Intel Core i3-1215U",
            "storage_gb": 512,
            "battery_hours": 7.0,
            "stock_quantity": 8,
            "delivery_days": 2,
            "rating": 4.3,
        },
        {
            "id": "LAP-002",
            "brand": "HP",
            "model_name": "Pavilion Test",
            "category": "Programming",
            "price": 56990,
            "ram_gb": 16,
            "processor": "Intel Core i5-1235U",
            "storage_gb": 512,
            "battery_hours": 8.0,
            "stock_quantity": 5,
            "delivery_days": 3,
            "rating": 4.5,
        },
        {
            "id": "LAP-003",
            "brand": "Lenovo",
            "model_name": "LOQ Test",
            "category": "Gaming",
            "price": 89990,
            "ram_gb": 16,
            "processor": "Intel Core i7-13650HX",
            "storage_gb": 1024,
            "battery_hours": 5.0,
            "stock_quantity": 0,
            "delivery_days": 6,
            "rating": 4.6,
        },
    ]


@pytest.fixture
def temp_database(test_environment, sample_products):
    database_path = test_environment / "test.sqlite"
    connection = sqlite3.connect(database_path)
    connection.execute(
        """
        CREATE TABLE products (
            id TEXT PRIMARY KEY NOT NULL,
            brand TEXT NOT NULL,
            model_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price INTEGER NOT NULL,
            ram_gb INTEGER NOT NULL,
            processor TEXT NOT NULL,
            storage_gb INTEGER NOT NULL,
            battery_hours REAL NOT NULL,
            stock_quantity INTEGER NOT NULL,
            delivery_days INTEGER NOT NULL,
            rating REAL NOT NULL
        )
        """
    )
    columns = (
        "id, brand, model_name, category, price, ram_gb, processor, storage_gb, "
        "battery_hours, stock_quantity, delivery_days, rating"
    )
    placeholders = ", ".join("?" for _ in range(12))
    connection.executemany(
        f"INSERT INTO products ({columns}) VALUES ({placeholders})",
        [tuple(product.values()) for product in sample_products],
    )
    connection.commit()
    connection.close()
    return database_path


@pytest.fixture
def clean_cart(temp_database):
    from app.services.cart_service import CartService

    service = CartService()
    service.clear_cart()
    return service


@pytest.fixture
def client(temp_database):
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_shopping_workflow(sample_products):
    return Mock(
        return_value={
            "recommendation": {
                "recommended_product": sample_products[1],
                "reason": "Best affordable in-stock option.",
                "alternatives": [sample_products[0]],
            },
            "error": None,
        }
    )


@pytest.fixture
def mock_faq_agent():
    from app.schemas.faq import FAQAnswer

    agent = Mock()
    agent.answer.return_value = FAQAnswer(
        answer="Eligible laptops include a one-year manufacturer warranty.",
        sources=["data/faq/warranty.txt"],
    )
    return agent
