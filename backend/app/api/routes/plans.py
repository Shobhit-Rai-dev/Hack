from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import SubscriptionPlan
from app.schemas.domain import PlanCreateRequest, PlanResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/api/plans", tags=["Subscription Plans"])

@router.get("", response_model=List[PlanResponse])
def list_plans(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    plans = db.query(SubscriptionPlan).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "billing_frequency": p.billing_frequency,
            "minimum_quantity": p.minimum_quantity,
            "behavior_at_end": p.behavior_at_end,
            "is_active": p.is_active
        }
        for p in plans
    ]

@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    req: PlanCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "STAFF"))
):
    plan = SubscriptionPlan(
        name=req.name.strip(),
        description=req.description,
        billing_frequency=req.billing_frequency,
        minimum_quantity=req.minimum_quantity,
        behavior_at_end=req.behavior_at_end,
        is_active=True
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return {
        "id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "billing_frequency": plan.billing_frequency,
        "minimum_quantity": plan.minimum_quantity,
        "behavior_at_end": plan.behavior_at_end,
        "is_active": plan.is_active
    }
