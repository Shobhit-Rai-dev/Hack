from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import Invoice
from app.schemas.domain import InvoiceListResponse, InvoiceDetailResponse
from app.api.deps import get_current_user, require_roles
from app.services.billing import generate_due_invoices
from app.utils.money import round_currency, to_decimal

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])

@router.get("", response_model=List[InvoiceListResponse])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Invoice).order_by(Invoice.id.desc())
    if current_user["role"] == "CUSTOMER":
        cust_id = current_user.get("customer_id")
        if not cust_id:
            return []
        query = query.filter(Invoice.customer_id == cust_id)

    invoices = query.all()
    results = []
    for inv in invoices:
        results.append({
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "customer_name": inv.customer.full_name if inv.customer else "Unknown",
            "subscription_number": inv.subscription.subscription_number if inv.subscription else "—",
            "due_date": inv.due_date.isoformat() if inv.due_date else "",
            "status": inv.status,
            "total_amount": float(round_currency(to_decimal(inv.total_amount))),
            "balance_due": float(round_currency(to_decimal(inv.balance_due)))
        })
    return results

@router.get("/{id}", response_model=InvoiceDetailResponse)
def get_invoice(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    invoice = db.query(Invoice).filter(Invoice.id == id).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice record not found.")

    if current_user["role"] == "CUSTOMER":
        cust_id = current_user.get("customer_id")
        if invoice.customer_id != cust_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access restricted. You cannot inspect other customers' invoices."
            )

    items = [
        {
            "id": it.id,
            "description": it.description,
            "quantity": it.quantity,
            "unit_price": float(round_currency(to_decimal(it.unit_price))),
            "line_total": float(round_currency(to_decimal(it.line_total)))
        }
        for it in invoice.items
    ]

    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "customer_name": invoice.customer.full_name if invoice.customer else "Unknown",
        "company_name": invoice.customer.company_name if invoice.customer else None,
        "billing_address": invoice.customer.billing_address if invoice.customer else None,
        "subscription_number": invoice.subscription.subscription_number if invoice.subscription else "—",
        "issue_date": invoice.issue_date.isoformat() if invoice.issue_date else "",
        "due_date": invoice.due_date.isoformat() if invoice.due_date else "",
        "billing_period_start": invoice.billing_period_start.isoformat() if invoice.billing_period_start else None,
        "billing_period_end": invoice.billing_period_end.isoformat() if invoice.billing_period_end else None,
        "subtotal": float(round_currency(to_decimal(invoice.subtotal))),
        "discount_amount": float(round_currency(to_decimal(invoice.discount_amount))),
        "tax_amount": float(round_currency(to_decimal(invoice.tax_amount))),
        "total_amount": float(round_currency(to_decimal(invoice.total_amount))),
        "amount_paid": float(round_currency(to_decimal(invoice.amount_paid))),
        "balance_due": float(round_currency(to_decimal(invoice.balance_due))),
        "status": invoice.status,
        "items": items
    }

@router.post("/generate")
def trigger_billing(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "STAFF"))
):
    created_count = generate_due_invoices(db)
    return {
        "message": f"Billing cycle completed. {created_count} new invoice(s) generated.",
        "invoices_created": created_count
    }
