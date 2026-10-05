import app
try:
    # This will trigger an OperationalError due to unclosed lock
    app.add_product('Laptop Pro', 1299.99)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    sys.exit(1)
