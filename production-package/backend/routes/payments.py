"""Payment processing routes for Stripe and Razorpay"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Literal
import logging
import uuid
import os
from datetime import datetime, timezone, timedelta

from database import get_db
from models import User, Plan, Subscription, SubscriptionStatus
from schemas import SubscriptionResponse
from auth import get_current_user
import stripe
import razorpay

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)

# Configure payment providers
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
razorpay_client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID", ""),
        os.getenv("RAZORPAY_KEY_SECRET", "")
    )
) if os.getenv("RAZORPAY_KEY_ID") else None


@router.post("/create-checkout-session")
async def create_checkout_session(
    plan_id: str,
    provider: Literal["stripe", "razorpay"],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a payment checkout session"""
    # Get plan
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = result.scalar_one_or_none()
    
    if not plan or not plan.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or inactive"
        )
    
    if provider == "stripe":
        if not stripe.api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe is not configured"
            )
        
        try:
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                customer_email=current_user.email,
                payment_method_types=['card'],
                line_items=[{
                    'price': plan.stripe_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=os.getenv('FRONTEND_URL', 'http://localhost:3000') + '/dashboard?payment=success',
                cancel_url=os.getenv('FRONTEND_URL', 'http://localhost:3000') + '/dashboard?payment=cancelled',
                metadata={
                    'user_id': current_user.id,
                    'plan_id': plan_id
                }
            )
            
            return {
                "provider": "stripe",
                "session_id": session.id,
                "checkout_url": session.url
            }
            
        except Exception as e:
            logger.error(f"Stripe error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Stripe error: {str(e)}"
            )
    
    elif provider == "razorpay":
        if not razorpay_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Razorpay is not configured"
            )
        
        try:
            # Create Razorpay subscription
            subscription_data = {
                "plan_id": plan.razorpay_plan_id if hasattr(plan, 'razorpay_plan_id') else None,
                "customer_notify": 1,
                "total_count": 12,  # Monthly for 1 year
                "notes": {
                    "user_id": current_user.id,
                    "plan_id": plan_id
                }
            }
            
            # If no Razorpay plan, create a payment link instead
            if not subscription_data["plan_id"]:
                # Create payment link for one-time monthly payment
                payment_link = razorpay_client.payment_link.create({
                    "amount": int(plan.price * 100),  # Amount in paise
                    "currency": "INR",
                    "description": f"MJ SEO - {plan.display_name}",
                    "customer": {
                        "email": current_user.email,
                        "name": current_user.full_name or current_user.email
                    },
                    "callback_url": os.getenv('FRONTEND_URL', 'http://localhost:3000') + '/dashboard?payment=success',
                    "callback_method": "get"
                })
                
                return {
                    "provider": "razorpay",
                    "payment_link_id": payment_link['id'],
                    "checkout_url": payment_link['short_url']
                }
            else:
                subscription = razorpay_client.subscription.create(subscription_data)
                
                return {
                    "provider": "razorpay",
                    "subscription_id": subscription['id'],
                    "checkout_url": subscription['short_url']
                }
            
        except Exception as e:
            logger.error(f"Razorpay error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Razorpay error: {str(e)}"
            )


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    if not webhook_secret:
        raise HTTPException(status_code=400, detail="Webhook secret not configured")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await handle_successful_payment(session, db, 'stripe')
        
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        await handle_subscription_update(subscription, db, 'stripe')
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        await handle_subscription_cancellation(subscription, db, 'stripe')
    
    return {"status": "success"}


@router.post("/razorpay-webhook")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Razorpay webhook events"""
    payload = await request.json()
    
    # Verify webhook signature
    webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET', '')
    signature = request.headers.get('X-Razorpay-Signature')
    
    if webhook_secret and signature:
        try:
            razorpay_client.utility.verify_webhook_signature(
                await request.body(),
                signature,
                webhook_secret
            )
        except:
            raise HTTPException(status_code=400, detail="Invalid signature")
    
    event = payload.get('event')
    
    if event == 'payment.captured':
        payment = payload['payload']['payment']['entity']
        await handle_successful_payment(payment, db, 'razorpay')
        
    elif event == 'subscription.activated':
        subscription = payload['payload']['subscription']['entity']
        await handle_subscription_update(subscription, db, 'razorpay')
        
    elif event == 'subscription.cancelled':
        subscription = payload['payload']['subscription']['entity']
        await handle_subscription_cancellation(subscription, db, 'razorpay')
    
    return {"status": "success"}


async def handle_successful_payment(payment_data: dict, db: AsyncSession, provider: str):
    """Handle successful payment and create/update subscription"""
    try:
        if provider == 'stripe':
            user_id = payment_data['metadata'].get('user_id')
            plan_id = payment_data['metadata'].get('plan_id')
            stripe_subscription_id = payment_data.get('subscription')
            stripe_customer_id = payment_data.get('customer')
        else:  # razorpay
            notes = payment_data.get('notes', {})
            user_id = notes.get('user_id')
            plan_id = notes.get('plan_id')
            stripe_subscription_id = None
            stripe_customer_id = None
        
        if not user_id or not plan_id:
            logger.error("Missing user_id or plan_id in payment metadata")
            return
        
        # Check if subscription already exists
        result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.plan_id == plan_id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
        existing_sub = result.scalar_one_or_none()
        
        if existing_sub:
            # Update existing subscription
            existing_sub.stripe_subscription_id = stripe_subscription_id
            existing_sub.stripe_customer_id = stripe_customer_id
            existing_sub.status = SubscriptionStatus.ACTIVE
            existing_sub.current_period_start = datetime.now(timezone.utc)
            existing_sub.current_period_end = datetime.now(timezone.utc) + timedelta(days=30)
        else:
            # Create new subscription
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id=user_id,
                plan_id=plan_id,
                stripe_subscription_id=stripe_subscription_id,
                stripe_customer_id=stripe_customer_id,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=datetime.now(timezone.utc),
                current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
                cancel_at_period_end=False,
                audits_used_this_month=0
            )
            db.add(subscription)
        
        await db.commit()
        logger.info(f"Subscription created/updated for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error handling successful payment: {str(e)}")
        await db.rollback()


async def handle_subscription_update(subscription_data: dict, db: AsyncSession, provider: str):
    """Handle subscription updates"""
    try:
        if provider == 'stripe':
            stripe_subscription_id = subscription_data['id']
            result = await db.execute(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == stripe_subscription_id
                )
            )
        else:  # razorpay
            razorpay_subscription_id = subscription_data['id']
            result = await db.execute(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == razorpay_subscription_id
                )
            )
        
        subscription = result.scalar_one_or_none()
        
        if subscription:
            # Update subscription details
            subscription.status = SubscriptionStatus.ACTIVE
            if provider == 'stripe':
                subscription.current_period_start = datetime.fromtimestamp(
                    subscription_data['current_period_start'], tz=timezone.utc
                )
                subscription.current_period_end = datetime.fromtimestamp(
                    subscription_data['current_period_end'], tz=timezone.utc
                )
            
            await db.commit()
            logger.info(f"Subscription updated: {subscription.id}")
            
    except Exception as e:
        logger.error(f"Error handling subscription update: {str(e)}")
        await db.rollback()


async def handle_subscription_cancellation(subscription_data: dict, db: AsyncSession, provider: str):
    """Handle subscription cancellation"""
    try:
        if provider == 'stripe':
            stripe_subscription_id = subscription_data['id']
            result = await db.execute(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == stripe_subscription_id
                )
            )
        else:  # razorpay
            razorpay_subscription_id = subscription_data['id']
            result = await db.execute(
                select(Subscription).where(
                    Subscription.stripe_subscription_id == razorpay_subscription_id
                )
            )
        
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancel_at_period_end = True
            await db.commit()
            logger.info(f"Subscription cancelled: {subscription.id}")
            
    except Exception as e:
        logger.error(f"Error handling subscription cancellation: {str(e)}")
        await db.rollback()


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's active subscription"""
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(
            Subscription.user_id == current_user.id,
            Subscription.status == SubscriptionStatus.ACTIVE
        )
        .order_by(Subscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel current subscription"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.status == SubscriptionStatus.ACTIVE
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    # Cancel in payment provider
    if subscription.stripe_subscription_id:
        if subscription.stripe_subscription_id.startswith('sub_'):
            # Stripe subscription
            try:
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
            except Exception as e:
                logger.error(f"Error cancelling Stripe subscription: {str(e)}")
        else:
            # Razorpay subscription
            try:
                if razorpay_client:
                    razorpay_client.subscription.cancel(
                        subscription.stripe_subscription_id
                    )
            except Exception as e:
                logger.error(f"Error cancelling Razorpay subscription: {str(e)}")
    
    # Update local subscription
    subscription.cancel_at_period_end = True
    await db.commit()
    
    return {"message": "Subscription will be cancelled at the end of billing period"}
