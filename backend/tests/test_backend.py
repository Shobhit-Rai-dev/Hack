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

def test_login_success():
    res = client.post("/api/auth/login", json={"email": "admin@subscriptiq.com", "password": "Admin@123!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "ADMIN"

def test_login_invalid_password():
    res = client.post("/api/auth/login", json={"email": "admin@subscriptiq.com", "password": "WrongPassword!"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid email or password."

def test_staff_role_restriction_on_discounts():
    staff_login = client.post("/api/auth/login", json={"email": "staff@subscriptiq.com", "password": "Staff@123!"})
    token = staff_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Staff must be forbidden from creating discount rules
    res = client.post("/api/discounts", json={
        "name": "STAFF_DISC",
        "discount_type": "Percentage",
        "discount_value": 5.0
    }, headers=headers)
    assert res.status_code == 403

def test_customer_isolation():
    bruce_login = client.post("/api/auth/login", json={"email": "bruce@waynecorp.com", "password": "Customer@123!"})
    token = bruce_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Bruce cannot inspect Stark's invoice (invoice 2 belongs to Tony Stark)
    res = client.get("/api/invoices/2", headers=headers)
    assert res.status_code == 403

def test_invoice_generation_idempotency():
    admin_login = client.post("/api/auth/login", json={"email": "admin@subscriptiq.com", "password": "Admin@123!"})
    token = admin_login.json()["access_token"]
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

def test_payment_and_overpayment_rejection():
    admin_login = client.post("/api/auth/login", json={"email": "admin@subscriptiq.com", "password": "Admin@123!"})
    token = admin_login.json()["access_token"]
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