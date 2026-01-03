"""
Organization Model - Multi-Tenant Support
Enables SaaS multi-tenancy with data isolation
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class SubscriptionPlan(str, enum.Enum):
    """Subscription plan tiers"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"


class Organization(Base):
    """
    Organization/Tenant Model
    
    Each organization represents a separate customer in the SaaS platform.
    All data (customers, deals, campaigns) is isolated by organization_id.
    """
    __tablename__ = "organizations"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subdomain: Mapped[str] = mapped_column(String(63), unique=True, nullable=False, index=True)
    slug: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    
    # Subscription Info
    plan: Mapped[SubscriptionPlan] = mapped_column(
        SQLEnum(SubscriptionPlan),
        default=SubscriptionPlan.FREE,
        nullable=False
    )
    subscription_status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus),
        default=SubscriptionStatus.TRIALING,
        nullable=False
    )
    
    # Billing Integration (Stripe)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    
    # Limits & Quotas
    max_users: Mapped[int] = mapped_column(Integer, default=5)
    max_customers: Mapped[int] = mapped_column(Integer, default=1000)
    max_ai_requests_per_month: Mapped[int] = mapped_column(Integer, default=100)
    
    # Current Usage
    current_users_count: Mapped[int] = mapped_column(Integer, default=0)
    current_customers_count: Mapped[int] = mapped_column(Integer, default=0)
    current_ai_requests_this_month: Mapped[int] = mapped_column(Integer, default=0)
    
    # Contact & Settings
    owner_email: Mapped[Optional[str]] = mapped_column(String(255))
    owner_phone: Mapped[Optional[str]] = mapped_column(String(50))
    company_website: Mapped[Optional[str]] = mapped_column(String(255))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Security & Compliance
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    data_retention_days: Mapped[int] = mapped_column(Integer, default=365)
    
    # Trial Info
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        onupdate=func.now()
    )
    
    # Relationships (to be added in other models)
    # users: Mapped[List["User"]] = relationship(back_populates="organization")
    # customers: Mapped[List["Customer"]] = relationship(back_populates="organization")
    # deals: Mapped[List["Deal"]] = relationship(back_populates="organization")
    # campaigns: Mapped[List["Campaign"]] = relationship(back_populates="organization")
    
    def __repr__(self):
        return f"<Organization {self.name} ({self.plan.value})>"
    
    @property
    def is_trial_active(self) -> bool:
        """Check if trial is still active"""
        if not self.trial_ends_at:
            return False
        return datetime.utcnow() < self.trial_ends_at
    
    @property
    def is_subscription_active(self) -> bool:
        """Check if subscription is active"""
        return self.subscription_status in [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING
        ]
    
    def can_add_user(self) -> bool:
        """Check if organization can add more users"""
        return self.current_users_count < self.max_users
    
    def can_add_customer(self) -> bool:
        """Check if organization can add more customers"""
        return self.current_customers_count < self.max_customers
    
    def can_use_ai(self) -> bool:
        """Check if organization has AI requests quota remaining"""
        if self.plan == SubscriptionPlan.ENTERPRISE:
            return True  # Unlimited for enterprise
        return self.current_ai_requests_this_month < self.max_ai_requests_per_month
    
    def increment_ai_usage(self):
        """Increment AI usage counter"""
        self.current_ai_requests_this_month += 1
    
    def reset_monthly_counters(self):
        """Reset monthly usage counters (called by scheduled job)"""
        self.current_ai_requests_this_month = 0
