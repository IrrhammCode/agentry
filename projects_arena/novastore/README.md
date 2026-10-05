# NovaStore // Modern E-Commerce & Inventory Platform

A full-stack e-commerce store and merchant operations microservice built with **FastAPI**, **SQLite (WAL Concurrency)**, and a modern **Reactive Web Dashboard**.

---

## 🛍️ Features

- **Dynamic Catalog**: Categorized product listings (Electronics, Audio, Workspace, Accessories) with real-time stock availability and instant search.
- **Atomic Checkout Engine**: Multi-item shopping cart with transactional inventory decrement in SQLite. If any item is out of stock, the transaction rolls back cleanly.
- **Merchant Operations Hub**:
  - Live revenue metrics & sales totals.
  - Low stock alerts (items with &le; 10 units).
  - Real-time stock restocker.
  - Product catalog manager (add, update, delete).
  - Order status lifecycle manager (pending &rarr; shipped &rarr; delivered).
- **Zero-Dependency Modern Web UI**: Fast, responsive dark UI (`#000000`) with glassmorphism, instant cart drawer, and order confirmation receipt.
- **Comprehensive Pytest Suite**: 10 automated unit and integration tests passing 100%.

---

## 🚀 Running the Platform

### Start the Service:
```bash
python -m uvicorn projects_arena.novastore.app:app --host 127.0.0.1 --port 5051
```

### Endpoints:
- **Interactive Storefront & Merchant Dashboard**: [http://127.0.0.1:5051](http://127.0.0.1:5051)
- **Interactive Swagger / OpenAPI Specs**: [http://127.0.0.1:5051/docs](http://127.0.0.1:5051/docs)
- **Health Diagnostics**: [http://127.0.0.1:5051/api/health](http://127.0.0.1:5051/api/health)
- **Analytics Overview**: [http://127.0.0.1:5051/api/analytics/overview](http://127.0.0.1:5051/api/analytics/overview)

### Run Tests:
```bash
pytest projects_arena/novastore/tests/test_store.py -v
```
