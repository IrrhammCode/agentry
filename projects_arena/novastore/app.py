"""
NovaStore Production API & E-Commerce Service
FastAPI REST application featuring:
- Full product catalog with categories, stock tracking, and search
- Atomic transactional checkout with inventory deduction
- Order lifecycle management and analytics
- Direct HTML dashboard serving at '/'
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .database import (
    init_db,
    seed_data,
    list_categories,
    list_products,
    get_product,
    create_product,
    update_product_stock,
    delete_product,
    create_order_transactional,
    list_orders,
    get_order_details,
    update_order_status,
    get_store_analytics,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_data()
    yield


app = FastAPI(
    title="NovaStore E-Commerce & Inventory Platform",
    description="Production-grade e-commerce microservice with real-time stock management and order processing",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class ProductCreate(BaseModel):
    category_id: int = Field(..., description="Category ID")
    name: str = Field(..., min_length=2, max_length=128)
    sku: str = Field(..., min_length=3, max_length=32)
    description: str = Field(default="")
    price: float = Field(..., gt=0.0)
    stock: int = Field(..., ge=0)
    image_url: Optional[str] = Field(default=None)


class ProductStockUpdate(BaseModel):
    stock: int = Field(..., ge=0)


class OrderItemInput(BaseModel):
    product_id: int = Field(..., description="Target product ID")
    quantity: int = Field(..., ge=1, description="Quantity to purchase")


class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    customer_email: str = Field(..., min_length=5, max_length=100, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    customer_address: str = Field(..., min_length=5, max_length=255)
    items: List[OrderItemInput] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status: pending, processing, shipped, delivered, cancelled")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=FileResponse)
async def serve_home():
    if not INDEX_HTML.exists():
        return JSONResponse({"message": "NovaStore API operational. Visit /docs for Swagger specifications."})
    return FileResponse(str(INDEX_HTML), media_type="text/html")


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "NovaStore",
        "version": "1.0.0",
        "timestamp": time.time(),
    }


@app.get("/api/analytics/overview")
async def analytics():
    return get_store_analytics()


@app.get("/api/categories")
async def get_categories():
    cats = list_categories()
    return {"categories": cats, "count": len(cats)}


@app.get("/api/products")
async def get_products(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search keyword in name, description, or SKU"),
):
    products = list_products(category_id=category_id, search=search)
    return {"products": products, "count": len(products)}


@app.get("/api/products/{product_id}")
async def get_product_by_id(product_id: int):
    prod = get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail=f"Product #{product_id} not found.")
    return prod


@app.post("/api/products", status_code=status.HTTP_201_CREATED)
async def add_product(payload: ProductCreate):
    try:
        pid = create_product(
            category_id=payload.category_id,
            name=payload.name,
            sku=payload.sku,
            description=payload.description,
            price=payload.price,
            stock=payload.stock,
            image_url=payload.image_url,
        )
        return {"message": "Product created successfully.", "product_id": pid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.patch("/api/products/{product_id}/stock")
async def modify_stock(product_id: int, payload: ProductStockUpdate):
    prod = get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail=f"Product #{product_id} not found.")
    update_product_stock(product_id, payload.stock)
    return {"message": f"Stock for product #{product_id} updated to {payload.stock}."}


@app.delete("/api/products/{product_id}")
async def remove_product(product_id: int):
    prod = get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail=f"Product #{product_id} not found.")
    delete_product(product_id)
    return {"message": f"Product #{product_id} deleted."}


@app.get("/api/orders")
async def get_orders(order_status: Optional[str] = Query(None, alias="status")):
    orders = list_orders(status=order_status)
    return {"orders": orders, "count": len(orders)}


@app.get("/api/orders/{order_id}")
async def get_order(order_id: int):
    order = get_order_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found.")
    return order


@app.post("/api/orders/checkout", status_code=status.HTTP_201_CREATED)
async def checkout(payload: CheckoutRequest):
    """
    Atomic checkout:
    Validates items, deducts inventory, and places order within a single transaction.
    """
    try:
        items_payload = [item.model_dump() for item in payload.items]
        receipt = create_order_transactional(
            customer_name=payload.customer_name,
            customer_email=payload.customer_email,
            customer_address=payload.customer_address,
            items=items_payload,
        )
        return {
            "message": "Order placed successfully! Inventory updated.",
            "order": receipt,
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout failed: {str(e)}")


@app.patch("/api/orders/{order_id}/status")
async def modify_order_status(order_id: int, payload: OrderStatusUpdate):
    valid_statuses = {"pending", "processing", "shipped", "delivered", "cancelled"}
    if payload.status.lower() not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{payload.status}'. Must be one of: {', '.join(valid_statuses)}.",
        )
    success = update_order_status(order_id, payload.status.lower())
    if not success:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found.")
    return {"message": f"Order #{order_id} status updated to '{payload.status.lower()}'."}


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
