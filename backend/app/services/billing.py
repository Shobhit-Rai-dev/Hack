import calendar
from datetime import date, timedelta
from decimal import Decimal
from typing import Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.entities import Subscription, Invoice, InvoiceItem, SubscriptionPlan
from app.utils.money import round_currency, to_decimal

def advance_date_by_frequency(current_date: date, frequency: str) -> date:
    freq = (frequency or "").strip().lower()
    if freq == "daily":
        return current_date + timedelta(days=1)
    elif freq == "weekly":
        return current_date + timedelta(days=7)
    elif freq == "monthly":
        year = current_date.year
        month = current_date.month + 1
        if month > 12:
            month = 1
            year += 1
        max_day = calendar.monthrange(year, month)[1]
        day = min(current_date.day, max_day)
        return date(year, month, day)
    elif freq == "yearly":
        year = current_date.year + 1
        month = current_date.month
        max_day = calendar.monthrange(year, month)[1]
        day = min(current_date.day, max_day)
        return date(year, month, day)
    else:
        return current_date + timedelta(days=30)

def generate_due_invoices(db: Session, target_date: date = None) -> int:
    """
    Scans for active subscriptions whose next_billing_date <= target_date,
    and generates exactly one invoice per subscription per billing cycle idempotently.
    Returns the number of new invoices created.
    """
    if target_date is None:
        target_date = date.today()

    eligible_subs = db.query(Subscription).join(SubscriptionPlan).filter(
        Subscription.status == "Active",
        Subscription.next_billing_date <= target_date
    ).all()

    created_count = 0

    for sub in eligible_subs:
        period_start = sub.next_billing_date
        plan_freq = sub.plan.billing_frequency if sub.plan else "Monthly"
        next_cycle_date = advance_date_by_frequency(period_start, plan_freq)
        period_end = next_cycle_date - timedelta(days=1)

        # 1. Idempotency Check: Don't generate if an invoice already exists for this subscription and period
        existing_invoice = db.query(Invoice).filter(
            Invoice.subscription_id == sub.id,
            Invoice.billing_period_start == period_start
        ).first()

        if existing_invoice:
            continue

        # Due date: Net 15 days or payment terms
        due_date = period_start + timedelta(days=15)

        # Generate unique invoice number
        count_all = db.query(Invoice).count() + 1 + created_count
        inv_number = f"INV-{period_start.strftime('%Y%m')}-{count_all:04d}"

        invoice = Invoice(
            invoice_number=inv_number,
            customer_id=sub.customer_id,
            subscription_id=sub.id,
            issue_date=period_start,
            due_date=due_date,
            billing_period_start=period_start,
            billing_period_end=period_end,
            subtotal=round_currency(to_decimal(sub.subtotal)),
            discount_amount=round_currency(to_decimal(sub.discount_amount)),
            tax_amount=round_currency(to_decimal(sub.tax_amount)),
            total_amount=round_currency(to_decimal(sub.total_amount)),
            amount_paid=Decimal("0.00"),
            balance_due=round_currency(to_decimal(sub.total_amount)),
            status="Confirmed"
        )
        db.add(invoice)
        db.flush()  # to obtain invoice.id

        # Copy line items
        for item in sub.items:
            inv_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item.product_id,
                description=item.description or (item.product.name if item.product else "Service Item"),
                quantity=item.quantity,
                unit_price=round_currency(to_decimal(item.unit_price)),
                line_total=round_currency(to_decimal(item.line_total))
            )
            db.add(inv_item)

        # Advance subscription next_billing_date
        sub.next_billing_date = next_cycle_date

        # Check end date behavior
        if sub.end_date and sub.next_billing_date > sub.end_date:
            behavior = sub.plan.behavior_at_end if sub.plan else "Close automatically"
            if behavior == "Close automatically":
                sub.status = "Closed"
            elif behavior == "Pause":
                sub.status = "Paused"

        try:
            db.commit()
            created_count += 1
        except IntegrityError:
            db.rollback()
            continue

    return created_count
