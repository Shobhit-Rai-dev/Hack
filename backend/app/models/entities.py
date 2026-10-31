from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Boolean, Text, Numeric,
    Date, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="CUSTOMER")  # ADMIN, STAFF, CUSTOMER
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="user", uselist=False)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    customer_number = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    company_name = Column(String(150), nullable=True)
    billing_address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="customer")
    quotations = relationship("Quotation", back_populates="customer", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="customer", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="customer", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="customer", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    product_type = Column(String(50), default="Service", nullable=False)  # Service, Digital Product, Physical Product
    sales_price = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    cost_price = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_name = Column(String(100), nullable=False)
    price_adjustment = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)

    product = relationship("Product", back_populates="variants")

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    billing_frequency = Column(String(50), default="Monthly", nullable=False)  # Daily, Weekly, Monthly, Yearly
    minimum_quantity = Column(Integer, default=1, nullable=False)
    behavior_at_end = Column(String(100), default="Close automatically", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    quotation_templates = relationship("QuotationTemplate", back_populates="plan")
    quotations = relationship("Quotation", back_populates="plan")
    subscriptions = relationship("Subscription", back_populates="plan")

class QuotationTemplate(Base):
    __tablename__ = "quotation_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    validity_days = Column(Integer, default=30, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    plan = relationship("SubscriptionPlan", back_populates="quotation_templates")
    items = relationship("QuotationTemplateItem", back_populates="template", cascade="all, delete-orphan")

class QuotationTemplateItem(Base):
    __tablename__ = "quotation_template_items"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("quotation_templates.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    description = Column(String(255), nullable=True)

    template = relationship("QuotationTemplate", back_populates="items")
    product = relationship("Product")

class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(Integer, primary_key=True, index=True)
    quotation_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=True)
    quotation_date = Column(Date, default=date.today, nullable=False)
    expiry_date = Column(Date, nullable=True)
    status = Column(String(50), default="Draft", nullable=False)  # Draft, Confirmed, Converted
    subtotal = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    discount_amount = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    tax_amount = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    total_amount = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="quotations")
    plan = relationship("SubscriptionPlan", back_populates="quotations")
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="quotation", uselist=False)

class QuotationItem(Base):
    __tablename__ = "quotation_items"

    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    line_total = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    description = Column(String(255), nullable=True)

    quotation = relationship("Quotation", back_populates="items")
    product = relationship("Product")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    subscription_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=True)
    start_date = Column(Date, default=date.today, nullable=False)
    next_billing_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(String(50), default="Active", nullable=False)  # Draft, Confirmed, Active, Paused, Closed
    subtotal = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    discount_amount = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    tax_amount = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    total_amount = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    payment_terms = Column(String(50), default="Net 15", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    quotation = relationship("Quotation", back_populates="subscription")
    items = relationship("SubscriptionItem", back_populates="subscription", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")

class SubscriptionItem(Base):
    __tablename__ = "subscription_items"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    line_total = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    description = Column(String(255), nullable=True)

    subscription = relationship("Subscription", back_populates="items")
    product = relationship("Product")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    issue_date = Column(Date, default=date.today, nullable=False)
    due_date = Column(Date, nullable=False)
    billing_period_start = Column(Date, nullable=True)
    billing_period_end = Column(Date, nullable=True)
    subtotal = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    discount_amount = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    tax_amount = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    total_amount = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    amount_paid = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    balance_due = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    status = Column(String(50), default="Confirmed", nullable=False)  # Draft, Confirmed, Paid, Partially Paid, Overdue, Cancelled
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("subscription_id", "billing_period_start", name="uq_subscription_billing_period"),
    )

    customer = relationship("Customer", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    line_total = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_reference = Column(String(50), unique=True, index=True, nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50), default="Bank Transfer", nullable=False)
    payment_date = Column(Date, default=date.today, nullable=False)
    note = Column(Text, nullable=True)
    status = Column(String(50), default="Settled", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    invoice = relationship("Invoice", back_populates="payments")
    customer = relationship("Customer", back_populates="payments")

class TaxRule(Base):
    __tablename__ = "tax_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    rate = Column(Numeric(5, 2), nullable=False)  # e.g. 18.00 for 18%
    applicable_to = Column(String(50), default="All", nullable=False)  # All, Services, Physical
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class DiscountRule(Base):
    __tablename__ = "discount_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    discount_type = Column(String(50), default="Percentage", nullable=False)  # Percentage, Fixed
    discount_value = Column(Numeric(12, 2), nullable=False)
    minimum_purchase = Column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    usage_limit = Column(Integer, nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
