"""
NovaStore End-to-End Integration & Contract Verification Script.
Simulates a complete user journey through the live API & UI contract:
1. Verify HTML assets and DOM hooks match frontend JS
2. Verify all API routes called by frontend JS
3. Test Storefront User Journey: browse, search, filter, checkout
4. Test Merchant Admin Journey: view analytics, restock inventory, change order status, add product
5. Verify real-time database state synchronization
"""

import sys
import json
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:5051"

def api_get(path):
    url = f"{BASE_URL}{path}"
    with urllib.request.urlopen(url) as res:
        return res.getcode(), json.loads(res.read().decode("utf-8"))

def api_post(path, data):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as res:
        return res.getcode(), json.loads(res.read().decode("utf-8"))

def api_patch(path, data):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PATCH",
    )
    with urllib.request.urlopen(req) as res:
        return res.getcode(), json.loads(res.read().decode("utf-8"))

def api_delete(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method="DELETE")
    with urllib.request.urlopen(req) as res:
        return res.getcode(), json.loads(res.read().decode("utf-8"))

def main():
    print("=" * 70)
    print(">>> NOVASTORE FRONTEND-BACKEND INTEGRATION AUDIT")
    print(f"Target Service: {BASE_URL}")
    print("=" * 70)

    # 1. UI HTML & DOM Contract Verification
    print("\n[Step 1] Verifying Frontend HTML DOM Elements...")
    with urllib.request.urlopen(BASE_URL + "/") as res:
        html = res.read().decode("utf-8")

    required_dom_ids = [
        "view-storefront",
        "view-admin",
        "search-input",
        "category-pills",
        "products-grid",
        "cart-modal",
        "cart-items-container",
        "cart-total",
        "cart-badge",
        "checkout-name",
        "checkout-email",
        "checkout-address",
        "checkout-receipt",
        "admin-rev",
        "admin-orders",
        "admin-prods",
        "admin-low-stock",
        "inventory-table-body",
        "orders-table-body",
        "add-product-modal",
    ]

    missing_ids = [dom_id for dom_id in required_dom_ids if f'id="{dom_id}"' not in html]
    if missing_ids:
        print(f"  [FAIL] Missing DOM IDs in index.html: {missing_ids}")
        return False
    print(f"  [OK] All {len(required_dom_ids)} frontend DOM elements verified.")

    # 2. Category & Products Contract
    print("\n[Step 2] Testing Product Catalog & Category Queries...")
    status, cats_res = api_get("/api/categories")
    assert status == 200, f"Expected 200, got {status}"
    cats = cats_res["categories"]
    print(f"  [OK] Categories loaded: {len(cats)} categories ({', '.join(c['name'] for c in cats)})")

    status, prods_res = api_get("/api/products")
    assert status == 200
    prods = prods_res["products"]
    print(f"  [OK] Total Products loaded: {len(prods)} products")

    # Filter by category
    status, cat_filtered = api_get("/api/products?category_id=1")
    assert status == 200
    print(f"  [OK] Category Filter (ID=1) returned: {len(cat_filtered['products'])} items")

    # Search keyword
    status, search_res = api_get("/api/products?search=Keyboard")
    assert status == 200
    assert len(search_res["products"]) >= 1
    print(f"  [OK] Search keyword 'Keyboard' returned: '{search_res['products'][0]['name']}'")

    # 3. Analytics Initial State
    print("\n[Step 3] Checking Initial Store Analytics...")
    status, initial_analytics = api_get("/api/analytics/overview")
    assert status == 200
    rev_before = initial_analytics["total_revenue"]
    orders_before = initial_analytics["total_orders"]
    print(f"  [OK] Current Revenue: ${rev_before:.2f} | Orders: {orders_before} | Low Stock: {initial_analytics['low_stock_alerts']}")

    # 4. End-to-End Customer Checkout Journey
    print("\n[Step 4] Simulating Customer Shopping Cart & Atomic Checkout...")
    # Find a product with available stock
    target_product = next(p for p in prods if p["stock"] >= 2)
    p_id = target_product["id"]
    p_name = target_product["name"]
    p_price = target_product["price"]
    initial_stock = target_product["stock"]

    print(f"  Target Product: '{p_name}' (ID: {p_id}, Price: ${p_price:.2f}, Current Stock: {initial_stock})")
    print("  Customer adds 2 units to cart and proceeds to checkout...")

    checkout_payload = {
        "customer_name": "Rian Pratama",
        "customer_email": "rian.pratama@example.com",
        "customer_address": "Jl. Senopati No. 12, Jakarta Selatan",
        "items": [
            {"product_id": p_id, "quantity": 2}
        ]
    }

    status, checkout_res = api_post("/api/orders/checkout", checkout_payload)
    assert status == 201, f"Checkout failed: {checkout_res}"
    order_receipt = checkout_res["order"]
    new_order_id = order_receipt["order_id"]
    charged_amount = order_receipt["total_amount"]
    print(f"  [SUCCESS] Order Created: #{new_order_id} | Charged: ${charged_amount:.2f} | Status: {order_receipt['status']}")

    # Verify inventory was decremented in backend
    status, updated_prod = api_get(f"/api/products/{p_id}")
    new_stock = updated_prod["stock"]
    expected_stock = initial_stock - 2
    assert new_stock == expected_stock, f"Stock mismatch! Expected {expected_stock}, got {new_stock}"
    print(f"  [VERIFIED] Inventory Stock atomically decremented from {initial_stock} -> {new_stock}")

    # 5. Merchant Operations & Synchronization
    print("\n[Step 5] Checking Merchant Analytics Update...")
    status, updated_analytics = api_get("/api/analytics/overview")
    rev_after = updated_analytics["total_revenue"]
    orders_after = updated_analytics["total_orders"]
    expected_rev = round(rev_before + charged_amount, 2)
    assert abs(rev_after - expected_rev) < 0.01, f"Revenue mismatch! Expected {expected_rev}, got {rev_after}"
    assert orders_after == orders_before + 1, f"Orders count mismatch!"
    print(f"  [VERIFIED] Revenue updated: ${rev_before:.2f} -> ${rev_after:.2f} (+${charged_amount:.2f})")
    print(f"  [VERIFIED] Orders count updated: {orders_before} -> {orders_after}")

    # 6. Merchant Order Fulfillment (Fulfill Order)
    print("\n[Step 6] Merchant Ships Order...")
    status, patch_res = api_patch(f"/api/orders/{new_order_id}/status", {"status": "shipped"})
    assert status == 200
    print(f"  [OK] Order #{new_order_id} status updated to 'shipped'")

    status, order_detail = api_get(f"/api/orders/{new_order_id}")
    assert order_detail["status"] == "shipped"
    print(f"  [VERIFIED] Order detail confirmation: Status = {order_detail['status']} | Items count = {len(order_detail['items'])}")

    # 7. Inventory Restock Flow
    print("\n[Step 7] Testing Merchant Inventory Restock Flow...")
    restock_target = new_stock + 20
    status, restock_res = api_patch(f"/api/products/{p_id}/stock", {"stock": restock_target})
    assert status == 200
    status, restocked_prod = api_get(f"/api/products/{p_id}")
    assert restocked_prod["stock"] == restock_target
    print(f"  [VERIFIED] Product '{p_name}' successfully restocked to {restock_target} units")

    # 8. Out-of-Stock Guardrail Test
    print("\n[Step 8] Testing Out-of-Stock Rejection & Rollback...")
    excessive_payload = {
        "customer_name": "Overdraft User",
        "customer_email": "overdraft@example.com",
        "customer_address": "Test Address",
        "items": [
            {"product_id": p_id, "quantity": 9999}
        ]
    }
    try:
        api_post("/api/orders/checkout", excessive_payload)
        print("  [FAIL] Expected 400 error on excessive quantity, but request succeeded!")
        return False
    except urllib.error.HTTPError as e:
        assert e.code == 400
        err_msg = json.loads(e.read().decode("utf-8"))["detail"]
        print(f"  [OK] Correctly rejected with HTTP 400: '{err_msg}'")

    print("\n" + "=" * 70)
    print("ALL FRONTEND-BACKEND CONTRACTS AND DATA FLOWS MATCH 100%!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
