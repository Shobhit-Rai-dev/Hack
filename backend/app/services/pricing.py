from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.utils.money import round_currency, to_decimal
from app.models.entities import Product, ProductVariant, TaxRule, DiscountRule

def compute_product_effective_price(
    product: Product,
    selected_variant_ids: Optional[List[int]] = None
) -> Decimal:
    """Computes the effective sales price of a product including any selected variant adjustments."""
    base_price = to_decimal(product.sales_price)
    if not selected_variant_ids or not product.variants:
        return round_currency(base_price)
    
    adjustment_total = Decimal("0.00")
    for variant in product.variants:
        if variant.id in selected_variant_ids:
            adjustment_total += to_decimal(variant.price_adjustment)
            
    return round_currency(base_price + adjustment_total)

def calculate_financials(
    db: Session,
    items_data: List[dict],  # list of {"product_id": int, "quantity": int, "unit_price": Optional[Decimal], "variant_ids": Optional[List[int]]}
    discount_rule_id: Optional[int] = None,
    tax_rule_id: Optional[int] = None,
) -> Tuple[Decimal, Decimal, Decimal, Decimal, List[dict]]:
    """
    Computes subtotal, discount, tax, total, and prepared line items.
    Returns: (subtotal, discount_amount, tax_amount, total_amount, evaluated_items)
    """
    subtotal = Decimal("0.00")
    evaluated_items = []

    for item in items_data:
        qty = int(item.get("quantity", 1))
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not product:
            continue

        if item.get("unit_price") is not None:
            unit_price = round_currency(to_decimal(item["unit_price"]))
        else:
            unit_price = compute_product_effective_price(product, item.get("variant_ids"))

        line_total = round_currency(unit_price * qty)
        subtotal += line_total

        desc = item.get("description") or product.name
        evaluated_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": qty,
            "unit_price": unit_price,
            "line_total": line_total,
            "description": desc
        })

    subtotal = round_currency(subtotal)

    # 1. Calculate Discount
    discount_amount = Decimal("0.00")
    if discount_rule_id:
        discount = db.query(DiscountRule).filter(DiscountRule.id == discount_rule_id, DiscountRule.is_active == True).first()
        if discount:
            min_purchase = to_decimal(discount.minimum_purchase)
            if subtotal >= min_purchase:
                if discount.usage_limit is None or discount.usage_count < discount.usage_limit:
                    if discount.discount_type == "Percentage":
                        rate = to_decimal(discount.discount_value) / Decimal("100.00")
                        discount_amount = round_currency(subtotal * rate)
                    else:
                        discount_amount = round_currency(to_decimal(discount.discount_value))
                    
                    if discount_amount > subtotal:
                        discount_amount = subtotal

    discount_amount = round_currency(discount_amount)
    taxable_base = max(Decimal("0.00"), subtotal - discount_amount)

    # 2. Calculate Tax
    tax_amount = Decimal("0.00")
    if tax_rule_id:
        tax = db.query(TaxRule).filter(TaxRule.id == tax_rule_id, TaxRule.is_active == True).first()
        if tax:
            rate = to_decimal(tax.rate) / Decimal("100.00")
            tax_amount = round_currency(taxable_base * rate)
    else:
        # Default active tax if any
        taxes = db.query(TaxRule).filter(TaxRule.is_active == True).all()
        for t in taxes:
            rate = to_decimal(t.rate) / Decimal("100.00")
            tax_amount += round_currency(taxable_base * rate)

    tax_amount = round_currency(tax_amount)
    total_amount = round_currency(max(Decimal("0.00"), taxable_base + tax_amount))

    return subtotal, discount_amount, tax_amount, total_amount, evaluated_items
