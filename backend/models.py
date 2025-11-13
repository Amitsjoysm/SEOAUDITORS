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
    metadata = Column(JSON)  # Store crawled data, timings, etc.
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
