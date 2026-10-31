from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import DashboardSummaryResponse
from app.api.deps import get_current_user
from app.services.analytics import get_dashboard_summary

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    customer_id = current_user.get("customer_id") if current_user["role"] == "CUSTOMER" else None
    return get_dashboard_summary(db, customer_id=customer_id)
