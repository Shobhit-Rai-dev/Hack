from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal, Base, get_db
from app.models.entities import (
    User, Customer, Product, ProductVariant, SubscriptionPlan,
    QuotationTemplate, QuotationTemplateItem, Quotation, QuotationItem,
    Subscription, SubscriptionItem, Invoice, InvoiceItem, Payment,
    TaxRule, DiscountRule
)
from app.core.security import get_password_hash

def run_seed(db: Session = None):
    close_db = False
    gen_to_close = None

    if db is None:
        from app.main import app
        if get_db in app.dependency_overrides:
            gen_to_close = app.dependency_overrides[get_db]()
            db = next(gen_to_close)
            close_db = False
        else:
            Base.metadata.create_all(bind=engine)
            db = SessionLocal()
            close_db = True

    try:
        # Check if already seeded to prevent duplication
        admin_user = db.query(User).filter(User.email == "admin@subscriptiq.com").first()
        if admin_user:
            return

        today = date.today()

        # 1. Users
        admin = User(
            full_name="Imperial Grand Marshal",
            email="admin@subscriptiq.com",
            password_hash=get_password_hash("Admin@123!"),
            role="ADMIN",
            is_active=True
        )
        staff = User(
            full_name="Audit Chancellor",
            email="staff@subscriptiq.com",
            password_hash=get_password_hash("Staff@123!"),
            role="STAFF",
            is_active=True
        )
        bruce_user = User(
            full_name="Bruce Wayne",
            email="bruce@waynecorp.com",
            password_hash=get_password_hash("Customer@123!"),
            role="CUSTOMER",
            is_active=True
        )
        tony_user = User(
            full_name="Tony Stark",
            email="tony@starkindustries.com",
            password_hash=get_password_hash("Customer@123!"),
            role="CUSTOMER",
            is_active=True
        )
        db.add_all([admin, staff, bruce_user, tony_user])
        db.flush()

        # 2. Customers
        bruce_cust = Customer(
            user_id=bruce_user.id,
            customer_number="CUST-001",
            full_name="Bruce Wayne",
            company_name="Wayne Enterprises",
            email="bruce@waynecorp.com",
            phone="+1-555-0199",
            billing_address="1007 Mountain Drive, Gotham City"
        )
        tony_cust = Customer(
            user_id=tony_user.id,
            customer_number="CUST-002",
            full_name="Tony Stark",
            company_name="Stark Industries",
            email="tony@starkindustries.com",
            phone="+1-555-0142",
            billing_address="10880 Wilshire Blvd, Los Angeles, CA"
        )
        diana_cust = Customer(
            user_id=None,
            customer_number="CUST-003",
            full_name="Diana Prince",
            company_name="Themyscira Cultural Institute",
            email="diana@themyscira.org",
            phone="+1-555-0177",
            billing_address="Gateway City Embassy"
        )
        db.add_all([bruce_cust, tony_cust, diana_cust])
        db.flush()

        # 3. Products
        prod_erp = Product(
            name="Enterprise ERP Cloud Suite",
            product_type="Service",
            sales_price=Decimal("15000.00"),
            cost_price=Decimal("4500.00"),
            description="Full imperial cloud ledger with multi-subsidiary consolidation.",
            is_active=True
        )
        prod_sec = Product(
            name="Security & Penetration Audit",
            product_type="Service",
            sales_price=Decimal("30000.00"),
            cost_price=Decimal("8000.00"),
            description="Comprehensive architectural and covenant audit.",
            is_active=True
        )
        prod_odoo = Product(
            name="Odoo ERP Connector",
            product_type="Digital Product",
            sales_price=Decimal("2500.00"),
            cost_price=Decimal("500.00"),
            description="Automated two-way ledger synchronization.",
            is_active=True
        )
        prod_sla = Product(
            name="Priority 24/7 SLA",
            product_type="Service",
            sales_price=Decimal("5000.00"),
            cost_price=Decimal("1000.00"),
            description="Round-the-clock priority dispatch.",
            is_active=True
        )
        db.add_all([prod_erp, prod_sec, prod_odoo, prod_sla])
        db.flush()

        # Product Variant (Odoo Brand adds 560 to base price)
        odoo_variant = ProductVariant(
            product_id=prod_odoo.id,
            variant_name="Odoo Brand Enterprise Certified",
            price_adjustment=Decimal("560.00")
        )
        db.add(odoo_variant)
        db.flush()

        # 4. Subscription Plans
        plan_monthly = SubscriptionPlan(
            name="Monthly Imperial Standard",
            description="Standard monthly billing cycle with auto-closure safeguards.",
            billing_frequency="Monthly",
            minimum_quantity=1,
            behavior_at_end="Close automatically",
            is_active=True
        )
        plan_annual = SubscriptionPlan(
            name="Annual Sovereign Sovereign",
            description="365-day calendar commitment with renewal privileges.",
            billing_frequency="Yearly",
            minimum_quantity=1,
            behavior_at_end="Renew when configured",
            is_active=True
        )
        plan_weekly = SubscriptionPlan(
            name="Weekly Rapid Response",
            description="Weekly short-burst project charters.",
            billing_frequency="Weekly",
            minimum_quantity=1,
            behavior_at_end="Pause",
            is_active=True
        )
        db.add_all([plan_monthly, plan_annual, plan_weekly])
        db.flush()

        # 5. Tax & Discount Rules
        tax_gst = TaxRule(
            name="GST 18%",
            rate=Decimal("18.00"),
            applicable_to="All",
            is_active=True
        )
        tax_stamp = TaxRule(
            name="Imperial Stamp Duty 5%",
            rate=Decimal("5.00"),
            applicable_to="Physical",
            is_active=False
        )
        disc_royal = DiscountRule(
            name="ROYAL10",
            discount_type="Percentage",
            discount_value=Decimal("10.00"),
            minimum_purchase=Decimal("10000.00"),
            usage_limit=100,
            usage_count=1,
            is_active=True
        )
        db.add_all([tax_gst, tax_stamp, disc_royal])
        db.flush()

        # 6. Quotation Templates
        tpl = QuotationTemplate(
            name="Executive Cloud Package",
            plan_id=plan_monthly.id,
            validity_days=30,
            notes="Standard 30-day corporate proposal package."
        )
        db.add(tpl)
        db.flush()

        tpl_item1 = QuotationTemplateItem(
            template_id=tpl.id,
            product_id=prod_erp.id,
            quantity=1,
            description="Enterprise ERP Cloud Suite"
        )
        tpl_item2 = QuotationTemplateItem(
            template_id=tpl.id,
            product_id=prod_sla.id,
            quantity=1,
            description="Priority 24/7 SLA"
        )
        db.add_all([tpl_item1, tpl_item2])
        db.flush()

        # 7. Quotations
        quo1 = Quotation(
            quotation_number="QUO-202610-0001",
            customer_id=bruce_cust.id,
            plan_id=plan_monthly.id,
            quotation_date=today - timedelta(days=30),
            expiry_date=today,
            status="Converted",
            subtotal=Decimal("15000.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("2700.00"),
            total_amount=Decimal("17700.00"),
            notes="Formal commercial quotation converted to active subscription."
        )
        quo2 = Quotation(
            quotation_number="QUO-202610-0002",
            customer_id=diana_cust.id,
            plan_id=plan_annual.id,
            quotation_date=today - timedelta(days=5),
            expiry_date=today + timedelta(days=25),
            status="Confirmed",
            subtotal=Decimal("30000.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("5400.00"),
            total_amount=Decimal("35400.00"),
            notes="Security assessment proposal pending charter sign-off."
        )
        db.add_all([quo1, quo2])
        db.flush()

        q_item1 = QuotationItem(
            quotation_id=quo1.id,
            product_id=prod_erp.id,
            quantity=1,
            unit_price=Decimal("15000.00"),
            line_total=Decimal("15000.00"),
            description="Enterprise ERP Cloud Suite"
        )
        q_item2 = QuotationItem(
            quotation_id=quo2.id,
            product_id=prod_sec.id,
            quantity=1,
            unit_price=Decimal("30000.00"),
            line_total=Decimal("30000.00"),
            description="Security & Penetration Audit"
        )
        db.add_all([q_item1, q_item2])
        db.flush()

        # 8. Subscriptions
        # Sub 1: Bruce Wayne (Paid / Current)
        sub1 = Subscription(
            subscription_number="SUB-202610-0001",
            customer_id=bruce_cust.id,
            plan_id=plan_monthly.id,
            quotation_id=quo1.id,
            start_date=today - timedelta(days=30),
            next_billing_date=today + timedelta(days=30),  # Not due today
            status="Active",
            subtotal=Decimal("15000.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("2700.00"),
            total_amount=Decimal("17700.00"),
            payment_terms="Net 15"
        )
        # Sub 2: Tony Stark (Due for billing generation today! Eligible for /api/invoices/generate)
        sub2 = Subscription(
            subscription_number="SUB-202610-0002",
            customer_id=tony_cust.id,
            plan_id=plan_monthly.id,
            quotation_id=None,
            start_date=today - timedelta(days=60),
            next_billing_date=today - timedelta(days=1),  # PAST DUE -> Eligible for generate_due_invoices!
            status="Active",
            subtotal=Decimal("20000.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("3600.00"),
            total_amount=Decimal("23600.00"),
            payment_terms="Net 15"
        )
        db.add_all([sub1, sub2])
        db.flush()

        sub_item1 = SubscriptionItem(
            subscription_id=sub1.id,
            product_id=prod_erp.id,
            quantity=1,
            unit_price=Decimal("15000.00"),
            line_total=Decimal("15000.00"),
            description="Enterprise ERP Cloud Suite"
        )
        sub_item2 = SubscriptionItem(
            subscription_id=sub2.id,
            product_id=prod_sec.id,
            quantity=1,
            unit_price=Decimal("20000.00"),
            line_total=Decimal("20000.00"),
            description="Continuous Security Oversight"
        )
        db.add_all([sub_item1, sub_item2])
        db.flush()

        # 9. Invoices
        # Invoice 1 belongs to Bruce Wayne (Paid)
        inv1 = Invoice(
            id=1,
            invoice_number="INV-202610-0001",
            customer_id=bruce_cust.id,
            subscription_id=sub1.id,
            issue_date=today - timedelta(days=20),
            due_date=today - timedelta(days=5),
            billing_period_start=today - timedelta(days=30),
            billing_period_end=today - timedelta(days=1),
            subtotal=Decimal("15000.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("2700.00"),
            total_amount=Decimal("17700.00"),
            amount_paid=Decimal("17700.00"),
            balance_due=Decimal("0.00"),
            status="Paid"
        )
        # Invoice 2 belongs to Tony Stark (Confirmed, total balance 35400.00 for test_payment_and_overpayment_rejection)
        inv2 = Invoice(
            id=2,
            invoice_number="INV-202610-0002",
            customer_id=tony_cust.id,
            subscription_id=sub2.id,
            issue_date=today - timedelta(days=10),
            due_date=today + timedelta(days=5),
            billing_period_start=today - timedelta(days=60),
            billing_period_end=today - timedelta(days=31),
            subtotal=Decimal("30000.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("5400.00"),
            total_amount=Decimal("35400.00"),
            amount_paid=Decimal("0.00"),
            balance_due=Decimal("35400.00"),
            status="Confirmed"
        )
        db.add_all([inv1, inv2])
        db.flush()

        inv_item1 = InvoiceItem(
            invoice_id=inv1.id,
            product_id=prod_erp.id,
            description="Enterprise ERP Cloud Suite (Monthly Charter)",
            quantity=1,
            unit_price=Decimal("15000.00"),
            line_total=Decimal("15000.00")
        )
        inv_item2 = InvoiceItem(
            invoice_id=inv2.id,
            product_id=prod_sec.id,
            description="Security & Penetration Audit (Debenture Assessment)",
            quantity=1,
            unit_price=Decimal("30000.00"),
            line_total=Decimal("30000.00")
        )
        db.add_all([inv_item1, inv_item2])
        db.flush()

        # 10. Payments
        pmt1 = Payment(
            payment_reference="PAY-202610-0001",
            invoice_id=inv1.id,
            customer_id=bruce_cust.id,
            amount=Decimal("17700.00"),
            payment_method="Bank Transfer",
            payment_date=today - timedelta(days=12),
            note="Discharge of debenture INV-202610-0001 via Gotham Wire",
            status="Settled"
        )
        db.add(pmt1)

        db.commit()
    finally:
        if gen_to_close:
            try:
                next(gen_to_close)
            except StopIteration:
                pass
        elif close_db:
            db.close()

if __name__ == "__main__":
    print("Seeding SubscriptIQ demo data...")
    run_seed()
    print("Demo database successfully initialized and seeded.")
