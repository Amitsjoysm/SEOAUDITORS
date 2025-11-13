"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import UserRole, AuditStatus, SubscriptionStatus, CheckStatus


# ============ Auth Schemas ============
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


# ============ User Schemas ============
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class UserWithSubscription(UserResponse):
    current_subscription: Optional["SubscriptionResponse"] = None


# ============ Plan Schemas ============
class PlanBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    price: float
    max_audits_per_month: int
    max_pages_per_audit: int
    features: List[str] = []


class PlanCreate(PlanBase):
    stripe_price_id: Optional[str] = None
    razorpay_plan_id: Optional[str] = None


class PlanUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    max_audits_per_month: Optional[int] = None
    max_pages_per_audit: Optional[int] = None
    features: Optional[List[str]] = None
    is_active: Optional[bool] = None


class PlanResponse(PlanBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    stripe_price_id: Optional[str] = None
    is_active: bool
    created_at: datetime


# ============ Subscription Schemas ============
class SubscriptionCreate(BaseModel):
    plan_id: str
    payment_method_id: Optional[str] = None  # Stripe payment method


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool
    audits_used_this_month: int
    created_at: datetime
    plan: PlanResponse


# ============ Audit Schemas ============
class AuditCreate(BaseModel):
    website_url: str = Field(..., description="Full URL of the website to audit (e.g., https://example.com)")


class AuditResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    category: str
    check_name: str
    status: CheckStatus
    impact_score: Optional[int] = None
    current_value: Optional[str] = None
    recommended_value: Optional[str] = None
    pros: List[str] = []
    cons: List[str] = []
    ranking_impact: Optional[str] = None
    solution: Optional[str] = None
    enhancements: List[str] = []
    details: Dict[str, Any] = {}


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    website_url: str
    status: AuditStatus
    pages_crawled: int
    total_checks_run: int
    checks_passed: int
    checks_failed: int
    checks_warning: int
    overall_score: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class AuditDetailResponse(AuditResponse):
    results: List[AuditResultResponse] = []
    metadata: Dict[str, Any] = {}


# ============ Chat Schemas ============
class ChatMessageCreate(BaseModel):
    audit_id: str
    content: str


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    audit_id: str
    role: str
    content: str
    created_at: datetime


# ============ API Token Schemas ============
class APITokenCreate(BaseModel):
    name: str = Field(..., description="Friendly name for this API token")


class APITokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: Optional[str] = None
    token: str
    is_active: bool
    last_used_at: Optional[datetime] = None
    created_at: datetime


# ============ Analytics Schemas ============
class AdminDashboardStats(BaseModel):
    total_users: int
    active_users: int
    total_audits: int
    audits_this_month: int
    total_revenue: float
    active_subscriptions: int
    avg_audit_score: float


class UserAuditStats(BaseModel):
    total_audits: int
    audits_this_month: int
    avg_score: float
    last_audit_date: Optional[datetime] = None
    remaining_audits: int


# ============ Report Schemas ============
class ReportDownloadRequest(BaseModel):
    audit_id: str
    format: str = Field(..., pattern="^(pdf|docx)$")
