"""
NovaStore Database Layer
Standard SQLite implementation for a production e-commerce & inventory platform:
- Schema for categories, products, customers, orders, and order items
- Concurrency via Write-Ahead Logging (WAL) and foreign keys enforcement
- Atomic transactional checkout with stock validation
- Idempotent seed data for immediate out-of-the-box readiness
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "novastore.db"


def get_db_path() -> Path:
    env_path = os.getenv("NOVASTORE_DB_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


@contextmanager
def get_db_connection(db_path: Optional[str | Path] = None) -> Generator[sqlite3.Connection, None, None]:
    target = Path(db_path) if db_path and str(db_path) != ":memory:" else (db_path or get_db_path())
    if isinstance(target, Path):
        target.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(target), timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        if str(target) != ":memory:":
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA busy_timeout = 5000;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    return dict(row) if row else None


def rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    return [dict(r) for r in rows]


def init_db(db_path: Optional[str | Path] = None) -> None:
    """Initialize schema tables and indexes."""
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()

        # Categories
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                slug TEXT NOT NULL UNIQUE,
                description TEXT
            );
        """)

        # Products
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sku TEXT NOT NULL UNIQUE,
                description TEXT,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                image_url TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
            );
        """)

        # Customers
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                address TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))
            );
        """)

        # Orders
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending', -- pending, processing, shipped, delivered, cancelled
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            );
        """)

        # Order Items
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
            );
        """)

        # Performance Indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);")


def reset_db(db_path: Optional[str | Path] = None) -> None:
    """Drop and recreate schema."""
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS order_items;")
        cur.execute("DROP TABLE IF EXISTS orders;")
        cur.execute("DROP TABLE IF EXISTS customers;")
        cur.execute("DROP TABLE IF EXISTS products;")
        cur.execute("DROP TABLE IF EXISTS categories;")
    init_db(db_path)


# ---------------------------------------------------------------------------
# Seed Data
# ---------------------------------------------------------------------------

SEED_CATEGORIES = [
    {"name": "Electronics", "slug": "electronics", "description": "High-performance tech gear & peripherals"},
    {"name": "Audio", "slug": "audio", "description": "Studio headphones, wireless sound & acoustic accessories"},
    {"name": "Workspace", "slug": "workspace", "description": "Ergonomic furniture, desk pads & organizers"},
    {"name": "Accessories", "slug": "accessories", "description": "Adapters, docks, cables & chargers"},
]

SEED_PRODUCTS = [
    {
        "category_slug": "electronics",
        "name": "Apex Pro Wireless Mechanical Keyboard",
        "sku": "KB-APEX-01",
        "description": "Custom hot-swappable tactile mechanical keyboard with RGB backlighting and Bluetooth 5.2.",
        "price": 159.99,
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&q=80",
    },
    {
        "category_slug": "audio",
        "name": "SonicWave ANC Wireless Headphones",
        "sku": "AU-SONIC-02",
        "description": "Active Noise Cancelling over-ear headphones with 40mm hi-res drivers and 40-hour battery.",
        "price": 199.50,
        "stock": 18,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
    },
    {
        "category_slug": "electronics",
        "name": "UltraView 27-inch 4K HDR Monitor",
        "sku": "MON-U27-03",
        "description": "IPS panel with 99% sRGB color gamut, USB-C 90W power delivery, and anti-glare coating.",
        "price": 349.00,
        "stock": 12,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&q=80",
    },
    {
        "category_slug": "workspace",
        "name": "ErgoFlex Ergonomic Mesh Desk Chair",
        "sku": "CH-ERGO-04",
        "description": "Breathable mesh back with dynamic lumbar support, 4D adjustable armrests, and synchro-tilt.",
        "price": 289.99,
        "stock": 8,
        "image_url": "https://images.unsplash.com/photo-1580481077195-c290a3c2005e?w=500&q=80",
    },
    {
        "category_slug": "accessories",
        "name": "OmniPort 10-in-1 USB-C Docking Station",
        "sku": "DK-OMNI-05",
        "description": "Dual HDMI 4K@60Hz, 100W PD charging, Gigabit Ethernet, SD card reader, and 3x USB 3.2.",
        "price": 89.00,
        "stock": 35,
        "image_url": "https://images.unsplash.com/photo-1625842268584-8f3296236761?w=500&q=80",
    },
    {
        "category_slug": "workspace",
        "name": "PrecisionDesk XXL Vegan Leather Desk Mat",
        "sku": "MAT-PREC-06",
        "description": "900x400mm waterproof desk blotter with anti-slip suede base and smooth mouse gliding surface.",
        "price": 34.50,
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1616440347437-b1c73416efc2?w=500&q=80",
    },
]


def seed_data(db_path: Optional[str | Path] = None) -> Dict[str, int]:
    """Seed initial categories, products, customer, and sample order."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM categories")
        if cur.fetchone()[0] == 0:
            for cat in SEED_CATEGORIES:
                cur.execute(
                    "INSERT INTO categories (name, slug, description) VALUES (?, ?, ?)",
                    (cat["name"], cat["slug"], cat["description"]),
                )

        cur.execute("SELECT id, slug FROM categories")
        cat_map = {row["slug"]: row["id"] for row in cur.fetchall()}

        cur.execute("SELECT COUNT(*) FROM products")
        if cur.fetchone()[0] == 0:
            for prod in SEED_PRODUCTS:
                cid = cat_map.get(prod["category_slug"])
                cur.execute(
                    """
                    INSERT INTO products (category_id, name, sku, description, price, stock, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (cid, prod["name"], prod["sku"], prod["description"], prod["price"], prod["stock"], prod["image_url"]),
                )

        cur.execute("SELECT COUNT(*) FROM customers")
        if cur.fetchone()[0] == 0:
            cur.execute(
                """
                INSERT INTO customers (name, email, address)
                VALUES (?, ?, ?)
                """,
                ("Alex Morgan", "alex.morgan@example.com", "742 Evergreen Terrace, Springfield, OR"),
            )
            customer_id = cur.lastrowid

            # Create 1 sample completed order
            cur.execute("SELECT id, price FROM products LIMIT 2")
            prods = cur.fetchall()
            p1_id, p1_price = prods[0]["id"], prods[0]["price"]
            p2_id, p2_price = prods[1]["id"], prods[1]["price"]

            total = p1_price * 1 + p2_price * 1
            cur.execute(
                "INSERT INTO orders (customer_id, total_amount, status) VALUES (?, ?, ?)",
                (customer_id, total, "shipped"),
            )
            order_id = cur.lastrowid

            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, p1_id, 1, p1_price),
            )
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, p2_id, 1, p2_price),
            )

        cur.execute("SELECT COUNT(*) FROM categories")
        cat_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM products")
        prod_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM orders")
        order_count = cur.fetchone()[0]

        return {"categories": cat_count, "products": prod_count, "orders": order_count}


# ---------------------------------------------------------------------------
# Business Queries & Transactional Operations
# ---------------------------------------------------------------------------

def list_categories(db_path: Optional[str | Path] = None) -> List[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM categories ORDER BY name ASC")
        return rows_to_dicts(cur.fetchall())


def list_products(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db_path: Optional[str | Path] = None,
) -> List[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        query = """
            SELECT p.*, c.name as category_name, c.slug as category_slug
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE 1=1
        """
        params: List[Any] = []
        if category_id:
            query += " AND p.category_id = ?"
            params.append(category_id)
        if search:
            query += " AND (p.name LIKE ? OR p.description LIKE ? OR p.sku LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])

        query += " ORDER BY p.id ASC"
        cur.execute(query, params)
        return rows_to_dicts(cur.fetchall())


def get_product(product_id: int, db_path: Optional[str | Path] = None) -> Optional[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?
            """,
            (product_id,),
        )
        return row_to_dict(cur.fetchone())


def create_product(
    category_id: int,
    name: str,
    sku: str,
    description: str,
    price: float,
    stock: int,
    image_url: Optional[str] = None,
    db_path: Optional[str | Path] = None,
) -> int:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO products (category_id, name, sku, description, price, stock, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (category_id, name, sku, description, price, stock, image_url),
        )
        return cur.lastrowid  # type: ignore[return-value]


def update_product_stock(product_id: int, new_stock: int, db_path: Optional[str | Path] = None) -> bool:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
        return cur.rowcount > 0


def delete_product(product_id: int, db_path: Optional[str | Path] = None) -> bool:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
        return cur.rowcount > 0


def create_order_transactional(
    customer_name: str,
    customer_email: str,
    customer_address: str,
    items: List[Dict[str, Any]],  # list of {"product_id": int, "quantity": int}
    db_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """
    Atomic transactional checkout:
    1. Validate or register customer
    2. Check stock availability for all items
    3. Deduct stock from products
    4. Create order and order_items records
    5. Commit atomically
    """
    if not items:
        raise ValueError("Order must contain at least one item.")

    with get_db_connection(db_path) as conn:
        cur = conn.cursor()

        # Step 1: Customer lookup or creation
        cur.execute("SELECT id FROM customers WHERE email = ?", (customer_email,))
        row = cur.fetchone()
        if row:
            customer_id = row["id"]
        else:
            cur.execute(
                "INSERT INTO customers (name, email, address) VALUES (?, ?, ?)",
                (customer_name, customer_email, customer_address),
            )
            customer_id = cur.lastrowid

        # Step 2: Validate stock and compute totals
        total_amount = 0.0
        validated_items = []

        for item in items:
            pid = item["product_id"]
            qty = item["quantity"]
            if qty <= 0:
                raise ValueError(f"Invalid quantity {qty} for product #{pid}.")

            cur.execute("SELECT id, name, price, stock FROM products WHERE id = ?", (pid,))
            prod = cur.fetchone()
            if not prod:
                raise ValueError(f"Product #{pid} does not exist.")

            if prod["stock"] < qty:
                raise ValueError(
                    f"Insufficient stock for '{prod['name']}'. Requested: {qty}, Available: {prod['stock']}."
                )

            item_total = prod["price"] * qty
            total_amount += item_total
            validated_items.append({
                "product_id": pid,
                "quantity": qty,
                "unit_price": prod["price"],
                "current_stock": prod["stock"],
            })

        # Step 3: Insert Order
        cur.execute(
            "INSERT INTO orders (customer_id, total_amount, status) VALUES (?, ?, 'pending')",
            (customer_id, round(total_amount, 2)),
        )
        order_id = cur.lastrowid

        # Step 4: Insert Order Items & Deduct Stock
        for v in validated_items:
            cur.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
                """,
                (order_id, v["product_id"], v["quantity"], v["unit_price"]),
            )
            new_stock = v["current_stock"] - v["quantity"]
            cur.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, v["product_id"]))

        return {
            "order_id": order_id,
            "customer_id": customer_id,
            "total_amount": round(total_amount, 2),
            "status": "pending",
            "items_count": len(validated_items),
        }


def list_orders(status: Optional[str] = None, db_path: Optional[str | Path] = None) -> List[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        query = """
            SELECT o.*, c.name as customer_name, c.email as customer_email,
                   (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as total_items
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE 1=1
        """
        params = []
        if status:
            query += " AND o.status = ?"
            params.append(status)
        query += " ORDER BY o.id DESC"
        cur.execute(query, params)
        return rows_to_dicts(cur.fetchall())


def get_order_details(order_id: int, db_path: Optional[str | Path] = None) -> Optional[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT o.*, c.name as customer_name, c.email as customer_email, c.address as customer_address
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.id = ?
            """,
            (order_id,),
        )
        order = row_to_dict(cur.fetchone())
        if not order:
            return None

        cur.execute(
            """
            SELECT oi.*, p.name as product_name, p.sku
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
            """,
            (order_id,),
        )
        order["items"] = rows_to_dicts(cur.fetchall())
        return order


def update_order_status(order_id: int, status: str, db_path: Optional[str | Path] = None) -> bool:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        return cur.rowcount > 0


def get_store_analytics(db_path: Optional[str | Path] = None) -> Dict[str, Any]:
    with get_db_connection(db_path) as conn:
        cur = conn.cursor()

        # Revenue
        cur.execute("SELECT COALESCE(SUM(total_amount), 0.0) FROM orders WHERE status != 'cancelled'")
        revenue = cur.fetchone()[0]

        # Order Counts
        cur.execute("SELECT COUNT(*) FROM orders")
        total_orders = cur.fetchone()[0]

        # Products & Low stock
        cur.execute("SELECT COUNT(*) FROM products")
        total_products = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM products WHERE stock <= 10")
        low_stock_alerts = cur.fetchone()[0]

        # Top product by units sold
        cur.execute("""
            SELECT p.name, SUM(oi.quantity) as sold
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            GROUP BY p.id
            ORDER BY sold DESC
            LIMIT 3
        """)
        top_products = rows_to_dicts(cur.fetchall())

        return {
            "total_revenue": round(revenue, 2),
            "total_orders": total_orders,
            "total_products": total_products,
            "low_stock_alerts": low_stock_alerts,
            "top_products": top_products,
        }
