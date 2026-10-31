from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
from app.api.routes import (
    auth, customers, products, plans, quotations,
    subscriptions, invoices, payments, taxes, discounts, staff, dashboard
)

# 1. Initialize tables
Base.metadata.create_all(bind=engine)

# 2. THIS VARIABLE MUST BE NAMED EXACTLY 'app' AT ROOT LEVEL
app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# 3. Middleware & Routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(plans.router)
app.include_router(quotations.router)
app.include_router(subscriptions.router)
app.include_router(invoices.router)
app.include_router(payments.router)
app.include_router(taxes.router)
app.include_router(discounts.router)
app.include_router(staff.router)
app.include_router(dashboard.router)

@app.get("/")
def health_check():
    return {"status": "online", "system": settings.PROJECT_NAME}