from datetime import date
from decimal import Decimal
from typing import Dict, Any, List, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.entities import Subscription, Invoice, Payment, SubscriptionPlan
from app.utils.money import round_currency, to_decimal

def calculate_mrr(active_subscriptions: List[Subscription]) -> Decimal:
    mrr = Decimal("0.00")
    for sub in active_subscriptions:
        total = to_decimal(sub.total_amount)
        freq = sub.plan.billing_frequency.strip().lower() if sub.plan else "monthly"
        if freq == "daily":
            mrr += total * Decimal("30")
        elif freq == "weekly":
            mrr += (total * Decimal("52")) / Decimal("12")
        elif freq == "monthly":
            mrr += total
        elif freq == "yearly":
            mrr += total / Decimal("12")
        else:
            mrr += total
    return round_currency(mrr)

def get_dashboard_summary(db: Session, customer_id: Optional[int] = None) -> Dict[str, Any]:
    today = date.today()

    # Base queries filtered by customer_id if provided
    subs_q = db.query(Subscription).join(SubscriptionPlan).filter(Subscription.status == "Active")
    inv_q = db.query(Invoice).filter(Invoice.status != "Cancelled")
    pmt_q = db.query(Payment)

    if customer_id:
        subs_q = subs_q.filter(Subscription.customer_id == customer_id)
        inv_q = inv_q.filter(Invoice.customer_id == customer_id)
        pmt_q = pmt_q.filter(Payment.customer_id == customer_id)

    active_subs = subs_q.all()
    invoices = inv_q.all()
    payments = pmt_q.all()

    # 1. KPIs
    mrr = calculate_mrr(active_subs)
    active_count = len(active_subs)

    payments_collected = sum(to_decimal(p.amount) for p in payments)
    outstanding_balance = sum(to_decimal(i.balance_due) for i in invoices if i.balance_due > 0)
    overdue_balance = sum(
        to_decimal(i.balance_due) for i in invoices
        if i.balance_due > 0 and i.due_date < today
    )

    payments_collected = round_currency(payments_collected)
    outstanding_balance = round_currency(outstanding_balance)
    overdue_balance = round_currency(overdue_balance)

    # 2. Insights
    insights = []
    insight_id = 1

    if overdue_balance > 0:
        insights.append({
            "id": insight_id,
            "title": "Overdue Debentures Detected",
            "severity": "CRITICAL",
            "explanation": f"Unsettled arrears of ₹{float(overdue_balance):,.2f} have exceeded their maturity terms.",
            "action": "Issue formal dunning notices and follow up on outstanding balances."
        })
        insight_id += 1

    if mrr > 0:
        insights.append({
            "id": insight_id,
            "title": "Recurring Revenue Stability",
            "severity": "INFO",
            "explanation": f"Current charters yield ₹{float(mrr):,.2f} normalized monthly run-rate across {active_count} active contract(s).",
            "action": "Maintain subscriber covenants and monitor renewal dates."
        })
        insight_id += 1

    if outstanding_balance > payments_collected and payments_collected > 0:
        insights.append({
            "id": insight_id,
            "title": "Collection Velocity Warning",
            "severity": "WARNING",
            "explanation": f"Outstanding receivables (₹{float(outstanding_balance):,.2f}) exceed historical settled cash collections.",
            "action": "Prompt debtors for prompt settlement of pending invoices."
        })
        insight_id += 1
    elif payments_collected > 0:
        insights.append({
            "id": insight_id,
            "title": "Treasury Liquidity Healthy",
            "severity": "INFO",
            "explanation": f"Settled collections of ₹{float(payments_collected):,.2f} sustain sound treasury liquidity.",
            "action": "Continue standard billing cycles and routine account audits."
        })
        insight_id += 1

    # 3. Revenue Trend (Payments by month)
    monthly_map = defaultdict(Decimal)
    for p in payments:
        if p.payment_date:
            month_key = p.payment_date.strftime("%b %Y")
            monthly_map[month_key] += to_decimal(p.amount)

    revenue_trend = []
    if monthly_map:
        for month_str, total in monthly_map.items():
            revenue_trend.append({
                "month": month_str,
                "total": float(round_currency(total))
            })
    else:
        current_month = today.strftime("%b %Y")
        revenue_trend.append({
            "month": current_month,
            "total": float(payments_collected)
        })

    return {
        "kpis": {
            "monthly_recurring_revenue": float(mrr),
            "active_subscriptions": active_count,
            "payments_collected": float(payments_collected),
            "outstanding_balance": float(outstanding_balance),
            "overdue_balance": float(overdue_balance)
        },
        "insights": insights,
        "revenue_trend": revenue_trend
    }
