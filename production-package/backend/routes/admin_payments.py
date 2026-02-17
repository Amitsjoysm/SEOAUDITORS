"""
Admin Payment Management Routes
Superadmin-only endpoints for managing payments, subscriptions, refunds, and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, extract
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import logging
import stripe
import os

from database import get_db
from models import (
    User, UserRole, Plan, Subscription, SubscriptionStatus,
    PaymentHistory, PaymentStatus, WebhookEvent
)
from auth import get_current_user

router = APIRouter(prefix="/admin/payments", tags=["Admin - Payments"])
logger = logging.getLogger(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


def require_superadmin(current_user: User = Depends(get_current_user)):
    """Dependency to ensure user is superadmin"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    return current_user


@router.get("/dashboard")
async def get_payment_dashboard(
    admin: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive payment dashboard statistics"""
    
    # Total revenue (all time)
    result = await db.execute(
        select(func.sum(PaymentHistory.amount))
        .where(PaymentHistory.status == PaymentStatus.SUCCEEDED)
    )
    total_revenue = result.scalar() or 0
    
    # Monthly recurring revenue (MRR)
    result = await db.execute(
        select(func.sum(Plan.price))
        .join(Subscription, Subscription.plan_id == Plan.id)
        .where(
            and_(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Plan.price > 0
            )
        )
    )
    mrr = result.scalar() or 0
    
    # Total active subscriptions
    result = await db.execute(
        select(func.count(Subscription.id))
        .where(Subscription.status == SubscriptionStatus.ACTIVE)
    )
    active_subscriptions = result.scalar()
    
    # Failed payments (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.execute(
        select(func.count(PaymentHistory.id))
        .where(
            and_(
                PaymentHistory.status == PaymentStatus.FAILED,
                PaymentHistory.created_at >= thirty_days_ago
            )
        )
    )
    failed_payments = result.scalar()
    
    # Revenue this month
    first_day_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.sum(PaymentHistory.amount))
        .where(
            and_(
                PaymentHistory.status == PaymentStatus.SUCCEEDED,
                PaymentHistory.created_at >= first_day_of_month
            )
        )
    )
    revenue_this_month = result.scalar() or 0
    
    # Revenue last month
    if first_day_of_month.month == 1:
        first_day_last_month = first_day_of_month.replace(year=first_day_of_month.year - 1, month=12)
    else:
        first_day_last_month = first_day_of_month.replace(month=first_day_of_month.month - 1)
    
    result = await db.execute(
        select(func.sum(PaymentHistory.amount))
        .where(
            and_(
                PaymentHistory.status == PaymentStatus.SUCCEEDED,
                PaymentHistory.created_at >= first_day_last_month,
                PaymentHistory.created_at < first_day_of_month
            )
        )
    )
    revenue_last_month = result.scalar() or 0
    
    # Churn rate (cancelled subscriptions in last 30 days / total active at start)
    result = await db.execute(
        select(func.count(Subscription.id))
        .where(
            and_(
                Subscription.status == SubscriptionStatus.CANCELLED,
                Subscription.updated_at >= thirty_days_ago
            )
        )
    )
    cancelled_count = result.scalar()
    
    churn_rate = (cancelled_count / max(active_subscriptions, 1)) * 100 if active_subscriptions > 0 else 0
    
    # Subscription distribution by plan
    result = await db.execute(
        select(
            Plan.display_name,
            Plan.price,
            func.count(Subscription.id).label('count')
        )
        .join(Subscription, Subscription.plan_id == Plan.id)
        .where(Subscription.status == SubscriptionStatus.ACTIVE)
        .group_by(Plan.id, Plan.display_name, Plan.price)
    )
    subscription_distribution = [
        {"plan": row.display_name, "price": row.price, "count": row.count}
        for row in result.all()
    ]
    
    # Recent failed payments
    result = await db.execute(
        select(PaymentHistory)
        .where(PaymentHistory.status == PaymentStatus.FAILED)
        .order_by(desc(PaymentHistory.created_at))
        .limit(10)
    )
    recent_failures = result.scalars().all()
    
    # Monthly revenue trend (last 6 months)
    monthly_revenue = []
    for i in range(6, 0, -1):
        month_start = (datetime.now(timezone.utc) - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        result = await db.execute(
            select(func.sum(PaymentHistory.amount))
            .where(
                and_(
                    PaymentHistory.status == PaymentStatus.SUCCEEDED,
                    PaymentHistory.created_at >= month_start,
                    PaymentHistory.created_at < month_end
                )
            )
        )
        revenue = result.scalar() or 0
        monthly_revenue.append({
            "month": month_start.strftime("%Y-%m"),
            "revenue": revenue
        })
    
    return {
        "overview": {
            "total_revenue": round(total_revenue, 2),
            "mrr": round(mrr, 2),
            "active_subscriptions": active_subscriptions,
            "failed_payments_30d": failed_payments,
            "revenue_this_month": round(revenue_this_month, 2),
            "revenue_last_month": round(revenue_last_month, 2),
            "churn_rate": round(churn_rate, 2)
        },
        "subscription_distribution": subscription_distribution,
        "recent_failures": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "amount": p.amount,
                "failure_message": p.failure_message,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in recent_failures
        ],
        "monthly_revenue_trend": monthly_revenue
    }


@router.get("/transactions")
async def get_all_transactions(
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    admin: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get all payment transactions with filters"""
    query = select(PaymentHistory).join(User, User.id == PaymentHistory.user_id)
    
    # Apply filters
    filters = []
    if status:
        try:
            payment_status = PaymentStatus(status)
            filters.append(PaymentHistory.status == payment_status)
        except ValueError:
            pass
    
    if user_id:
        filters.append(PaymentHistory.user_id == user_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(desc(PaymentHistory.created_at)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    payments = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(PaymentHistory.id))
    if filters:
        count_query = count_query.where(and_(*filters))
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # Get user emails
    transactions = []
    for payment in payments:
        user = await db.get(User, payment.user_id)
        transactions.append({
            "id": payment.id,
            "user_id": payment.user_id,
            "user_email": user.email if user else None,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "payment_method_type": payment.payment_method_type,
            "payment_method_last4": payment.payment_method_last4,
            "payment_method_brand": payment.payment_method_brand,
            "stripe_payment_intent_id": payment.stripe_payment_intent_id,
            "stripe_charge_id": payment.stripe_charge_id,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "refund_amount": payment.refund_amount,
            "refund_reason": payment.refund_reason,
            "failure_message": payment.failure_message
        })
    
    return {
        "transactions": transactions,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/subscriptions")
async def get_all_subscriptions(
    status: Optional[str] = None,
    plan_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    admin: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get all subscriptions with filters"""
    from sqlalchemy.orm import selectinload
    
    query = select(Subscription).options(
        selectinload(Subscription.user),
        selectinload(Subscription.plan)
    )
    
    # Apply filters
    filters = []
    if status:
        try:
            sub_status = SubscriptionStatus(status)
            filters.append(Subscription.status == sub_status)
        except ValueError:
            pass
    
    if plan_id:
        filters.append(Subscription.plan_id == plan_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(desc(Subscription.created_at)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    
    # Get total count
    count_query = select(func.count(Subscription.id))
    if filters:
        count_query = count_query.where(and_(*filters))
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return {
        "subscriptions": [
            {
                "id": sub.id,
                "user_id": sub.user_id,
                "user_email": sub.user.email,
                "plan_name": sub.plan.display_name,
                "plan_price": sub.plan.price,
                "status": sub.status,
                "stripe_subscription_id": sub.stripe_subscription_id,
                "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
                "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
                "cancel_at_period_end": sub.cancel_at_period_end,
                "audits_used_this_month": sub.audits_used_this_month,
                "created_at": sub.created_at.isoformat() if sub.created_at else None
            }
            for sub in subscriptions
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/refund/{payment_id}")
async def refund_payment(
    payment_id: str,
    amount: Optional[float] = None,
    reason: Optional[str] = None,
    admin: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Issue a refund for a payment"""
    # Get payment
    payment = await db.get(PaymentHistory, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != PaymentStatus.SUCCEEDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refund succeeded payments"
        )
    
    if not payment.stripe_charge_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No charge ID found for this payment"
        )
    
    # Calculate refund amount
    refund_amount_cents = int((amount or payment.amount) * 100)
    
    try:
        # Create refund in Stripe
        refund = stripe.Refund.create(
            charge=payment.stripe_charge_id,
            amount=refund_amount_cents,
            reason=reason or 'requested_by_customer',
            metadata={
                'admin_id': admin.id,
                'admin_email': admin.email
            }
        )
        
        # Update payment record
        payment.status = PaymentStatus.REFUNDED
        payment.refund_amount = refund_amount_cents / 100
        payment.refund_reason = reason
        await db.commit()
        
        logger.info(f"Refunded ${refund_amount_cents/100} for payment {payment_id} by admin {admin.id}")
        
        return {
            "message": "Refund issued successfully",
            "refund_id": refund.id,
            "amount_refunded": refund_amount_cents / 100
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Refund error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refund failed: {str(e)}"
        )


@router.post("/cancel-subscription/{subscription_id}")
async def admin_cancel_subscription(
    subscription_id: str,
    immediate: bool = False,
    admin: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Admin cancel a user's subscription"""
    subscription = await db.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    if not subscription.stripe_subscription_id:
        # Free plan
        subscription.status = SubscriptionStatus.CANCELLED
        await db.commit()
        return {"message": "Free subscription cancelled"}
    
    try:
        if immediate:
            stripe.Subscription.delete(subscription.stripe_subscription_id)
            subscription.status = SubscriptionStatus.CANCELLED
            message = "Subscription cancelled immediately"
        else:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            subscription.cancel_at_period_end = True
            message = "Subscription will be cancelled at period end"
        
        await db.commit()
        logger.info(f"Admin {admin.id} cancelled subscription {subscription_id}")
        
        return {"message": message}
        
    except stripe.error.StripeError as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.post("/extend-subscription/{subscription_id}")
async def extend_subscription(
    subscription_id: str,
    days: int,
    admin: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Extend a subscription period (manual credit)"""
    subscription = await db.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Extend period end
    if subscription.current_period_end:
        subscription.current_period_end += timedelta(days=days)
    else:
        subscription.current_period_end = datetime.now(timezone.utc) + timedelta(days=days)
    
    await db.commit()
    logger.info(f"Admin {admin.id} extended subscription {subscription_id} by {days} days")
    
    return {
        "message": f"Subscription extended by {days} days",
        "new_period_end": subscription.current_period_end.isoformat()
    }


@router.get("/webhook-events")
async def get_webhook_events(
    processed: Optional[bool] = None,
    event_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    admin: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get webhook events log"""
    query = select(WebhookEvent)
    
    filters = []
    if processed is not None:
        filters.append(WebhookEvent.processed == processed)
    if event_type:
        filters.append(WebhookEvent.event_type == event_type)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(desc(WebhookEvent.created_at)).limit(limit).offset(offset)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return {
        "events": [
            {
                "id": e.id,
                "stripe_event_id": e.stripe_event_id,
                "event_type": e.event_type,
                "processed": e.processed,
                "processing_attempts": e.processing_attempts,
                "error_message": e.error_message,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "processed_at": e.processed_at.isoformat() if e.processed_at else None
            }
            for e in events
        ],
        "total": len(events)
    }


@router.post("/retry-webhook/{event_id}")
async def retry_webhook_event(
    event_id: str,
    admin: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Manually retry a failed webhook event"""
    event = await db.get(WebhookEvent, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook event not found"
        )
    
    if event.processed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event already processed successfully"
        )
    
    # Reset processing flag
    event.processed = False
    event.error_message = None
    await db.commit()
    
    # TODO: Trigger webhook processing
    logger.info(f"Admin {admin.id} requested retry for webhook {event_id}")
    
    return {"message": "Webhook will be retried"}


@router.get("/failed-payments")
async def get_failed_payments(
    days: int = 30,
    admin: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get failed payments with user details for follow-up"""
    from sqlalchemy.orm import selectinload
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    result = await db.execute(
        select(PaymentHistory)
        .where(
            and_(
                PaymentHistory.status == PaymentStatus.FAILED,
                PaymentHistory.created_at >= cutoff_date
            )
        )
        .order_by(desc(PaymentHistory.created_at))
    )
    failed_payments = result.scalars().all()
    
    # Get user details
    payments_with_users = []
    for payment in failed_payments:
        user = await db.get(User, payment.user_id)
        subscription = None
        if payment.subscription_id:
            subscription = await db.get(Subscription, payment.subscription_id)
        
        payments_with_users.append({
            "payment_id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "failure_code": payment.failure_code,
            "failure_message": payment.failure_message,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "stripe_customer_id": user.stripe_customer_id
            } if user else None,
            "subscription_status": subscription.status if subscription else None
        })
    
    return {
        "failed_payments": payments_with_users,
        "total": len(payments_with_users),
        "period_days": days
    }


@router.get("/revenue-report")
async def get_revenue_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Generate detailed revenue report"""
    # Default to last 30 days if no dates provided
    if not start_date:
        start = datetime.now(timezone.utc) - timedelta(days=30)
    else:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    
    if not end_date:
        end = datetime.now(timezone.utc)
    else:
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    # Total revenue in period
    result = await db.execute(
        select(func.sum(PaymentHistory.amount))
        .where(
            and_(
                PaymentHistory.status == PaymentStatus.SUCCEEDED,
                PaymentHistory.created_at >= start,
                PaymentHistory.created_at <= end
            )
        )
    )
    total_revenue = result.scalar() or 0
    
    # Revenue by plan
    result = await db.execute(
        select(
            Plan.display_name,
            Plan.price,
            func.count(PaymentHistory.id).label('payment_count'),
            func.sum(PaymentHistory.amount).label('revenue')
        )
        .join(Subscription, Subscription.id == PaymentHistory.subscription_id)
        .join(Plan, Plan.id == Subscription.plan_id)
        .where(
            and_(
                PaymentHistory.status == PaymentStatus.SUCCEEDED,
                PaymentHistory.created_at >= start,
                PaymentHistory.created_at <= end
            )
        )
        .group_by(Plan.id, Plan.display_name, Plan.price)
    )
    revenue_by_plan = [
        {
            "plan": row.display_name,
            "price": row.price,
            "payment_count": row.payment_count,
            "revenue": row.revenue or 0
        }
        for row in result.all()
    ]
    
    # Number of transactions
    result = await db.execute(
        select(func.count(PaymentHistory.id))
        .where(
            and_(
                PaymentHistory.status == PaymentStatus.SUCCEEDED,
                PaymentHistory.created_at >= start,
                PaymentHistory.created_at <= end
            )
        )
    )
    transaction_count = result.scalar()
    
    # Refunded amount
    result = await db.execute(
        select(func.sum(PaymentHistory.refund_amount))
        .where(
            and_(
                PaymentHistory.status == PaymentStatus.REFUNDED,
                PaymentHistory.created_at >= start,
                PaymentHistory.created_at <= end
            )
        )
    )
    refunded_amount = result.scalar() or 0
    
    return {
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat()
        },
        "total_revenue": round(total_revenue, 2),
        "transaction_count": transaction_count,
        "refunded_amount": round(refunded_amount, 2),
        "net_revenue": round(total_revenue - refunded_amount, 2),
        "revenue_by_plan": revenue_by_plan
    }
