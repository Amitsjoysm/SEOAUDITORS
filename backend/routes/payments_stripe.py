"""
Complete Stripe Payment System with Advanced Features
Includes: Checkout, Webhooks, Subscriptions, Refunds, Payment Methods, Fraud Prevention
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import logging
import uuid
import os
import asyncio

from database import get_db
from models import (
    User, Plan, Subscription, SubscriptionStatus,
    PaymentHistory, PaymentStatus, WebhookEvent, PaymentMethod
)
from auth import get_current_user
import stripe

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Webhook processing lock to prevent duplicate processing
webhook_locks = {}


async def get_or_create_stripe_customer(user: User, db: AsyncSession) -> str:
    """Get existing Stripe customer or create a new one"""
    if user.stripe_customer_id:
        try:
            # Verify customer exists in Stripe
            stripe.Customer.retrieve(user.stripe_customer_id)
            return user.stripe_customer_id
        except stripe.error.InvalidRequestError:
            # Customer doesn't exist, create new one
            pass
    
    # Create new customer
    try:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name or user.email,
            metadata={
                "user_id": user.id,
                "role": user.role
            }
        )
        user.stripe_customer_id = customer.id
        await db.commit()
        logger.info(f"Created Stripe customer {customer.id} for user {user.id}")
        return customer.id
    except Exception as e:
        logger.error(f"Failed to create Stripe customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment account"
        )


@router.post("/create-checkout-session")
async def create_checkout_session(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Stripe Checkout Session for subscription
    Includes fraud prevention and security measures
    """
    # Get plan
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = result.scalar_one_or_none()
    
    if not plan or not plan.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or inactive"
        )
    
    # Check if plan is free
    if plan.price == 0:
        # Create free subscription directly
        await create_free_subscription(current_user, plan, db)
        return {
            "status": "success",
            "message": "Free plan activated",
            "redirect_url": f"{FRONTEND_URL}/dashboard?subscription=activated"
        }
    
    # Check for existing active subscription
    result = await db.execute(
        select(Subscription).where(
            and_(
                Subscription.user_id == current_user.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
    )
    existing_subscription = result.scalar_one_or_none()
    
    if existing_subscription:
        # Handle upgrade/downgrade
        if existing_subscription.plan_id == plan_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have this plan"
            )
        # Will be handled in subscription change flow
    
    # Get or create Stripe customer
    customer_id = await get_or_create_stripe_customer(current_user, db)
    
    if not stripe.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system is not configured"
        )
    
    if not plan.stripe_price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This plan is not available for purchase"
        )
    
    try:
        # Create Stripe checkout session with fraud prevention
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': plan.stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/plans?payment=cancelled",
            
            # Security and fraud prevention
            allow_promotion_codes=True,
            billing_address_collection='required',
            
            # Automatic tax calculation (if enabled in Stripe)
            automatic_tax={'enabled': False},  # Set to True if you configure tax
            
            # Metadata for webhook processing
            metadata={
                'user_id': current_user.id,
                'plan_id': plan_id,
                'user_email': current_user.email
            },
            
            # Subscription configuration
            subscription_data={
                'metadata': {
                    'user_id': current_user.id,
                    'plan_id': plan_id
                },
                # Trial period if configured
                # 'trial_period_days': 7,
            },
            
            # Payment intent data for fraud prevention
            payment_intent_data={
                'metadata': {
                    'user_id': current_user.id,
                    'plan_id': plan_id
                }
            }
        )
        
        logger.info(f"Created checkout session {session.id} for user {current_user.id}")
        
        return {
            "session_id": session.id,
            "checkout_url": session.url,
            "public_key": os.getenv("STRIPE_PUBLISHABLE_KEY", "")
        }
        
    except stripe.error.CardError as e:
        logger.error(f"Card error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except stripe.error.RateLimitError as e:
        logger.error(f"Rate limit error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )
    except stripe.error.InvalidRequestError as e:
        logger.error(f"Invalid request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment request"
        )
    except stripe.error.AuthenticationError as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment system authentication failed"
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment processing error"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


async def create_free_subscription(user: User, plan: Plan, db: AsyncSession):
    """Create a free subscription without payment"""
    # Check if user already has this plan
    result = await db.execute(
        select(Subscription).where(
            and_(
                Subscription.user_id == user.id,
                Subscription.plan_id == plan.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if not existing:
        subscription = Subscription(
            id=str(uuid.uuid4()),
            user_id=user.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc) + timedelta(days=365),  # 1 year for free
            cancel_at_period_end=False,
            audits_used_this_month=0
        )
        db.add(subscription)
        await db.commit()
        logger.info(f"Created free subscription for user {user.id}")


@router.post("/stripe-webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe webhook events with idempotency and security
    Processes: checkout, subscriptions, payments, refunds, disputes
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    if not STRIPE_WEBHOOK_SECRET:
        logger.error("Webhook secret not configured")
        raise HTTPException(status_code=500, detail="Webhook not configured")
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event_id = event['id']
    event_type = event['type']
    
    logger.info(f"Received webhook event: {event_type} (ID: {event_id})")
    
    # Check if event already processed (idempotency)
    result = await db.execute(
        select(WebhookEvent).where(WebhookEvent.stripe_event_id == event_id)
    )
    existing_event = result.scalar_one_or_none()
    
    if existing_event:
        if existing_event.processed:
            logger.info(f"Event {event_id} already processed, skipping")
            return {"status": "success", "message": "Already processed"}
        else:
            # Event failed before, retry
            logger.info(f"Retrying failed event {event_id}")
    else:
        # Create new webhook event record
        webhook_event = WebhookEvent(
            id=str(uuid.uuid4()),
            stripe_event_id=event_id,
            event_type=event_type,
            payload=event.to_dict(),
            processing_attempts=0
        )
        db.add(webhook_event)
        await db.commit()
        existing_event = webhook_event
    
    # Acquire lock for this event to prevent concurrent processing
    if event_id in webhook_locks:
        logger.warning(f"Event {event_id} is already being processed")
        return {"status": "processing"}
    
    webhook_locks[event_id] = True
    
    try:
        # Update processing attempt
        existing_event.processing_attempts += 1
        existing_event.last_attempt_at = datetime.now(timezone.utc)
        await db.commit()
        
        # Process event based on type
        if event_type == 'checkout.session.completed':
            await handle_checkout_completed(event['data']['object'], db)
        
        elif event_type == 'customer.subscription.updated':
            await handle_subscription_updated(event['data']['object'], db)
        
        elif event_type == 'customer.subscription.deleted':
            await handle_subscription_deleted(event['data']['object'], db)
        
        elif event_type == 'invoice.payment_succeeded':
            await handle_payment_succeeded(event['data']['object'], db)
        
        elif event_type == 'invoice.payment_failed':
            await handle_payment_failed(event['data']['object'], db)
        
        elif event_type == 'customer.subscription.trial_will_end':
            await handle_trial_ending(event['data']['object'], db)
        
        elif event_type == 'charge.refunded':
            await handle_charge_refunded(event['data']['object'], db)
        
        elif event_type == 'charge.dispute.created':
            await handle_dispute_created(event['data']['object'], db)
        
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        # Mark event as processed
        existing_event.processed = True
        existing_event.processed_at = datetime.now(timezone.utc)
        await db.commit()
        
        logger.info(f"Successfully processed event {event_id}")
        
    except Exception as e:
        logger.error(f"Error processing webhook {event_id}: {str(e)}", exc_info=True)
        existing_event.error_message = str(e)
        await db.commit()
        raise
    
    finally:
        # Release lock
        if event_id in webhook_locks:
            del webhook_locks[event_id]
    
    return {"status": "success"}


async def handle_checkout_completed(session: dict, db: AsyncSession):
    """Handle successful checkout session completion"""
    try:
        user_id = session['metadata'].get('user_id')
        plan_id = session['metadata'].get('plan_id')
        subscription_id = session.get('subscription')
        customer_id = session.get('customer')
        
        if not user_id or not plan_id:
            logger.error("Missing metadata in checkout session")
            return
        
        # Get user and plan
        user = await db.get(User, user_id)
        plan = await db.get(Plan, plan_id)
        
        if not user or not plan:
            logger.error(f"User {user_id} or Plan {plan_id} not found")
            return
        
        # Cancel any existing active subscriptions
        result = await db.execute(
            select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status == SubscriptionStatus.ACTIVE
                )
            )
        )
        existing_subs = result.scalars().all()
        for sub in existing_subs:
            sub.status = SubscriptionStatus.CANCELLED
            sub.cancel_at_period_end = True
        
        # Get subscription details from Stripe
        stripe_sub = stripe.Subscription.retrieve(subscription_id)
        
        # Create new subscription
        subscription = Subscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            plan_id=plan_id,
            stripe_subscription_id=subscription_id,
            stripe_customer_id=customer_id,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.fromtimestamp(stripe_sub.current_period_start, tz=timezone.utc),
            current_period_end=datetime.fromtimestamp(stripe_sub.current_period_end, tz=timezone.utc),
            cancel_at_period_end=False,
            audits_used_this_month=0
        )
        db.add(subscription)
        
        # Update user's Stripe customer ID
        user.stripe_customer_id = customer_id
        
        await db.commit()
        logger.info(f"Created subscription {subscription.id} for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in handle_checkout_completed: {str(e)}")
        await db.rollback()
        raise


async def handle_subscription_updated(subscription_data: dict, db: AsyncSession):
    """Handle subscription updates (renewals, plan changes, etc.)"""
    try:
        stripe_subscription_id = subscription_data['id']
        
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription_id
            )
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            logger.warning(f"Subscription {stripe_subscription_id} not found in database")
            return
        
        # Update subscription details
        stripe_status = subscription_data['status']
        
        # Map Stripe status to our status
        status_map = {
            'active': SubscriptionStatus.ACTIVE,
            'canceled': SubscriptionStatus.CANCELLED,
            'past_due': SubscriptionStatus.PAST_DUE,
            'incomplete': SubscriptionStatus.INCOMPLETE,
            'trialing': SubscriptionStatus.TRIALING
        }
        
        subscription.status = status_map.get(stripe_status, SubscriptionStatus.ACTIVE)
        subscription.current_period_start = datetime.fromtimestamp(
            subscription_data['current_period_start'], tz=timezone.utc
        )
        subscription.current_period_end = datetime.fromtimestamp(
            subscription_data['current_period_end'], tz=timezone.utc
        )
        subscription.cancel_at_period_end = subscription_data.get('cancel_at_period_end', False)
        
        await db.commit()
        logger.info(f"Updated subscription {subscription.id} - Status: {subscription.status}")
        
    except Exception as e:
        logger.error(f"Error in handle_subscription_updated: {str(e)}")
        await db.rollback()
        raise


async def handle_subscription_deleted(subscription_data: dict, db: AsyncSession):
    """Handle subscription cancellation"""
    try:
        stripe_subscription_id = subscription_data['id']
        
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription_id
            )
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancel_at_period_end = True
            await db.commit()
            logger.info(f"Cancelled subscription {subscription.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_subscription_deleted: {str(e)}")
        await db.rollback()
        raise


async def handle_payment_succeeded(invoice: dict, db: AsyncSession):
    """Handle successful payment"""
    try:
        customer_id = invoice['customer']
        subscription_id = invoice.get('subscription')
        payment_intent_id = invoice.get('payment_intent')
        charge_id = invoice.get('charge')
        amount_paid = invoice['amount_paid'] / 100  # Convert cents to dollars
        
        # Find user by Stripe customer ID
        result = await db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return
        
        # Find subscription
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()
        
        # Get payment method details if available
        payment_method_type = None
        payment_method_last4 = None
        payment_method_brand = None
        
        if charge_id:
            try:
                charge = stripe.Charge.retrieve(charge_id)
                payment_method_type = charge.payment_method_details.get('type')
                if payment_method_type == 'card':
                    card_details = charge.payment_method_details.get('card', {})
                    payment_method_last4 = card_details.get('last4')
                    payment_method_brand = card_details.get('brand')
            except Exception as e:
                logger.warning(f"Could not retrieve charge details: {str(e)}")
        
        # Create payment history record
        payment_history = PaymentHistory(
            id=str(uuid.uuid4()),
            user_id=user.id,
            subscription_id=subscription.id if subscription else None,
            stripe_payment_intent_id=payment_intent_id,
            stripe_charge_id=charge_id,
            stripe_invoice_id=invoice['id'],
            amount=amount_paid,
            currency=invoice.get('currency', 'usd'),
            status=PaymentStatus.SUCCEEDED,
            payment_method_type=payment_method_type,
            payment_method_last4=payment_method_last4,
            payment_method_brand=payment_method_brand,
            metadata={
                'invoice_number': invoice.get('number'),
                'period_start': invoice.get('period_start'),
                'period_end': invoice.get('period_end')
            }
        )
        db.add(payment_history)
        
        # Reset usage counter if new billing period
        if subscription:
            subscription.audits_used_this_month = 0
        
        await db.commit()
        logger.info(f"Recorded successful payment ${amount_paid} for user {user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_payment_succeeded: {str(e)}")
        await db.rollback()
        raise


async def handle_payment_failed(invoice: dict, db: AsyncSession):
    """Handle failed payment"""
    try:
        customer_id = invoice['customer']
        subscription_id = invoice.get('subscription')
        payment_intent_id = invoice.get('payment_intent')
        amount = invoice['amount_due'] / 100
        
        # Get failure details
        last_error = invoice.get('last_finalization_error') or {}
        failure_code = last_error.get('code')
        failure_message = last_error.get('message', 'Payment failed')
        
        # Find user
        result = await db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return
        
        # Find subscription
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()
        
        # Create payment history record for failed payment
        payment_history = PaymentHistory(
            id=str(uuid.uuid4()),
            user_id=user.id,
            subscription_id=subscription.id if subscription else None,
            stripe_payment_intent_id=payment_intent_id,
            stripe_invoice_id=invoice['id'],
            amount=amount,
            currency=invoice.get('currency', 'usd'),
            status=PaymentStatus.FAILED,
            failure_code=failure_code,
            failure_message=failure_message,
            metadata={
                'invoice_number': invoice.get('number'),
                'attempt_count': invoice.get('attempt_count', 0)
            }
        )
        db.add(payment_history)
        
        # Update subscription status
        if subscription:
            subscription.status = SubscriptionStatus.PAST_DUE
        
        await db.commit()
        logger.warning(f"Payment failed for user {user.id}: {failure_message}")
        
        # TODO: Send email notification to user about failed payment
        
    except Exception as e:
        logger.error(f"Error in handle_payment_failed: {str(e)}")
        await db.rollback()
        raise


async def handle_trial_ending(subscription_data: dict, db: AsyncSession):
    """Handle trial period ending notification"""
    # TODO: Send email to user that trial is ending
    logger.info(f"Trial ending for subscription {subscription_data['id']}")


async def handle_charge_refunded(charge: dict, db: AsyncSession):
    """Handle charge refund"""
    try:
        charge_id = charge['id']
        refund_amount = charge['amount_refunded'] / 100
        
        # Find payment history
        result = await db.execute(
            select(PaymentHistory).where(
                PaymentHistory.stripe_charge_id == charge_id
            )
        )
        payment = result.scalar_one_or_none()
        
        if payment:
            payment.status = PaymentStatus.REFUNDED
            payment.refund_amount = refund_amount
            payment.refund_reason = charge.get('refunds', {}).get('data', [{}])[0].get('reason')
            await db.commit()
            logger.info(f"Recorded refund of ${refund_amount} for payment {payment.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_charge_refunded: {str(e)}")
        await db.rollback()


async def handle_dispute_created(dispute: dict, db: AsyncSession):
    """Handle charge dispute"""
    try:
        charge_id = dispute['charge']
        
        # Find payment history
        result = await db.execute(
            select(PaymentHistory).where(
                PaymentHistory.stripe_charge_id == charge_id
            )
        )
        payment = result.scalar_one_or_none()
        
        if payment:
            payment.status = PaymentStatus.DISPUTED
            payment.metadata = payment.metadata or {}
            payment.metadata['dispute_reason'] = dispute.get('reason')
            payment.metadata['dispute_status'] = dispute.get('status')
            await db.commit()
            logger.warning(f"Dispute created for payment {payment.id}: {dispute.get('reason')}")
        
    except Exception as e:
        logger.error(f"Error in handle_dispute_created: {str(e)}")
        await db.rollback()


# User-facing endpoints

@router.get("/subscription")
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's active subscription with plan details"""
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(
            and_(
                Subscription.user_id == current_user.id,
                or_(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.status == SubscriptionStatus.TRIALING
                )
            )
        )
        .order_by(Subscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        # Check if user should have free plan
        result = await db.execute(
            select(Plan).where(and_(Plan.price == 0, Plan.is_active == True))
        )
        free_plan = result.scalar_one_or_none()
        
        if free_plan:
            # Create free subscription
            await create_free_subscription(current_user, free_plan, db)
            # Fetch the newly created subscription
            result = await db.execute(
                select(Subscription)
                .options(selectinload(Subscription.plan))
                .where(
                    Subscription.user_id == current_user.id
                )
                .order_by(Subscription.created_at.desc())
            )
            subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return {
        "id": subscription.id,
        "status": subscription.status,
        "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
        "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        "cancel_at_period_end": subscription.cancel_at_period_end,
        "audits_used_this_month": subscription.audits_used_this_month,
        "plan": {
            "id": subscription.plan.id,
            "name": subscription.plan.name,
            "display_name": subscription.plan.display_name,
            "price": subscription.plan.price,
            "max_audits_per_month": subscription.plan.max_audits_per_month,
            "max_pages_per_audit": subscription.plan.max_pages_per_audit,
            "features": subscription.plan.features
        }
    }


@router.post("/cancel-subscription")
async def cancel_subscription(
    immediate: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel current subscription (at period end or immediately)"""
    result = await db.execute(
        select(Subscription).where(
            and_(
                Subscription.user_id == current_user.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    if not subscription.stripe_subscription_id:
        # Free plan - cancel immediately
        subscription.status = SubscriptionStatus.CANCELLED
        await db.commit()
        return {"message": "Subscription cancelled"}
    
    try:
        if immediate:
            # Cancel immediately
            stripe.Subscription.delete(subscription.stripe_subscription_id)
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancel_at_period_end = True
            message = "Subscription cancelled immediately"
        else:
            # Cancel at period end
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            subscription.cancel_at_period_end = True
            message = "Subscription will be cancelled at the end of billing period"
        
        await db.commit()
        logger.info(f"Cancelled subscription {subscription.id} for user {current_user.id}")
        
        return {"message": message, "cancel_at_period_end": subscription.cancel_at_period_end}
        
    except stripe.error.StripeError as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.get("/payment-history")
async def get_payment_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's payment history"""
    result = await db.execute(
        select(PaymentHistory)
        .where(PaymentHistory.user_id == current_user.id)
        .order_by(desc(PaymentHistory.created_at))
        .limit(limit)
        .offset(offset)
    )
    payments = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(PaymentHistory.id))
        .where(PaymentHistory.user_id == current_user.id)
    )
    total = count_result.scalar()
    
    return {
        "payments": [
            {
                "id": p.id,
                "amount": p.amount,
                "currency": p.currency,
                "status": p.status,
                "payment_method_type": p.payment_method_type,
                "payment_method_last4": p.payment_method_last4,
                "payment_method_brand": p.payment_method_brand,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "refund_amount": p.refund_amount,
                "refund_reason": p.refund_reason,
                "failure_message": p.failure_message
            }
            for p in payments
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/change-plan")
async def change_subscription_plan(
    new_plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade or downgrade subscription plan"""
    # Get current subscription
    result = await db.execute(
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(
            and_(
                Subscription.user_id == current_user.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
    )
    current_subscription = result.scalar_one_or_none()
    
    if not current_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    # Get new plan
    new_plan = await db.get(Plan, new_plan_id)
    if not new_plan or not new_plan.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or inactive"
        )
    
    if current_subscription.plan_id == new_plan_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already on this plan"
        )
    
    # Handle free plan changes
    if new_plan.price == 0:
        # Downgrade to free - cancel current subscription
        if current_subscription.stripe_subscription_id:
            try:
                stripe.Subscription.delete(current_subscription.stripe_subscription_id)
            except:
                pass
        current_subscription.status = SubscriptionStatus.CANCELLED
        await create_free_subscription(current_user, new_plan, db)
        return {"message": "Downgraded to free plan"}
    
    if not current_subscription.stripe_subscription_id:
        # Upgrading from free - create checkout session
        return await create_checkout_session(new_plan_id, current_user, db)
    
    # Upgrade/Downgrade paid subscription
    try:
        stripe_subscription = stripe.Subscription.retrieve(current_subscription.stripe_subscription_id)
        
        # Update subscription item
        stripe.Subscription.modify(
            current_subscription.stripe_subscription_id,
            cancel_at_period_end=False,
            proration_behavior='create_prorations',  # Prorate charges
            items=[{
                'id': stripe_subscription['items']['data'][0].id,
                'price': new_plan.stripe_price_id,
            }]
        )
        
        # Update local subscription
        current_subscription.plan_id = new_plan_id
        await db.commit()
        
        logger.info(f"Changed plan for user {current_user.id} to {new_plan_id}")
        
        return {
            "message": "Plan changed successfully",
            "new_plan": new_plan.display_name,
            "proration": "You will be charged/credited the prorated amount"
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Error changing plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change plan"
        )


@router.get("/billing-portal")
async def create_billing_portal_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create Stripe billing portal session for managing payment methods, invoices, etc."""
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No billing account found"
        )
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=f"{FRONTEND_URL}/settings"
        )
        
        return {
            "url": session.url
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Error creating billing portal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create billing portal"
        )
