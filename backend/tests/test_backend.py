import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db
from scripts.seed_demo import run_seed

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_subscriptiq.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    run_seed()
    yield
    Base.metadata.drop_all(bind=engine)

def get_auth_token(email: str, password: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]

# --- Core App & Health ---
def test_health_check():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "system" in data

# --- Authentication Tests ---
def test_login_success():
    res = client.post("/api/auth/login", json={"email": "admin@subscriptiq.com", "password": "Admin@123!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "ADMIN"
    assert data["user"]["email"] == "admin@subscriptiq.com"

def test_login_invalid_password():
    res = client.post("/api/auth/login", json={"email": "admin@subscriptiq.com", "password": "WrongPassword!"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid email or password."

def test_login_unknown_user():
    res = client.post("/api/auth/login", json={"email": "nonexistent@subscriptiq.com", "password": "Password@123!"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid email or password."

def test_unauthenticated_request_rejected():
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 401

def test_invalid_token_rejected():
    res = client.get("/api/dashboard/summary", headers={"Authorization": "Bearer totally-invalid-token"})
    assert res.status_code == 401

# --- Role-Based Authorization Tests ---
def test_staff_role_restriction_on_discounts():
    token = get_auth_token("staff@subscriptiq.com", "Staff@123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Staff must be forbidden from creating discount rules
    res = client.post("/api/discounts", json={
        "name": "STAFF_DISC",
        "discount_type": "Percentage",
        "discount_value": 5.0
    }, headers=headers)
    assert res.status_code == 403

def test_staff_cannot_manage_staff():
    token = get_auth_token("staff@subscriptiq.com", "Staff@123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Staff cannot list staff accounts
    res = client.get("/api/users", headers=headers)
    assert res.status_code == 403

    # Staff cannot enroll new staff
    res2 = client.post("/api/users/staff", json={
        "full_name": "Rogue Officer",
        "email": "rogue@subscriptiq.com",
        "password": "Password@123!"
    }, headers=headers)
    assert res2.status_code == 403

def test_customer_isolation():
    token = get_auth_token("bruce@waynecorp.com", "Customer@123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Bruce cannot inspect Stark's invoice (invoice 2 belongs to Tony Stark)
    res = client.get("/api/invoices/2", headers=headers)
    assert res.status_code == 403

    # Bruce CAN inspect his own invoice (invoice 1 belongs to Bruce Wayne)
    res_own = client.get("/api/invoices/1", headers=headers)
    assert res_own.status_code == 200
    assert res_own.json()["customer_name"] == "Bruce Wayne"

def test_customer_cannot_access_administrative_features():
    token = get_auth_token("bruce@waynecorp.com", "Customer@123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Customers cannot view general customer registry
    assert client.get("/api/customers", headers=headers).status_code == 403

    # Customers cannot trigger billing generation
    assert client.post("/api/invoices/generate", headers=headers).status_code == 403

    # Customers cannot record arbitrary payments
    assert client.post("/api/payments", json={
        "invoice_id": 1,
        "payment_method": "Cash",
        "amount": 100.0
    }, headers=headers).status_code == 403

# --- Billing Engine & Invoices ---
def test_invoice_generation_idempotency():
    token = get_auth_token("admin@subscriptiq.com", "Admin@123!")
    headers = {"Authorization": f"Bearer {token}"}

    # First run generates eligible due invoices
    res1 = client.post("/api/invoices/generate", headers=headers)
    assert res1.status_code == 200
    created_count = res1.json()["invoices_created"]
    assert created_count >= 1

    # Immediate second run must be idempotent (0 new invoices)
    res2 = client.post("/api/invoices/generate", headers=headers)
    assert res2.status_code == 200
    assert res2.json()["invoices_created"] == 0

# --- Payments & Outstanding Balances ---
def test_payment_and_overpayment_rejection():
    token = get_auth_token("admin@subscriptiq.com", "Admin@123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to overpay invoice 2 (balance is 35400)
    res = client.post("/api/payments", json={
        "invoice_id": 2,
        "payment_method": "UPI",
        "amount": 99999.00
    }, headers=headers)
    assert res.status_code == 400
    assert "exceeds balance due" in res.json()["detail"]

    # Valid partial payment of 10000
    pay_res = client.post("/api/payments", json={
        "invoice_id": 2,
        "payment_method": "UPI",
        "amount": 10000.00
    }, headers=headers)
    assert pay_res.status_code == 201
    assert pay_res.json()["invoice_status"] == "Partially Paid"
    assert pay_res.json()["balance_due"] == 25400.0

# --- Dashboard & Analytics ---
def test_dashboard_summary_admin():
    token = get_auth_token("admin@subscriptiq.com", "Admin@123!")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/dashboard/summary", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "kpis" in data
    kpis = data["kpis"]
    assert "monthly_recurring_revenue" in kpis
    assert "active_subscriptions" in kpis
    assert "payments_collected" in kpis
    assert "outstanding_balance" in kpis
    assert "overdue_balance" in kpis

    assert isinstance(kpis["monthly_recurring_revenue"], (int, float))
    assert kpis["active_subscriptions"] >= 1
    assert "insights" in data
    assert "revenue_trend" in data
    assert len(data["revenue_trend"]) >= 1

# --- Quotation Conversion ---
def test_quotation_conversion_duplicate_prevention():
    token = get_auth_token("admin@subscriptiq.com", "Admin@123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Quotation 1 is already converted in seed
    res = client.post("/api/quotations/1/convert", headers=headers)
    assert res.status_code == 400
    assert "already been converted" in res.json()["detail"]

# --- Customer Creation ---
def test_customer_creation_and_duplicate_email():
    token = get_auth_token("admin@subscriptiq.com", "Admin@123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to create customer with existing email
    res = client.post("/api/customers", json={
        "full_name": "Duplicate Bruce",
        "email": "bruce@waynecorp.com"
    }, headers=headers)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]

    # Valid new customer
    res2 = client.post("/api/customers", json={
        "full_name": "Arthur Curry",
        "email": "arthur@atlantis.gov",
        "company_name": "Kingdom of Atlantis",
        "phone": "+1-555-0800"
    }, headers=headers)
    assert res2.status_code == 201
    assert res2.json()["full_name"] == "Arthur Curry"