import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import app

def test_products():
    conn = app.init_db()
    cursor = conn.cursor()
    cursor.execute('SELECT count(*) FROM products')
    assert cursor.fetchone()[0] > 0, "No products found!"
