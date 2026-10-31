from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import Subscription
from app.schemas.domain import SubscriptionResponse
from app.api.deps import get_current_user, require_roles
from app.utils.money import round_currency, to_decimal

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

@router.get("", response_model=List[SubscriptionResponse])
def list_subscriptions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Subscription).order_by(Subscription.id.desc())
    if current_user["role"] == "CUSTOMER":
        cust_id = current_user.get("customer_id")
        if not cust_id:
            return []
        query = query.filter(Subscription.customer_id == cust_id)

    subscriptions = query.all()
    results = []
    for s in subscriptions:
        results.append({
            "id": s.id,
            "subscription_number": s.subscription_number,
            "customer_name": s.customer.full_name if s.customer else "Unknown",
            "plan_name": s.plan.name if s.plan else "Custom Plan",
            "billing_frequency": s.plan.billing_frequency if s.plan else "Monthly",
            "start_date": s.start_date.isoformat() if s.start_date else "",
            "next_billing_date": s.next_billing_date.isoformat() if s.next_billing_date else "",
            "status": s.status,
            "total_amount": float(round_currency(to_decimal(s.total_amount)))
        })
    return results

@router.patch("/{id}/status")
def update_subscription_status(
    id: int,
    status_param: str = Query(..., alias="status"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "STAFF"))
):
    sub = db.query(Subscription).filter(Subscription.id == id).first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found.")

    allowed = ["Draft", "Confirmed", "Active", "Paused", "Closed"]
    matched_status = None
    for st in allowed:
        if st.lower() == status_param.strip().lower():
            matched_status = st
            break

    if not matched_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid subscription status. Allowed: {', '.join(allowed)}"
        )

    sub.status = matched_status
    db.commit()
    db.refresh(sub)

    return {
        "id": sub.id,
        "subscription_number": sub.subscription_number,
        "status": sub.status,
        "message": f"Subscription status updated to {sub.status}."
    }
