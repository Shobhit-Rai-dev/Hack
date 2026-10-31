from datetime import date
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import Payment, Invoice
from app.schemas.domain import PaymentCreateRequest, PaymentResponse, PaymentRecordResult
from app.api.deps import get_current_user, require_roles
from app.utils.money import round_currency, to_decimal

router = APIRouter(prefix="/api/payments", tags=["Payments"])

@router.get("", response_model=List[PaymentResponse])
def list_payments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Payment).order_by(Payment.id.desc())
    if current_user["role"] == "CUSTOMER":
        cust_id = current_user.get("customer_id")
        if not cust_id:
            return []
        query = query.filter(Payment.customer_id == cust_id)

    payments = query.all()
    results = []
    for p in payments:
        results.append({
            "id": p.id,
            "payment_reference": p.payment_reference,
            "invoice_number": p.invoice.invoice_number if p.invoice else "—",
            "customer_name": p.customer.full_name if p.customer else "Unknown",
            "payment_date": p.payment_date.isoformat() if p.payment_date else "",
            "payment_method": p.payment_method,
            "status": p.status,
            "amount": float(round_currency(to_decimal(p.amount)))
        })
    return results

@router.post("", response_model=PaymentRecordResult, status_code=status.HTTP_201_CREATED)
def record_payment(
    req: PaymentCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "STAFF"))
):
    invoice = db.query(Invoice).filter(Invoice.id == req.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice record not found.")

    payment_amt = round_currency(to_decimal(req.amount))
    if payment_amt <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment amount must be greater than zero.")

    current_balance = round_currency(to_decimal(invoice.balance_due))
    if payment_amt > current_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount of ₹{payment_amt} exceeds balance due of ₹{current_balance}."
        )

    # Parse date
    pay_date = date.today()
    if req.payment_date:
        try:
            pay_date = date.fromisoformat(req.payment_date)
        except ValueError:
            pay_date = date.today()

    count = db.query(Payment).count() + 1
    pay_ref = f"PAY-{pay_date.strftime('%Y%m')}-{count:04d}"

    payment = Payment(
        payment_reference=pay_ref,
        invoice_id=invoice.id,
        customer_id=invoice.customer_id,
        amount=payment_amt,
        payment_method=req.payment_method,
        payment_date=pay_date,
        note=req.note,
        status="Settled"
    )
    db.add(payment)

    # Update invoice totals and status atomically
    new_paid = round_currency(to_decimal(invoice.amount_paid) + payment_amt)
    new_balance = round_currency(to_decimal(invoice.balance_due) - payment_amt)
    invoice.amount_paid = new_paid
    invoice.balance_due = new_balance

    if new_balance <= Decimal("0.00"):
        invoice.status = "Paid"
    else:
        invoice.status = "Partially Paid"

    db.commit()
    db.refresh(invoice)
    db.refresh(payment)

    return {
        "id": payment.id,
        "payment_reference": payment.payment_reference,
        "invoice_status": invoice.status,
        "balance_due": float(invoice.balance_due),
        "amount": float(payment.amount)
    }
