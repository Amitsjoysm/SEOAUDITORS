"""SQLAlchemy Models for MJ SEO Application"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
import uuid


class UserRole(str, enum.Enum):
    USER = "user"
    SUPERADMIN = "superadmin"


class AuditStatus(str, enum.Enum):
    PENDING = "pending"
    CRAWLING = "crawling"
    ANALYZING = "analyzing"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    INCOMPLETE = "incomplete"
    TRIALING = "trialing"


class CheckStatus(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    INFO = "info"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    stripe_customer_id = Column(String, unique=True)  # Stripe Customer ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    audits = relationship("Audit", back_populates="user", cascade="all, delete-orphan")
    api_tokens = relationship("APIToken", back_populates="user", cascade="all, delete-orphan")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    display_name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)  # Monthly price in USD
    stripe_price_id = Column(String)  # Stripe Price ID
    razorpay_plan_id = Column(String)  # Razorpay Plan ID
    max_audits_per_month = Column(Integer, nullable=False)
    max_pages_per_audit = Column(Integer, nullable=False)
    features = Column(JSON)  # List of feature descriptions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(String, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    stripe_subscription_id = Column(String, unique=True)
    stripe_customer_id = Column(String)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    audits_used_this_month = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")


class Audit(Base):
    __tablename__ = "audits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    website_url = Column(String, nullable=False)
    status = Column(SQLEnum(AuditStatus), default=AuditStatus.PENDING, nullable=False)
    pages_crawled = Column(Integer, default=0)
    total_checks_run = Column(Integer, default=0)
    checks_passed = Column(Integer, default=0)
    checks_failed = Column(Integer, default=0)
    checks_warning = Column(Integer, default=0)
    overall_score = Column(Float)  # 0-100
    report_pdf_path = Column(String)
    report_docx_path = Column(String)
    error_message = Column(Text)
    audit_metadata = Column(JSON)  # Store crawled data, timings, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="audits")
    results = relationship("AuditResult", back_populates="audit", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="audit", cascade="all, delete-orphan")


class AuditResult(Base):
    __tablename__ = "audit_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    audit_id = Column(String, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    category = Column(String, nullable=False)  # Technical SEO, Performance, etc.
    check_name = Column(String, nullable=False)
    status = Column(SQLEnum(CheckStatus), nullable=False)
    impact_score = Column(Integer)  # 0-100
    current_value = Column(String)
    recommended_value = Column(String)
    pros = Column(JSON)  # List of pros
    cons = Column(JSON)  # List of cons
    ranking_impact = Column(Text)
    solution = Column(Text)
    enhancements = Column(JSON)  # List of enhancement suggestions
    details = Column(JSON)  # Additional check-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    audit = relationship("Audit", back_populates="results")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    audit_id = Column(String, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    audit = relationship("Audit", back_populates="chat_messages")


class APIToken(Base):
    __tablename__ = "api_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)  # Friendly name for the token
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="api_tokens")


class Theme(Base):
    __tablename__ = "themes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=False)  # Only one theme can be active
    
    # Color palette
    primary_color = Column(String, default="#a78bfa")  # Soft purple
    secondary_color = Column(String, default="#fbbf24")  # Soft amber
    accent_color = Column(String, default="#34d399")  # Soft emerald
    background_color = Column(String, default="#0f172a")  # Dark slate
    surface_color = Column(String, default="#1e293b")  # Lighter slate
    text_primary = Column(String, default="#f8fafc")  # Light text
    text_secondary = Column(String, default="#cbd5e1")  # Muted text
    
    # Additional theme settings
    border_radius = Column(String, default="0.75rem")  # Border radius
    font_family = Column(String, default="Inter, system-ui, sans-serif")
    custom_css = Column(Text)  # Custom CSS for advanced customization
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())



class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class PaymentHistory(Base):
    __tablename__ = "payment_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    stripe_payment_intent_id = Column(String, unique=True)
    stripe_charge_id = Column(String)
    stripe_invoice_id = Column(String)
    amount = Column(Float, nullable=False)  # Amount in USD
    currency = Column(String, default="usd")
    status = Column(SQLEnum(PaymentStatus), nullable=False)
    payment_method_type = Column(String)  # card, bank_transfer, etc.
    payment_method_last4 = Column(String)  # Last 4 digits of card
    payment_method_brand = Column(String)  # visa, mastercard, etc.
    failure_code = Column(String)
    failure_message = Column(Text)
    refund_amount = Column(Float)
    refund_reason = Column(String)
    metadata = Column(JSON)  # Additional payment metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="payment_history")
    subscription = relationship("Subscription", backref="payment_history")


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stripe_event_id = Column(String, unique=True, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    processed = Column(Boolean, default=False)
    processing_attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    payload = Column(JSON)  # Store full event payload
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stripe_payment_method_id = Column(String, unique=True, nullable=False)
    stripe_customer_id = Column(String, nullable=False)
    type = Column(String, nullable=False)  # card, bank_account, etc.
    card_brand = Column(String)  # visa, mastercard, etc.
    card_last4 = Column(String)
    card_exp_month = Column(Integer)
    card_exp_year = Column(Integer)
    is_default = Column(Boolean, default=False)
    billing_details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="payment_methods")
