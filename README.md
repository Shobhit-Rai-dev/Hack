SubscriptIQ --- The Royal Ledger

Full Project README, Workflow, Architecture, Setup and Demo Guide

Project: Subscription Management System
Frontend: React + Vite
Backend: FastAPI + SQLAlchemy
Database: SQLite for local development
Status: Local hackathon/demo implementation, based on the supplied
Antigravity report.

Security note: The accounts in this README are development/demo
accounts only. Never use these passwords in production. Do not commit
real secrets, .env files, virtual environments, or dependency folders.

1. Overview

SubscriptIQ --- The Royal Ledger is a subscription management platform
that centralizes customer records, products, plans, quotations,
subscriptions, recurring invoices, payments, taxes, discounts, staff
access, and financial analytics.

The interface uses a parchment-inspired "Royal Ledger" visual identity
with a modern business-management layout.

Problem addressed

Businesses managing recurring services need to coordinate customers,
products, pricing, billing schedules, invoices, taxes, discounts, and
payments. SubscriptIQ aims to bring these workflows into one place and
make financial and subscription status easier to understand.

2. Features

Authentication and role-aware navigation for Admin, Staff, and
Customer.

Customer management and customer portal association.

Product catalogue and product variants.

Daily, weekly, monthly, and yearly subscription plans.

Quotation templates, quotations, and quotation-to-subscription
conversion.

Subscription status/lifecycle management.

Due invoice generation and invoice details/ledger preview.

Payment recording and balance tracking.

Tax and discount rule management.

Dashboard KPIs, revenue/collection trends, and rule-based insights.

Backend checks for role restrictions and customer data isolation.

Duplicate invoice generation protection and payment validation, as
described in the supplied implementation report.

Dashboard metrics

MRR: monthly recurring revenue run-rate.

Active subscriptions: count of subscriptions considered active
by the backend.

Payments collected: recorded collections; not the same as MRR.

Outstanding balance: amounts still unpaid.

Overdue balance: unpaid amounts considered overdue by the
application.

Revenue/collection trend: monthly chart data and business
insights.

3. Technology Stack

Frontend

React 18, Vite, React Router

Lucide React

Recharts

CSS

Backend

Python, FastAPI, Uvicorn

SQLAlchemy and Pydantic

SQLite for development

JWT authentication

Argon2id password hashing

Pytest and HTTPX

Architecture style

A modular monolith: one FastAPI backend with domain-specific routes,
schemas, models, and services. This is simpler to run and maintain than
a distributed microservice system for this project scope.

4. Architecture

┌───────────────────────────────────────────┐
│ Browser: React UI                         │
│ Login / Dashboard / Admin / Customer Portal│
└─────────────────────┬─────────────────────┘
                      │ /api requests
                      ▼
┌───────────────────────────────────────────┐
│ Vite dev server :5173                     │
│ Proxy /api → http://127.0.0.1:8000        │
└─────────────────────┬─────────────────────┘
                      ▼
┌───────────────────────────────────────────┐
│ FastAPI backend :8000                     │
│ API routes → services → SQLAlchemy models │
│ Auth/JWT/RBAC | Pricing | Billing | Stats  │
└─────────────────────┬─────────────────────┘
                      ▼
┌───────────────────────────────────────────┐
│ SQLite development database               │
│ Users, customers, products, plans,         │
│ quotations, subscriptions, invoices,       │
│ payments, taxes, discounts                 │
└───────────────────────────────────────────┘

Important code locations

Path                                     Responsibility

frontend/src/App.jsx                   Main frontend routing/layout

frontend/src/context/AuthContext.jsx   Authentication state

frontend/src/api/client.js             API requests and response/error
handling

frontend/src/components/Sidebar.jsx    Role-aware navigation

frontend/src/pages/                    Login and application pages

backend/app/main.py                    FastAPI entry point and router
registration

backend/app/core/config.py             Settings/environment configuration

backend/app/core/security.py           Password hashing and JWT helpers

backend/app/models/entities.py         SQLAlchemy entities and constraints

backend/app/schemas/domain.py          Request/response validation schemas

backend/app/api/routes/                API route handlers

backend/app/services/pricing.py        Pricing, variant adjustments,
taxes/discounts

backend/app/services/billing.py        Billing cadence and due invoice
generation

backend/app/services/analytics.py      Dashboard aggregation and insights

backend/app/utils/money.py             Decimal-based money helpers

backend/scripts/seed_demo.py           Development/demo seed data

backend/tests/                         Backend and integration tests

5. Roles and Demo Credentials

The supplied Antigravity report lists these pre-seeded development
accounts:

Role           Email / Login ID          Password

ADMIN      admin@subscriptiq.com   Admin@123!
STAFF      staff@subscriptiq.com   Staff@123!
CUSTOMER   bruce@waynecorp.com     Customer@123!

Role overview

Admin: administrative dashboard and broader system management,
including staff administration.

Staff: permitted operational tasks; restricted from selected
administrative actions.

Customer: own subscriptions, invoices, and payment history.

Switching accounts during a demo

Sign out of the current account.

Return to the login page.

Enter the email and password for the next role.

Sign in and show the role-specific navigation.

If credentials fail, verify that the backend is using the expected
database and run the seed script described below. These credentials are
taken from the supplied report and have not been independently
revalidated while creating this README.

Production warning: These public demo passwords are not production
secrets. Change/remove them before deployment. Keep the real
SECRET_KEY and other credentials in a private .env file and never
commit that file.

6. Core Workflows

A. Login

User submits credentials from the login page.

Frontend calls POST /api/auth/login.

Backend validates the user and password hash.

Backend returns authentication information/token.

Frontend uses the authenticated role to render the appropriate
interface.

GET /api/auth/me can retrieve the current authenticated user's
details.

B. Customer → quotation → subscription

Create/select a customer.

Configure products and plans.

Prepare a quotation, optionally from a template.

Convert an eligible quotation into a subscription.

Track the subscription status.

Customer signs in to see their own subscription details.

C. Recurring billing

Billing service finds subscriptions due for billing.

It calculates the relevant period and amount.

Applicable product pricing, tax, and discount rules are considered
where configured.

An invoice is created for the subscription/customer.

Duplicate generation for the same subscription and billing period is
intended to be blocked.

Invoice details become available for review and payment tracking.

D. Payment

A permitted user records a payment against an invoice.

Backend validates the payment amount.

Payment record is stored.

Invoice paid amount and outstanding balance are updated.

Invoice status and dashboard totals reflect the payment.

E. Customer portal

Sign in as bruce@waynecorp.com.

Show My Subscriptions, My Invoices, and Payment History
if present.

Customers should only access their own records; authorization should
be enforced by the backend, not only by hiding UI links.

F. Dashboard

Frontend requests GET /api/dashboard/summary.

Backend aggregates subscription, invoice, and payment data.

Dashboard displays KPIs, chart data, and insights.

MRR and collected payments should be described as separate measures.

7. Local Setup (Windows PowerShell)

Prerequisites: compatible Python version, Node.js/npm, and project
dependencies.

Start backend

From the repository root:

cd backend
.\venv\Scripts\Activate.ps1
python -m scripts.seed_demo
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

If PowerShell activation is blocked, use the environment's Python
directly:

.\venv\Scripts\python.exe -m scripts.seed_demo
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Keep the backend terminal open.

Start frontend

Open a second terminal at the repository root:

cd frontend
npm.cmd install
npm.cmd run dev

Open http://localhost:5173 in Chrome or Edge. Keep both servers
running.

Vite API proxy

The documented frontend config proxies /api to
http://127.0.0.1:8000. Keep API paths consistent and avoid
accidentally constructing /api/api/....

Production frontend build

From frontend/:

npm.cmd run build

The generated build is normally in frontend/dist/.

8. API Endpoint Inventory

The supplied implementation report lists the following endpoints.
Consult route and schema files for exact request/response fields.

Method                  Endpoint                           Purpose

POST                  /api/auth/login                  Sign in

GET                   /api/auth/me                     Current authenticated
user

GET                   /api/dashboard/summary           Dashboard KPIs and
insights

GET, POST           /api/customers                   List/create customers

GET, POST           /api/products                    List/create products

GET, POST           /api/plans                       List/create plans

GET, POST           /api/quotation-templates         List/create quotation
templates

GET, POST           /api/quotations                  List/create quotations

POST                  /api/quotations/{id}/convert     Convert quotation to
subscription

GET                   /api/subscriptions               List subscriptions

PATCH                 /api/subscriptions/{id}/status   Update subscription
status

GET                   /api/invoices                    List invoices

GET                   /api/invoices/{id}               Invoice details

POST                  /api/invoices/generate           Generate due invoices

GET, POST           /api/payments                    List/record payments

GET, POST           /api/taxes                       List/create tax rules

PATCH                 /api/taxes/{id}/status           Enable/disable tax rule

GET, POST           /api/discounts                   List/create discount
rules

PATCH                 /api/discounts/{id}/status       Enable/disable discount

GET                   /api/users                       List users/staff,
permission-dependent

POST                  /api/users/staff                 Create staff account

PATCH                 /api/users/{id}/status           Update user status

9. Data Model Overview

The reported relational model includes: - Users - Customers - Products
and product variants - Plans - Quotation templates - Quotations and
quotation items - Subscriptions and subscription items - Invoices and
invoice items - Payments - Tax rules - Discount rules

The implementation report describes foreign keys, indexes, and
uniqueness constraints. The actual schema is in
backend/app/models/entities.py.

10. Pricing, Billing and Financial Rules

Supported billing frequencies: Daily, Weekly, Monthly, Yearly.

A documented example variant rule adds ₹560 for the Odoo
brand/variant.

Monetary calculations use Decimal helpers, according to the
implementation report.

Due invoice generation is intended to be idempotent for a
subscription/billing period.

Payment recording updates invoice balances/status and rejects
overpayments, according to the report.

MRR is a recurring-revenue run rate; collected payments are recorded
cash collections. Do not treat them as identical.

11. Security and Data Integrity

The supplied report describes: - Argon2id password hashing. - JWT
authentication. - Role-based authorization. - Customer data isolation
for subscriptions, invoices, and payments. - Unique customer email
checks. - Duplicate quotation-conversion prevention. - Idempotent
invoice generation. - Decimal money calculations. - Payment validation
and overpayment rejection.

Retest these controls after code changes. Frontend navigation
restrictions are not a substitute for backend authorization.

12. Testing and Verification

The supplied Antigravity report records:

Check                           Reported result

Backend Pytest suite            15 passed, 0 failed
Frontend production build       Passed
Live proxy integration flows    13 passed
Playwright browser automation   Blocked by driver download HTTP 404

Reported backend tests cover login success/failure, invalid tokens,
unauthenticated requests, role restrictions, customer isolation,
invoice-generation idempotency, payment/overpayment handling, dashboard
summary, duplicate quotation conversion, and duplicate customer email.

Verification caveat: These results are copied from the supplied
Antigravity report; they were not independently rerun while writing this
README. The automated browser workflow did not complete.

Manual smoke-test checklist

Start backend and frontend.

Sign in as Admin and inspect the dashboard.

Open Customers, Products, Plans, Quotations, Subscriptions,
Invoices, Payments, Taxes, Discounts, and Staff where available.

Open an invoice detail/ledger preview.

Test invoice generation only against demo data and only when safe.

Sign out and sign in as Customer.

Check customer subscriptions, invoices, and payment history.

Review browser console, Network tab, and backend terminal for
errors.

13. Known Limitations

According to the supplied report: - Password-reset email delivery is
not configured because external SMTP/email-provider credentials are
not included. - Playwright browser automation was blocked by a remote
driver download error; direct API/proxy integration tests were used
instead. - Production security, deployment, backups, monitoring, and
load/performance testing have not been independently certified by this
README. - No measured evidence is provided here that every page loads in
under two seconds; do not claim that performance target without a
benchmark.

14. Troubleshooting

Login returns an unexpected JSON response

Ensure backend is running at 127.0.0.1:8000.

Ensure frontend is running at localhost:5173.

Check the Vite /api proxy configuration.

Inspect the failing request and response in the browser Network tab.

Confirm demo seed data was loaded into the database used by the
running backend.

Pages load but data is missing

Confirm both servers are running.

Inspect /api/... requests in the browser Network tab.

Check the backend terminal for errors.

Confirm the current role is permitted to access the endpoint.

Demo credentials fail

Run the seed script from the backend/ directory.

Confirm the backend points to the intended SQLite database.

Avoid deleting a database that contains data you need.

15. Git Hygiene

Recommended root .gitignore entries:

node_modules/
dist/
.venv/
venv/
__pycache__/
*.py[cod]
.env
.env.*
!.env.example
*.db
*.sqlite
*.sqlite3
.pytest_cache/
.coverage

Commit package-lock.json to preserve frontend dependency versions. Do
not commit node_modules/, virtual environments, private .env files,
local databases containing sensitive data, or real credentials.

16. Suggested Hackathon Demo Sequence

Login page and branding.

Admin dashboard and KPI cards.

Customers, Products, and Plans.

Quotations and Subscriptions.

Invoices and Payments, including ledger preview if available.

Sign out and sign in as Customer to show the customer portal.

Close with the platform's unified subscription-management goal.

Demo account quick reference: - Admin: admin@subscriptiq.com /
Admin@123! - Staff: staff@subscriptiq.com / Staff@123! - Customer:
bruce@waynecorp.com / Customer@123!

Avoid creating unwanted records during recording.

17. Project Status

The supplied report marks the project READY FOR DEMO, citing
implemented backend modules, passing backend tests, a successful
frontend build, and passing live proxy integration flows. It also
records incomplete browser automation and unconfigured password-reset
email delivery.

The accurate description is: a local hackathon/demo implementation
based on the reported checks, not independently audited or
production-certified software.

Quick Reference

Item                                Value

Project                             SubscriptIQ --- The Royal Ledger

Frontend                            React + Vite

Frontend URL                        http://localhost:5173

Backend                             FastAPI + Uvicorn

Backend address                     http://127.0.0.1:8000

API prefix                          /api

Development database                SQLite

Backend tests                       python -m pytest -v tests/test_backend.py
from backend/

Frontend build                      npm.cmd run build from frontend/

SubscriptIQ --- The Royal Ledger
Bringing subscription operations and billing into one organized
ledger.