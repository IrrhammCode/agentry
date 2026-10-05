import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parent / 'store.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )''')
    conn.commit()
    # BUG: Connection is left unclosed, causing database lock in subsequent steps!
    return conn

def add_product(name, price):
    conn = sqlite3.connect(DB_PATH, timeout=0.1)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Store API initialized.")
