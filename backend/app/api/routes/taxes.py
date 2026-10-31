from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import TaxRule
from app.schemas.domain import TaxCreateRequest, TaxResponse
from app.api.deps import require_roles
from app.utils.money import round_currency, to_decimal

router = APIRouter(prefix="/api/taxes", tags=["Taxes"])

@router.get("", response_model=List[TaxResponse])
def list_taxes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "STAFF"))
):
    taxes = db.query(TaxRule).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "rate": float(round_currency(to_decimal(t.rate))),
            "applicable_to": t.applicable_to,
            "is_active": t.is_active
        }
        for t in taxes
    ]

@router.post("", response_model=TaxResponse, status_code=status.HTTP_201_CREATED)
def create_tax(
    req: TaxCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN"))
):
    tax = TaxRule(
        name=req.name.strip(),
        rate=round_currency(to_decimal(req.rate)),
        applicable_to=req.applicable_to,
        is_active=True
    )
    db.add(tax)
    db.commit()
    db.refresh(tax)

    return {
        "id": tax.id,
        "name": tax.name,
        "rate": float(round_currency(to_decimal(tax.rate))),
        "applicable_to": tax.applicable_to,
        "is_active": tax.is_active
    }

@router.patch("/{id}/status")
def toggle_tax_status(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN"))
):
    tax = db.query(TaxRule).filter(TaxRule.id == id).first()
    if not tax:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tax rule not found.")

    tax.is_active = not tax.is_active
    db.commit()
    db.refresh(tax)

    return {
        "id": tax.id,
        "name": tax.name,
        "is_active": tax.is_active,
        "message": f"Tax rule status changed to {'active' if tax.is_active else 'disabled'}."
    }
