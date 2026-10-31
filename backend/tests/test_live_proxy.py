import httpx

BASE_URL = "http://localhost:5173/api"

def run_live_proxy_tests():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    print("1. Testing Admin Login...")
    res = client.post("/auth/login", json={"email": "admin@subscriptiq.com", "password": "Admin@123!"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("   -> Success! Admin token obtained.")

    print("2. Testing Dashboard Summary...")
    res = client.get("/dashboard/summary", headers=admin_headers)
    assert res.status_code == 200
    summary = res.json()
    assert "kpis" in summary
    assert "monthly_recurring_revenue" in summary["kpis"]
    print(f"   -> Success! MRR: ₹{summary['kpis']['monthly_recurring_revenue']:,}")

    print("3. Testing Customers Listing & Creation...")
    res = client.get("/customers", headers=admin_headers)
    assert res.status_code == 200
    custs = res.json()
    assert len(custs) >= 1
    print(f"   -> Success! Retrieved {len(custs)} customers.")

    print("4. Testing Products & Variants...")
    res = client.get("/products", headers=admin_headers)
    assert res.status_code == 200
    prods = res.json()
    assert len(prods) >= 1
    print(f"   -> Success! Retrieved {len(prods)} products.")

    print("5. Testing Subscription Plans...")
    res = client.get("/plans", headers=admin_headers)
    assert res.status_code == 200
    plans = res.json()
    assert len(plans) >= 1
    print(f"   -> Success! Retrieved {len(plans)} plans.")

    print("6. Testing Quotation Templates & Quotations...")
    res_t = client.get("/quotation-templates", headers=admin_headers)
    assert res_t.status_code == 200
    res_q = client.get("/quotations", headers=admin_headers)
    assert res_q.status_code == 200
    print(f"   -> Success! Templates: {len(res_t.json())}, Quotations: {len(res_q.json())}.")

    print("7. Testing Subscriptions...")
    res = client.get("/subscriptions", headers=admin_headers)
    assert res.status_code == 200
    subs = res.json()
    assert len(subs) >= 1
    print(f"   -> Success! Retrieved {len(subs)} subscriptions.")

    print("8. Testing Invoices & Due Invoice Generation...")
    res_gen = client.post("/invoices/generate", headers=admin_headers)
    assert res_gen.status_code == 200
    print(f"   -> Success! Generated {res_gen.json()['invoices_created']} due invoices.")

    res_inv = client.get("/invoices", headers=admin_headers)
    assert res_inv.status_code == 200
    invs = res_inv.json()
    assert len(invs) >= 2
    print(f"   -> Success! Retrieved {len(invs)} invoices.")

    print("9. Testing Invoice Detail Inspection...")
    res_inv_det = client.get(f"/invoices/{invs[0]['id']}", headers=admin_headers)
    assert res_inv_det.status_code == 200
    assert "items" in res_inv_det.json()
    print("   -> Success! Invoice detail and printable items loaded.")

    print("10. Testing Payments Listing...")
    res = client.get("/payments", headers=admin_headers)
    assert res.status_code == 200
    print(f"   -> Success! Retrieved {len(res.json())} payments.")

    print("11. Testing Taxes & Discounts...")
    res_tax = client.get("/taxes", headers=admin_headers)
    assert res_tax.status_code == 200
    res_disc = client.get("/discounts", headers=admin_headers)
    assert res_disc.status_code == 200
    print(f"   -> Success! Taxes: {len(res_tax.json())}, Discounts: {len(res_disc.json())}.")

    print("12. Testing Staff Management...")
    res_users = client.get("/users", headers=admin_headers)
    assert res_users.status_code == 200
    print(f"   -> Success! Retrieved {len(res_users.json())} personnel accounts.")

    print("13. Testing Customer Portal Isolation...")
    bruce_res = client.post("/auth/login", json={"email": "bruce@waynecorp.com", "password": "Customer@123!"})
    assert bruce_res.status_code == 200
    bruce_token = bruce_res.json()["access_token"]
    bruce_headers = {"Authorization": f"Bearer {bruce_token}"}

    # Bruce cannot view customer list
    assert client.get("/customers", headers=bruce_headers).status_code == 403
    # Bruce cannot inspect invoice 2 (Stark)
    assert client.get("/invoices/2", headers=bruce_headers).status_code == 403
    # Bruce CAN inspect invoice 1 (his own)
    assert client.get("/invoices/1", headers=bruce_headers).status_code == 200
    print("   -> Success! Customer isolation strictly verified.")

    print("\nALL 13 LIVE PROXY INTEGRATION FLOWS PASSED!")

if __name__ == "__main__":
   import httpx

BASE_URL = "http://localhost:5173/api"

def run_live_proxy_tests():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    print("1. Testing Admin Login...")
    res = client.post("/auth/login", json={"email": "admin@subscriptiq.com", "password": "Admin@123!"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("   -> Success! Admin token obtained.")

    print("2. Testing Dashboard Summary...")
    res = client.get("/dashboard/summary", headers=admin_headers)
    assert res.status_code == 200
    summary = res.json()
    assert "kpis" in summary
    assert "monthly_recurring_revenue" in summary["kpis"]
    print(f"   -> Success! MRR: INR {summary['kpis']['monthly_recurring_revenue']:,}")

    print("3. Testing Customers Listing & Creation...")
    res = client.get("/customers", headers=admin_headers)
    assert res.status_code == 200
    custs = res.json()
    assert len(custs) >= 1
    print(f"   -> Success! Retrieved {len(custs)} customers.")

    print("4. Testing Products & Variants...")
    res = client.get("/products", headers=admin_headers)
    assert res.status_code == 200
    prods = res.json()
    assert len(prods) >= 1
    print(f"   -> Success! Retrieved {len(prods)} products.")

    print("5. Testing Subscription Plans...")
    res = client.get("/plans", headers=admin_headers)
    assert res.status_code == 200
    plans = res.json()
    assert len(plans) >= 1
    print(f"   -> Success! Retrieved {len(plans)} plans.")

    print("6. Testing Quotation Templates & Quotations...")
    res_t = client.get("/quotation-templates", headers=admin_headers)
    assert res_t.status_code == 200
    res_q = client.get("/quotations", headers=admin_headers)
    assert res_q.status_code == 200
    print(f"   -> Success! Templates: {len(res_t.json())}, Quotations: {len(res_q.json())}.")

    print("7. Testing Subscriptions...")
    res = client.get("/subscriptions", headers=admin_headers)
    assert res.status_code == 200
    subs = res.json()
    assert len(subs) >= 1
    print(f"   -> Success! Retrieved {len(subs)} subscriptions.")

    print("8. Testing Invoices & Due Invoice Generation...")
    res_gen = client.post("/invoices/generate", headers=admin_headers)
    assert res_gen.status_code == 200
    print(f"   -> Success! Generated {res_gen.json()['invoices_created']} due invoices.")

    res_inv = client.get("/invoices", headers=admin_headers)
    assert res_inv.status_code == 200
    invs = res_inv.json()
    assert len(invs) >= 2
    print(f"   -> Success! Retrieved {len(invs)} invoices.")

    print("9. Testing Invoice Detail Inspection...")
    res_inv_det = client.get(f"/invoices/{invs[0]['id']}", headers=admin_headers)
    assert res_inv_det.status_code == 200
    assert "items" in res_inv_det.json()
    print("   -> Success! Invoice detail and printable items loaded.")

    print("10. Testing Payments Listing...")
    res = client.get("/payments", headers=admin_headers)
    assert res.status_code == 200
    print(f"   -> Success! Retrieved {len(res.json())} payments.")

    print("11. Testing Taxes & Discounts...")
    res_tax = client.get("/taxes", headers=admin_headers)
    assert res_tax.status_code == 200
    res_disc = client.get("/discounts", headers=admin_headers)
    assert res_disc.status_code == 200
    print(f"   -> Success! Taxes: {len(res_tax.json())}, Discounts: {len(res_disc.json())}.")

    print("12. Testing Staff Management...")
    res_users = client.get("/users", headers=admin_headers)
    assert res_users.status_code == 200
    print(f"   -> Success! Retrieved {len(res_users.json())} personnel accounts.")

    print("13. Testing Customer Portal Isolation...")
    bruce_res = client.post("/auth/login", json={"email": "bruce@waynecorp.com", "password": "Customer@123!"})
    assert bruce_res.status_code == 200
    bruce_token = bruce_res.json()["access_token"]
    bruce_headers = {"Authorization": f"Bearer {bruce_token}"}

    # Bruce cannot view customer list
    assert client.get("/customers", headers=bruce_headers).status_code == 403
    # Bruce cannot inspect invoice 2 (Stark)
    assert client.get("/invoices/2", headers=bruce_headers).status_code == 403
    # Bruce CAN inspect invoice 1 (his own)
    assert client.get("/invoices/1", headers=bruce_headers).status_code == 200
    print("   -> Success! Customer isolation strictly verified.")

    print("\nALL 13 LIVE PROXY INTEGRATION FLOWS PASSED!")

if __name__ == "__main__":
    run_live_proxy_tests()
