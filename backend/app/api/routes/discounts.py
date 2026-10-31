from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import DiscountRule
from app.schemas.domain import DiscountCreateRequest, DiscountResponse
from app.api.deps import require_roles
from app.utils.money import round_currency, to_decimal

router = APIRouter(prefix="/api/discounts", tags=["Discounts"])

@router.get("", response_model=List[DiscountResponse])
def list_discounts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "STAFF"))
):
    discounts = db.query(DiscountRule).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "discount_type": d.discount_type,
            "discount_value": float(round_currency(to_decimal(d.discount_value))),
            "minimum_purchase": float(round_currency(to_decimal(d.minimum_purchase))),
            "usage_limit": d.usage_limit,
            "usage_count": d.usage_count,
            "is_active": d.is_active
        }
        for d in discounts
    ]

@router.post("", response_model=DiscountResponse, status_code=status.HTTP_201_CREATED)
def create_discount(
    req: DiscountCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN"))
):
    existing = db.query(DiscountRule).filter(DiscountRule.name == req.name.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A discount rule with this name or code already exists."
        )

    discount = DiscountRule(
        name=req.name.strip(),
        discount_type=req.discount_type,
        discount_value=round_currency(to_decimal(req.discount_value)),
        minimum_purchase=round_currency(to_decimal(req.minimum_purchase)),
        usage_limit=req.usage_limit,
        usage_count=0,
        is_active=True
    )
    db.add(discount)
    db.commit()
    db.refresh(discount)

    return {
        "id": discount.id,
        "name": discount.name,
        "discount_type": discount.discount_type,
        "discount_value": float(round_currency(to_decimal(discount.discount_value))),
        "minimum_purchase": float(round_currency(to_decimal(discount.minimum_purchase))),
        "usage_limit": discount.usage_limit,
        "usage_count": discount.usage_count,
        "is_active": discount.is_active
    }

@router.patch("/{id}/status")
def toggle_discount_status(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN"))
):
    discount = db.query(DiscountRule).filter(DiscountRule.id == id).first()
    if not discount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discount rule not found.")

    discount.is_active = not discount.is_active
    db.commit()
    db.refresh(discount)

    return {
        "id": discount.id,
        "name": discount.name,
        "is_active": discount.is_active,
        "message": f"Discount rule status changed to {'active' if discount.is_active else 'disabled'}."
    }
