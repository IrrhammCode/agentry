import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import app

def test_store_api():
    app.init_db()
    count = app.get_product_count()
    assert count >= 2, f"Expected at least 2 products, got {count}"

def test_add_product():
    app.add_product('Mechanical Keyboard', 120.00)
    assert app.get_product_count() >= 3
