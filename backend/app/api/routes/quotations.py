from datetime import date, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import (
    Quotation, QuotationItem, QuotationTemplate, QuotationTemplateItem,
    Subscription, SubscriptionItem, SubscriptionPlan, Customer, Product
)
from app.schemas.domain import (
    QuotationResponse, QuotationTemplateCreateRequest, QuotationTemplateResponse
)
from app.api.deps import get_current_user, require_roles
from app.services.billing import advance_date_by_frequency
from app.services.pricing import calculate_financials
from app.utils.money import round_currency, to_decimal

router = APIRouter(tags=["Quotations & Templates"])

# --- Quotations ---
@router.get("/api/quotations", response_model=List[QuotationResponse])
def list_quotations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Quotation).order_by(Quotation.id.desc())
    if current_user["role"] == "CUSTOMER":
        cust_id = current_user.get("customer_id")
        if not cust_id:
            return []
        query = query.filter(Quotation.customer_id == cust_id)

    quotations = query.all()
    results = []
    for q in quotations:
        results.append({
            "id": q.id,
            "quotation_number": q.quotation_number,
            "customer_name": q.customer.full_name if q.customer else "Unknown",
            "plan_name": q.plan.name if q.plan else "Standard",
            "quotation_date": q.quotation_date.isoformat() if q.quotation_date else "",
            "expiry_date": q.expiry_date.isoformat() if q.expiry_date else "",
            "status": q.status,
            "total_amount": float(round_currency(to_decimal(q.total_amount)))
        })
    return results

@router.post("/api/quotations/{id}/convert")
def convert_quotation(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "STAFF"))
):
    quotation = db.query(Quotation).filter(Quotation.id == id).first()
    if not quotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found.")

    if quotation.status == "Converted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quotation has already been converted to a subscription."
        )

    if not quotation.plan_id:
        # Default to first available plan if none specified
        first_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).first()
        if not first_plan:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active plan available to convert.")
        quotation.plan_id = first_plan.id

    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == quotation.plan_id).first()
    today = date.today()
    next_billing = advance_date_by_frequency(today, plan.billing_frequency)

    sub_count = db.query(Subscription).count() + 1
    sub_num = f"SUB-{today.strftime('%Y%m')}-{sub_count:04d}"

    subscription = Subscription(
        subscription_number=sub_num,
        customer_id=quotation.customer_id,
        plan_id=quotation.plan_id,
        quotation_id=quotation.id,
        start_date=today,
        next_billing_date=next_billing,
        status="Active",
        subtotal=round_currency(to_decimal(quotation.subtotal)),
        discount_amount=round_currency(to_decimal(quotation.discount_amount)),
        tax_amount=round_currency(to_decimal(quotation.tax_amount)),
        total_amount=round_currency(to_decimal(quotation.total_amount)),
        payment_terms="Net 15"
    )
    db.add(subscription)
    db.flush()

    for item in quotation.items:
        sub_item = SubscriptionItem(
            subscription_id=subscription.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=round_currency(to_decimal(item.unit_price)),
            line_total=round_currency(to_decimal(item.line_total)),
            description=item.description
        )
        db.add(sub_item)

    quotation.status = "Converted"
    db.commit()

    return {
        "message": "Quotation successfully converted to subscription.",
        "subscription_number": sub_num,
        "subscription_id": subscription.id
    }

# --- Quotation Templates ---
@router.get("/api/quotation-templates", response_model=List[QuotationTemplateResponse])
def list_quotation_templates(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    templates = db.query(QuotationTemplate).all()
    results = []
    for t in templates:
        items = [
            {
                "id": it.id,
                "product_id": it.product_id,
                "product_name": it.product.name if it.product else "",
                "quantity": it.quantity,
                "description": it.description
            }
            for it in t.items
        ]
        results.append({
            "id": t.id,
            "name": t.name,
            "plan_id": t.plan_id,
            "plan_name": t.plan.name if t.plan else "",
            "billing_frequency": t.plan.billing_frequency if t.plan else "Monthly",
            "validity_days": t.validity_days,
            "notes": t.notes,
            "items": items
        })
    return results

@router.post("/api/quotation-templates", response_model=QuotationTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_quotation_template(
    req: QuotationTemplateCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "STAFF"))
):
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == req.plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected plan does not exist.")

    template = QuotationTemplate(
        name=req.name.strip(),
        plan_id=req.plan_id,
        validity_days=req.validity_days,
        notes=req.notes
    )
    db.add(template)
    db.flush()

    template_items = []
    for it in req.items:
        prod = db.query(Product).filter(Product.id == it.product_id).first()
        if not prod:
            continue
        t_item = QuotationTemplateItem(
            template_id=template.id,
            product_id=it.product_id,
            quantity=it.quantity,
            description=it.description or prod.name
        )
        db.add(t_item)
        db.flush()
        template_items.append({
            "id": t_item.id,
            "product_id": prod.id,
            "product_name": prod.name,
            "quantity": it.quantity,
            "description": t_item.description
        })

    db.commit()
    db.refresh(template)

    return {
        "id": template.id,
        "name": template.name,
        "plan_id": template.plan_id,
        "plan_name": plan.name,
        "billing_frequency": plan.billing_frequency,
        "validity_days": template.validity_days,
        "notes": template.notes,
        "items": template_items
    }
