from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import User
from app.schemas.domain import StaffCreateRequest, UserResponse
from app.api.deps import require_roles
from app.core.security import get_password_hash, validate_password_strength

router = APIRouter(prefix="/api/users", tags=["Staff Management"])

@router.get("", response_model=List[UserResponse])
def list_staff(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN"))
):
    users = db.query(User).order_by(User.id.asc()).all()
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "customer_id": u.customer.id if u.customer else None
        }
        for u in users
    ]

@router.post("/staff", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_staff_member(
    req: StaffCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN"))
):
    valid, msg = validate_password_strength(req.password)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    existing = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user account with this email address already exists."
        )

    user = User(
        full_name=req.full_name.strip(),
        email=req.email.lower().strip(),
        password_hash=get_password_hash(req.password),
        role="STAFF",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "customer_id": None
    }

@router.patch("/{id}/status")
def toggle_user_status(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN"))
):
    if id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrative safety rule: Cannot modify your own account status."
        )

    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "message": f"User status changed to {'active' if user.is_active else 'suspended'}."
    }
