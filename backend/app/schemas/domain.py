import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# --- Auth & Users ---
class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not EMAIL_REGEX.match(v.strip()):
            raise ValueError("Invalid email format.")
        return v.strip().lower()

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    customer_id: Optional[int] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class StaffCreateRequest(BaseModel):
    full_name: str
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not EMAIL_REGEX.match(v.strip()):
            raise ValueError("Invalid email format.")
        return v.strip().lower()

# --- Customers ---
class CustomerCreateRequest(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    company_name: Optional[str] = None
    billing_address: Optional[str] = None
    create_portal_account: bool = False
    portal_password: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not EMAIL_REGEX.match(v.strip()):
            raise ValueError("Invalid email format.")
        return v.strip().lower()

class CustomerResponse(BaseModel):
    id: int
    customer_number: str
    full_name: str
    company_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    user_id: Optional[int] = None
    total_balance_due: float
    billing_address: Optional[str] = None

# --- Products ---
class ProductVariantResponse(BaseModel):
    id: int
    variant_name: str
    price_adjustment: float

class ProductCreateRequest(BaseModel):
    name: str
    product_type: str = "Service"
    sales_price: float = Field(..., ge=0)
    cost_price: float = Field(default=0.0, ge=0)
    description: Optional[str] = None
    notes: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    product_type: str
    sales_price: float
    cost_price: float
    description: Optional[str] = None
    notes: Optional[str] = None
    variants: List[ProductVariantResponse] = []

# --- Plans ---
class PlanCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    billing_frequency: str = "Monthly"
    minimum_quantity: int = Field(default=1, ge=1)
    behavior_at_end: str = "Close automatically"

class PlanResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    billing_frequency: str
    minimum_quantity: int
    behavior_at_end: str
    is_active: bool

# --- Quotation Templates ---
class QuotationTemplateItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)
    description: Optional[str] = None

class QuotationTemplateItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    description: Optional[str] = None

class QuotationTemplateCreateRequest(BaseModel):
    name: str
    plan_id: int
    validity_days: int = Field(default=30, ge=1)
    notes: Optional[str] = None
    items: List[QuotationTemplateItemCreate] = []

class QuotationTemplateResponse(BaseModel):
    id: int
    name: str
    plan_id: int
    plan_name: str
    billing_frequency: str
    validity_days: int
    notes: Optional[str] = None
    items: List[QuotationTemplateItemResponse] = []

# --- Quotations ---
class QuotationItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)
    unit_price: Optional[float] = None
    description: Optional[str] = None

class QuotationCreateRequest(BaseModel):
    customer_id: int
    plan_id: Optional[int] = None
    validity_days: int = Field(default=30, ge=1)
    items: List[QuotationItemCreate] = []
    notes: Optional[str] = None

class QuotationResponse(BaseModel):
    id: int
    quotation_number: str
    customer_name: str
    plan_name: Optional[str] = None
    quotation_date: str
    expiry_date: Optional[str] = None
    status: str
    total_amount: float

# --- Subscriptions ---
class SubscriptionResponse(BaseModel):
    id: int
    subscription_number: str
    customer_name: str
    plan_name: str
    billing_frequency: str
    start_date: str
    next_billing_date: str
    status: str
    total_amount: float

# --- Invoices ---
class InvoiceItemResponse(BaseModel):
    id: int
    description: str
    quantity: int
    unit_price: float
    line_total: float

class InvoiceListResponse(BaseModel):
    id: int
    invoice_number: str
    customer_name: str
    subscription_number: Optional[str] = None
    due_date: str
    status: str
    total_amount: float
    balance_due: float

class InvoiceDetailResponse(BaseModel):
    id: int
    invoice_number: str
    customer_name: str
    company_name: Optional[str] = None
    billing_address: Optional[str] = None
    subscription_number: Optional[str] = None
    issue_date: str
    due_date: str
    billing_period_start: Optional[str] = None
    billing_period_end: Optional[str] = None
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    amount_paid: float
    balance_due: float
    status: str
    items: List[InvoiceItemResponse] = []

# --- Payments ---
class PaymentCreateRequest(BaseModel):
    invoice_id: int
    payment_method: str = "Bank Transfer"
    amount: float = Field(..., gt=0)
    payment_date: Optional[str] = None
    note: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    payment_reference: str
    invoice_number: str
    customer_name: str
    payment_date: str
    payment_method: str
    status: str
    amount: float

class PaymentRecordResult(BaseModel):
    id: int
    payment_reference: str
    invoice_status: str
    balance_due: float
    amount: float

# --- Taxes & Discounts ---
class TaxCreateRequest(BaseModel):
    name: str
    rate: float = Field(..., ge=0)
    applicable_to: str = "All"

class TaxResponse(BaseModel):
    id: int
    name: str
    rate: float
    applicable_to: str
    is_active: bool

class DiscountCreateRequest(BaseModel):
    name: str
    discount_type: str = "Percentage"
    discount_value: float = Field(..., ge=0)
    minimum_purchase: float = Field(default=0.0, ge=0)
    usage_limit: Optional[int] = Field(default=None, ge=1)

class DiscountResponse(BaseModel):
    id: int
    name: str
    discount_type: str
    discount_value: float
    minimum_purchase: float
    usage_limit: Optional[int] = None
    usage_count: int
    is_active: bool

# --- Dashboard ---
class KPIs(BaseModel):
    monthly_recurring_revenue: float
    active_subscriptions: int
    payments_collected: float
    outstanding_balance: float
    overdue_balance: float

class Insight(BaseModel):
    id: int
    title: str
    severity: str
    explanation: str
    action: str

class RevenueTrendItem(BaseModel):
    month: str
    total: float

class DashboardSummaryResponse(BaseModel):
    kpis: KPIs
    insights: List[Insight] = []
    revenue_trend: List[RevenueTrendItem] = []
