import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parent / 'store.db')

def init_db():
    # Properly closed connection as directed by Agentry!
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )''')
        conn.commit()

def add_product(name, price):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
        conn.commit()

def get_product_count():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT count(*) FROM products')
        row = cursor.fetchone()
        return row[0] if row else 0

if __name__ == '__main__':
    init_db()
    add_product('MacBook Pro M3', 1999.00)
    add_product('Dell XPS 15', 1499.00)
    print(f"Store API ready. Total products: {get_product_count()}")
