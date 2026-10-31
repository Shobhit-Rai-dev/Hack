from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import Product
from app.schemas.domain import ProductCreateRequest, ProductResponse
from app.api.deps import get_current_user, require_roles
from app.utils.money import round_currency, to_decimal

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    products = db.query(Product).filter(Product.is_active == True).all()
    results = []
    for p in products:
        variants = [
            {
                "id": v.id,
                "variant_name": v.variant_name,
                "price_adjustment": float(round_currency(to_decimal(v.price_adjustment)))
            }
            for v in p.variants
        ]
        results.append({
            "id": p.id,
            "name": p.name,
            "product_type": p.product_type,
            "sales_price": float(round_currency(to_decimal(p.sales_price))),
            "cost_price": float(round_currency(to_decimal(p.cost_price))),
            "description": p.description,
            "notes": p.notes,
            "variants": variants
        })
    return results

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    req: ProductCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "STAFF"))
):
    product = Product(
        name=req.name.strip(),
        product_type=req.product_type,
        sales_price=round_currency(to_decimal(req.sales_price)),
        cost_price=round_currency(to_decimal(req.cost_price)),
        description=req.description,
        notes=req.notes,
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    return {
        "id": product.id,
        "name": product.name,
        "product_type": product.product_type,
        "sales_price": float(round_currency(to_decimal(product.sales_price))),
        "cost_price": float(round_currency(to_decimal(product.cost_price))),
        "description": product.description,
        "notes": product.notes,
        "variants": []
    }
