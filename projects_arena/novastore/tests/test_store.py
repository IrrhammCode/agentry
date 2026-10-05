"""
Automated Test Suite for NovaStore E-Commerce Platform
Tests:
- Categories and product catalog queries
- Category filtering and full-text keyword search
- Product creation, inventory updates, and deletion
- Atomic transactional checkout (verifies inventory decrement in SQLite)
- Inventory guardrails: insufficient stock raises 400 and preserves database state
- Order lifecycle state transitions
- Business analytics computations
"""

import pytest
from fastapi.testclient import TestClient

from projects_arena.novastore.app import app
from projects_arena.novastore.database import init_db, reset_db, seed_data, get_product


@pytest.fixture(autouse=True)
def setup_store_db():
    """Reset and re-seed the SQLite database before every test."""
    reset_db()
    seed_data()
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "NovaStore"


def test_list_categories(client):
    res = client.get("/api/categories")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 4
    names = [c["name"] for c in data["categories"]]
    assert "Electronics" in names
    assert "Audio" in names


def test_list_products_and_filter(client):
    # List all
    res = client.get("/api/products")
    assert res.status_code == 200
    prods = res.json()["products"]
    assert len(prods) == 6

    # Filter by category 1 (Electronics)
    res_cat = client.get("/api/products?category_id=1")
    assert res_cat.status_code == 200
    cat_prods = res_cat.json()["products"]
    assert len(cat_prods) >= 1
    assert all(p["category_id"] == 1 for p in cat_prods)

    # Search by keyword "Keyboard"
    res_search = client.get("/api/products?search=Keyboard")
    assert res_search.status_code == 200
    search_prods = res_search.json()["products"]
    assert len(search_prods) == 1
    assert "Keyboard" in search_prods[0]["name"]


def test_product_detail(client):
    res = client.get("/api/products/1")
    assert res.status_code == 200
    prod = res.json()
    assert prod["id"] == 1
    assert "name" in prod
    assert "price" in prod
    assert prod["stock"] > 0


def test_add_and_delete_product(client):
    new_prod = {
        "category_id": 1,
        "name": "Starlight Wireless Gaming Mouse",
        "sku": "MS-STAR-99",
        "description": "Ultra-lightweight magnesium alloy chassis with 26K DPI optical sensor.",
        "price": 129.00,
        "stock": 15,
        "image_url": "https://example.com/mouse.jpg",
    }
    create_res = client.post("/api/products", json=new_prod)
    assert create_res.status_code == 201
    pid = create_res.json()["product_id"]

    # Verify created
    get_res = client.get(f"/api/products/{pid}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Starlight Wireless Gaming Mouse"

    # Delete
    del_res = client.delete(f"/api/products/{pid}")
    assert del_res.status_code == 200

    # Verify 404
    assert client.get(f"/api/products/{pid}").status_code == 404


def test_update_product_stock(client):
    res = client.patch("/api/products/1/stock", json={"stock": 50})
    assert res.status_code == 200
    prod = client.get("/api/products/1").json()
    assert prod["stock"] == 50


def test_atomic_checkout_success(client):
    """
    Test placing an order:
    1. Product #1 initial stock is 25
    2. Order 3 units
    3. Order succeeds and stock drops to 22 atomically in SQLite
    """
    initial_stock = get_product(1)["stock"]
    assert initial_stock == 25

    checkout_payload = {
        "customer_name": "Jordan Lee",
        "customer_email": "jordan.lee@example.com",
        "customer_address": "404 Silicon Way, San Francisco, CA",
        "items": [
            {"product_id": 1, "quantity": 3},
        ],
    }

    res = client.post("/api/orders/checkout", json=checkout_payload)
    assert res.status_code == 201
    receipt = res.json()["order"]
    assert receipt["order_id"] > 0
    assert receipt["status"] == "pending"

    # Verify atomic stock decrement
    updated_stock = get_product(1)["stock"]
    assert updated_stock == initial_stock - 3


def test_atomic_checkout_insufficient_stock_rollback(client):
    """
    Test order failure when requesting more units than available stock.
    Database must rollback and preserve original stock.
    """
    initial_stock = get_product(2)["stock"]
    assert initial_stock == 18

    # Attempt to order 999 units (exceeds stock)
    impossible_payload = {
        "customer_name": "Greedy Buyer",
        "customer_email": "buyer@example.com",
        "customer_address": "123 Main St",
        "items": [
            {"product_id": 2, "quantity": 999},
        ],
    }

    res = client.post("/api/orders/checkout", json=impossible_payload)
    assert res.status_code == 400
    assert "Insufficient stock" in res.json()["detail"]

    # Verify stock remained untouched
    current_stock = get_product(2)["stock"]
    assert current_stock == initial_stock


def test_order_status_lifecycle(client):
    orders = client.get("/api/orders").json()["orders"]
    order_id = orders[0]["id"]

    # Transition to processing
    res1 = client.patch(f"/api/orders/{order_id}/status", json={"status": "processing"})
    assert res1.status_code == 200

    # Transition to delivered
    res2 = client.patch(f"/api/orders/{order_id}/status", json={"status": "delivered"})
    assert res2.status_code == 200

    detail = client.get(f"/api/orders/{order_id}").json()
    assert detail["status"] == "delivered"
    assert len(detail["items"]) > 0


def test_analytics_overview(client):
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_revenue"] > 0
    assert data["total_orders"] >= 1
    assert data["total_products"] == 6
    assert isinstance(data["top_products"], list)
