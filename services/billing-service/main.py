"""
Billing Domain Service
FastAPI-based billing and subscription management for Aurora SaaS
"""
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from uuid import uuid4
import os

app = FastAPI(title="Aurora Billing Service", version="1.0.0")

# Enums
class PlanTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class BillingStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    TRIALING = "trialing"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    PAID = "paid"
    OPEN = "open"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"

# Models
class Plan(BaseModel):
    id: str
    name: str
    tier: PlanTier
    price_monthly: float
    price_yearly: float
    features: List[str]
    user_limit: int
    storage_gb: int
    api_calls_per_month: int

class Subscription(BaseModel):
    id: str
    tenant_id: str
    plan_id: str
    plan: Plan
    status: BillingStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    created_at: datetime

class PaymentMethod(BaseModel):
    id: str
    tenant_id: str
    type: str  # card, bank_account
    last4: str
    brand: Optional[str] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    is_default: bool = False

class Invoice(BaseModel):
    id: str
    tenant_id: str
    amount: float
    currency: str = "usd"
    status: InvoiceStatus
    period_start: datetime
    period_end: datetime
    paid_at: Optional[datetime] = None
    created_at: datetime

# Plan definitions
PLANS = {
    "free": Plan(
        id="free",
        name="Free",
        tier=PlanTier.FREE,
        price_monthly=0,
        price_yearly=0,
        features=["Up to 3 users", "100 tasks", "1GB storage", "Basic support"],
        user_limit=3,
        storage_gb=1,
        api_calls_per_month=1000,
    ),
    "starter": Plan(
        id="starter",
        name="Starter",
        tier=PlanTier.STARTER,
        price_monthly=29,
        price_yearly=290,
        features=["Up to 10 users", "1,000 tasks", "10GB storage", "Email support"],
        user_limit=10,
        storage_gb=10,
        api_calls_per_month=10000,
    ),
    "professional": Plan(
        id="professional",
        name="Professional",
        tier=PlanTier.PROFESSIONAL,
        price_monthly=99,
        price_yearly=990,
        features=["Up to 50 users", "Unlimited tasks", "100GB storage", "Priority support", "API access"],
        user_limit=50,
        storage_gb=100,
        api_calls_per_month=100000,
    ),
    "enterprise": Plan(
        id="enterprise",
        name="Enterprise",
        tier=PlanTier.ENTERPRISE,
        price_monthly=299,
        price_yearly=2990,
        features=["Unlimited users", "Unlimited tasks", "1TB storage", "24/7 support", "API access", "SSO"],
        user_limit=-1,
        storage_gb=1000,
        api_calls_per_month=-1,
    ),
}

# In-memory storage (replace with PostgreSQL in production)
subscriptions_db: dict = {}
payment_methods_db: dict = {}
invoices_db: dict = {}

def get_tenant_id_from_context() -> str:
    """Extract tenant_id from request context (JWT in production)"""
    return "default-tenant"

@app.get("/plans", response_model=List[Plan])
async def list_plans():
    """List all available plans"""
    return list(PLANS.values())

@app.get("/plans/{plan_id}", response_model=Plan)
async def get_plan(plan_id: str):
    """Get a specific plan"""
    plan = PLANS.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@app.get("/subscription", response_model=Optional[Subscription])
async def get_subscription(
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Get current subscription"""
    subscription = subscriptions_db.get(tenant_id)
    if not subscription:
        return None
    subscription.plan = PLANS[subscription.plan_id]
    return subscription

@app.post("/subscription")
async def create_subscription(
    plan_id: str,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Create or update subscription"""
    plan = PLANS.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    now = datetime.utcnow()
    period_end = now + timedelta(days=30)
    
    subscription = Subscription(
        id=str(uuid4()),
        tenant_id=tenant_id,
        plan_id=plan_id,
        plan=plan,
        status=BillingStatus.TRIALING,
        current_period_start=now,
        current_period_end=period_end,
        created_at=now,
    )
    
    subscriptions_db[tenant_id] = subscription
    return subscription

@app.post("/subscription/cancel")
async def cancel_subscription(
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Cancel subscription at period end"""
    subscription = subscriptions_db.get(tenant_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription")
    
    subscription.cancel_at_period_end = True
    subscriptions_db[tenant_id] = subscription
    return subscription

@app.get("/payment-methods", response_model=List[PaymentMethod])
async def list_payment_methods(
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """List payment methods"""
    return [pm for pm in payment_methods_db.values() if pm.tenant_id == tenant_id]

@app.post("/payment-methods")
async def add_payment_method(
    payment_type: str,
    last4: str,
    brand: Optional[str] = None,
    expiry_month: Optional[int] = None,
    expiry_year: Optional[int] = None,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Add a payment method"""
    payment_method = PaymentMethod(
        id=str(uuid4()),
        tenant_id=tenant_id,
        type=payment_type,
        last4=last4,
        brand=brand,
        expiry_month=expiry_month,
        expiry_year=expiry_year,
        is_default=False,
    )
    
    payment_methods_db[payment_method.id] = payment_method
    return payment_method

@app.delete("/payment-methods/{method_id}")
async def delete_payment_method(
    method_id: str,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Delete a payment method"""
    payment_method = payment_methods_db.get(method_id)
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    if payment_method.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    del payment_methods_db[method_id]
    return {"message": "Payment method deleted"}

@app.get("/invoices", response_model=List[Invoice])
async def list_invoices(
    tenant_id: str = Depends(get_tenant_id_from_context),
    limit: int = Query(12, ge=1, le=100)
):
    """List invoices"""
    invoices = [inv for inv in invoices_db.values() if inv.tenant_id == tenant_id]
    invoices.sort(key=lambda inv: inv.created_at, reverse=True)
    return invoices[:limit]

@app.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Get a specific invoice"""
    invoice = invoices_db.get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return invoice

@app.get("/billing/stats")
async def get_billing_stats(
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Get billing statistics"""
    invoices = [inv for inv in invoices_db.values() if inv.tenant_id == tenant_id]
    subscription = subscriptions_db.get(tenant_id)
    
    total_paid = sum(inv.amount for inv in invoices if inv.status == InvoiceStatus.PAID)
    total_pending = sum(inv.amount for inv in invoices if inv.status == InvoiceStatus.OPEN)
    
    return {
        "subscription_status": subscription.status if subscription else "none",
        "current_plan": subscription.plan_id if subscription else "none",
        "total_paid": total_paid,
        "total_pending": total_pending,
        "invoices_count": len(invoices),
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "billing-service",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
