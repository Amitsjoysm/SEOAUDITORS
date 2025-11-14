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
    payment_metadata = Column(JSON)  # Additional payment metadata (renamed from metadata)
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



class EnvironmentKey(Base):
    """Model for storing encrypted environment keys/secrets"""
    __tablename__ = "environment_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key_name = Column(String, nullable=False, unique=True, index=True)  # e.g., "STRIPE_SECRET_KEY"
    key_value = Column(Text, nullable=False)  # Encrypted value
    description = Column(Text)  # Description of what this key is for
    category = Column(String)  # e.g., "payment", "ai", "email", "other"
    is_active = Column(Boolean, default=True)
    last_updated_by = Column(String)  # User ID who last updated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())



class LLMProvider(str, enum.Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class LLMSetting(Base):
    """Model for storing LLM configuration"""
    __tablename__ = "llm_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    provider = Column(SQLEnum(LLMProvider), nullable=False)  # groq, openai, anthropic, gemini, ollama
    model_name = Column(String, nullable=False)  # e.g., "llama-3.3-70b-versatile", "gpt-4", "claude-3-opus"
    api_key_ref = Column(String)  # Reference to environment key name (e.g., "GROQ_API_KEY")
    base_url = Column(String)  # For Ollama or custom endpoints
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=4096)
    top_p = Column(Float, default=1.0)
    is_active = Column(Boolean, default=False)  # Only one can be active
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())



class SEOSettings(Base):
    """Model for storing SEO configuration for the application"""
    __tablename__ = "seo_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Meta Tags
    site_title = Column(String, default="MJ SEO - AI-Powered SEO Audit Platform")
    site_description = Column(Text, default="Production-ready SEO audit platform with 132+ comprehensive checks, AI-powered insights, and detailed reports")
    site_keywords = Column(Text)  # Comma-separated keywords
    author = Column(String, default="MJ SEO")
    
    # Open Graph Tags
    og_title = Column(String)
    og_description = Column(Text)
    og_image = Column(String)  # URL to OG image
    og_url = Column(String)
    og_type = Column(String, default="website")
    og_site_name = Column(String, default="MJ SEO")
    
    # Twitter Card Tags
    twitter_card = Column(String, default="summary_large_image")
    twitter_site = Column(String)  # @username
    twitter_creator = Column(String)  # @username
    twitter_title = Column(String)
    twitter_description = Column(Text)
    twitter_image = Column(String)
    
    # Schema.org structured data
    organization_name = Column(String, default="MJ SEO")
    organization_logo = Column(String)
    organization_description = Column(Text)
    organization_url = Column(String)
    organization_email = Column(String)
    organization_phone = Column(String)
    organization_social_profiles = Column(JSON)  # List of social media URLs
    
    # Analytics & Tracking
    google_analytics_id = Column(String)  # GA4 Measurement ID
    google_tag_manager_id = Column(String)
    google_site_verification = Column(String)  # Meta tag content
    facebook_domain_verification = Column(String)
    
    # Additional SEO Settings
    robots_txt_content = Column(Text)
    sitemap_enabled = Column(Boolean, default=True)
    canonical_url = Column(String)
    language_code = Column(String, default="en")
    
    # Performance & Optimization
    enable_lazy_loading = Column(Boolean, default=True)
    enable_image_optimization = Column(Boolean, default=True)
    enable_minification = Column(Boolean, default=True)
    enable_compression = Column(Boolean, default=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)  # Only one can be active
    last_updated_by = Column(String)  # User ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
