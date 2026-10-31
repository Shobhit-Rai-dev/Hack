from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import Customer, User, Invoice
from app.schemas.domain import CustomerCreateRequest, CustomerResponse
from app.api.deps import require_roles
from app.core.security import get_password_hash, validate_password_strength
from app.utils.money import round_currency, to_decimal

router = APIRouter(prefix="/api/customers", tags=["Customers"])

@router.get("", response_model=List[CustomerResponse])
def list_customers(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "STAFF"))
):
    customers = db.query(Customer).order_by(Customer.id.asc()).all()
    results = []
    for c in customers:
        # Compute outstanding balance for customer
        balance = db.query(Invoice).filter(
            Invoice.customer_id == c.id,
            Invoice.status.in_(["Confirmed", "Partially Paid", "Overdue"])
        ).all()
        total_balance = sum(to_decimal(i.balance_due) for i in balance)
        
        results.append({
            "id": c.id,
            "customer_number": c.customer_number,
            "full_name": c.full_name,
            "company_name": c.company_name,
            "email": c.email,
            "phone": c.phone,
            "user_id": c.user_id,
            "total_balance_due": float(round_currency(total_balance)),
            "billing_address": c.billing_address
        })
    return results

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    req: CustomerCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "STAFF"))
):
    existing = db.query(Customer).filter(Customer.email == req.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A customer with this email address already exists."
        )

    user_id = None
    if req.create_portal_account:
        if not req.portal_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portal password is required when creating portal credentials."
            )
        valid, msg = validate_password_strength(req.portal_password)
        if not valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        existing_user = db.query(User).filter(User.email == req.email.lower().strip()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user account with this email already exists."
            )

        new_user = User(
            full_name=req.full_name,
            email=req.email.lower().strip(),
            password_hash=get_password_hash(req.portal_password),
            role="CUSTOMER",
            is_active=True
        )
        db.add(new_user)
        db.flush()
        user_id = new_user.id

    cust_count = db.query(Customer).count() + 1
    cust_num = f"CUST-{cust_count:03d}"

    customer = Customer(
        user_id=user_id,
        customer_number=cust_num,
        full_name=req.full_name,
        email=req.email.lower().strip(),
        phone=req.phone,
        company_name=req.company_name,
        billing_address=req.billing_address
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)

    return {
        "id": customer.id,
        "customer_number": customer.customer_number,
        "full_name": customer.full_name,
        "company_name": customer.company_name,
        "email": customer.email,
        "phone": customer.phone,
        "user_id": customer.user_id,
        "total_balance_due": 0.0,
        "billing_address": customer.billing_address
    }
