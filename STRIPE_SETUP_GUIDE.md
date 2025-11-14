# 🎯 Complete Stripe Payment System Setup Guide

## Overview
A production-ready Stripe payment system has been implemented with:
- ✅ Complete checkout flow
- ✅ Webhook handling with idempotency
- ✅ Subscription management (upgrade/downgrade/cancel)
- ✅ Payment history tracking
- ✅ Refund functionality
- ✅ Fraud prevention hooks
- ✅ Admin payment dashboard
- ✅ Failed payment handling
- ✅ Dispute management

---

## 📋 Step 1: Create Stripe Products & Prices

### Go to Stripe Dashboard
1. **Test Mode:** https://dashboard.stripe.com/test/products
2. Click "**Add Product**" button

### Create 3 Products (Basic, Pro, Enterprise)

#### Product 1: Basic Plan
```
Name: Basic Plan
Description: Basic SEO audits for small websites and startups
Pricing Model: Recurring
Billing Period: Monthly
Price: $29.00
```
After saving, **COPY the Price ID** (format: `price_xxxxxxxxxxxxx`)

#### Product 2: Pro Plan
```
Name: Pro Plan  
Description: Professional SEO audits with advanced features for growing businesses
Pricing Model: Recurring
Billing Period: Monthly
Price: $99.00
```
After saving, **COPY the Price ID**

#### Product 3: Enterprise Plan
```
Name: Enterprise Plan
Description: Enterprise-grade SEO audits for large organizations
Pricing Model: Recurring
Billing Period: Monthly
Price: $299.00
```
After saving, **COPY the Price ID**

> **Note:** Free plan requires NO Stripe setup - it's handled automatically in the app

---

## 📋 Step 2: Configure Webhook Endpoint

### Create Webhook
1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click "**Add endpoint**"
3. **Endpoint URL:** `https://your-domain.com/api/payments/stripe-webhook`
   - For development: `https://stripe-payment-sync.preview.emergentagent.com/api/payments/stripe-webhook`
4. **Description:** "MJ SEO Payment Webhooks"
5. **Select events to listen to:** Click "Select events" and choose:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.trial_will_end`
   - `charge.refunded`
   - `charge.dispute.created`

6. Click "**Add endpoint**"
7. **COPY the Signing Secret** (format: `whsec_xxxxxxxxxxxxx`)

---

## 📋 Step 3: Update Environment Variables

Add the following to `/app/backend/.env`:

```bash
# Stripe Configuration (ALREADY SET)
STRIPE_SECRET_KEY="sk_test_51STFwADoGaR8tHFRfRhrM62DdDzoC8eAc2x5GJrReQlyi6Vgw4IULPn74ihpcryqjho0Gn5RUOfmEI9ycwT03ZL000RlTcoUkW"
STRIPE_PUBLISHABLE_KEY="pk_test_51STFwADoGaR8tHFRLsFDEAvjeaKa80Reh6XZ0wQUqkhxxZfq63NOPk549NpuNBdXaIMnZMEBYwkbHyirPtnjLsoV00IQm4fIiO"

# UPDATE THESE WITH YOUR VALUES:
STRIPE_WEBHOOK_SECRET="whsec_YOUR_WEBHOOK_SIGNING_SECRET_HERE"
STRIPE_PRICE_BASIC="price_YOUR_BASIC_PRICE_ID_HERE"
STRIPE_PRICE_PRO="price_YOUR_PRO_PRICE_ID_HERE"
STRIPE_PRICE_ENTERPRISE="price_YOUR_ENTERPRISE_PRICE_ID_HERE"

FRONTEND_URL="https://stripe-payment-sync.preview.emergentagent.com"
```

Add to `/app/frontend/.env` (ALREADY SET):
```bash
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_51STFwADoGaR8tHFRLsFDEAvjeaKa80Reh6XZ0wQUqkhxxZfq63NOPk549NpuNBdXaIMnZMEBYwkbHyirPtnjLsoV00IQm4fIiO
```

---

## 📋 Step 4: Update Database with Price IDs

After getting the Price IDs, run:

```bash
cd /app/backend
python init_db_tables.py
```

This will recreate the database with the correct Stripe Price IDs.

**OR manually update the plans in the database if you want to keep existing data:**

```python
# Update via Python script or SQL
UPDATE plans SET stripe_price_id = 'price_YOUR_BASIC_ID' WHERE name = 'basic';
UPDATE plans SET stripe_price_id = 'price_YOUR_PRO_ID' WHERE name = 'pro';
UPDATE plans SET stripe_price_id = 'price_YOUR_ENTERPRISE_ID' WHERE name = 'enterprise';
```

---

## 🔧 Features Implemented

### 🔹 User Features
1. **Subscription Purchase**
   - Browse plans at `/plans`
   - Secure Stripe Checkout
   - Automatic subscription activation
   - Email receipt from Stripe

2. **Subscription Management**
   - View current subscription
   - Upgrade/downgrade plans (with proration)
   - Cancel subscription (at period end or immediately)
   - Access billing portal

3. **Payment History**
   - View all past payments
   - See payment status (succeeded/failed/refunded)
   - Download invoices

4. **Billing Portal**
   - Update payment methods
   - View invoices
   - Manage subscriptions
   - Download receipts

### 🔹 Admin Features (Super Admin Only)

#### Payment Dashboard (`/admin/payments/dashboard`)
- Total revenue (all-time)
- Monthly Recurring Revenue (MRR)
- Active subscriptions count
- Failed payments tracking
- Revenue trends (6-month chart)
- Subscription distribution by plan
- Churn rate calculation

#### Transaction Management (`/admin/payments/transactions`)
- View all transactions
- Filter by status/user/date
- Search by user email
- Export transaction data

#### Subscription Management (`/admin/payments/subscriptions`)
- View all subscriptions
- Filter by status/plan
- Cancel user subscriptions
- Extend subscription periods (manual credit)

#### Refund Management
- Issue full or partial refunds
- Track refund reasons
- View refund history
- Dispute handling

#### Failed Payment Management
- View all failed payments
- See failure reasons
- User contact information
- Retry payment tracking

#### Webhook Event Log
- View all webhook events
- See processing status
- Retry failed webhooks
- Debug webhook issues

---

## 🛡️ Security Features Implemented

### 1. Webhook Security
- ✅ Signature verification (prevents replay attacks)
- ✅ Idempotency (prevents duplicate processing)
- ✅ Event logging and retry mechanism
- ✅ Concurrent processing locks

### 2. Fraud Prevention
- ✅ Stripe Radar integration (automatic fraud detection)
- ✅ Billing address collection
- ✅ Card verification (CVV required)
- ✅ 3D Secure support
- ✅ Payment method validation

### 3. Data Security
- ✅ No card details stored locally
- ✅ Tokenized payment methods
- ✅ Encrypted communication (HTTPS)
- ✅ PCI DSS compliant (Stripe handles card data)

### 4. Business Logic Security
- ✅ User authentication required
- ✅ Subscription ownership verification
- ✅ Rate limiting on payment endpoints
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ CSRF protection

---

## 📊 Database Schema

### New Tables Created:

#### 1. `payment_history`
Tracks all payment transactions:
- Payment amount, currency, status
- Payment method details (last4, brand)
- Failure reasons
- Refund information
- Stripe IDs for reference

#### 2. `webhook_events`
Logs all webhook events:
- Event type and ID
- Processing status
- Retry attempts
- Error messages
- Full payload storage

#### 3. `payment_methods`
Stores payment methods:
- Card details (last4, brand, expiry)
- Default payment method
- Billing information
- Stripe payment method ID

#### 4. Updated `users` table
- Added: `stripe_customer_id` for Stripe customer linking

---

## 🔄 Payment Flow

### User Purchase Flow:
1. User selects a plan
2. Clicks "Subscribe" → Redirected to Stripe Checkout
3. Enters payment information
4. Stripe processes payment
5. Webhook receives `checkout.session.completed`
6. System creates subscription in database
7. User redirected to success page
8. Welcome email sent (optional)

### Subscription Update Flow:
1. User upgrades/downgrades plan
2. System calculates proration
3. Updates Stripe subscription
4. Webhook receives `customer.subscription.updated`
5. Database updated with new plan
6. Proration invoice created

### Payment Failure Flow:
1. Payment fails (expired card, insufficient funds)
2. Webhook receives `invoice.payment_failed`
3. System logs failure reason
4. Subscription marked as `past_due`
5. Email sent to user (optional)
6. Stripe auto-retries payment (configurable)

---

## 🧪 Testing Guide

### Test with Stripe Test Cards:

#### Successful Payment:
```
Card Number: 4242 4242 4242 4242
Expiry: Any future date
CVV: Any 3 digits
```

#### Payment Declined:
```
Card Number: 4000 0000 0000 0002
```

#### Insufficient Funds:
```
Card Number: 4000 0000 0000 9995
```

#### 3D Secure Authentication:
```
Card Number: 4000 0025 0000 3155
```

### Testing Webhooks Locally:

1. Install Stripe CLI:
```bash
brew install stripe/stripe-cli/stripe
```

2. Login:
```bash
stripe login
```

3. Forward webhooks to local server:
```bash
stripe listen --forward-to localhost:8001/api/payments/stripe-webhook
```

4. Trigger test events:
```bash
stripe trigger checkout.session.completed
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
```

---

## 📌 API Endpoints

### User Endpoints:
```
POST   /api/payments/create-checkout-session  - Create checkout
POST   /api/payments/stripe-webhook            - Handle webhooks
GET    /api/payments/subscription              - Get subscription
POST   /api/payments/cancel-subscription       - Cancel subscription
POST   /api/payments/change-plan               - Change plan
GET    /api/payments/payment-history           - Payment history
GET    /api/payments/billing-portal            - Billing portal
```

### Admin Endpoints:
```
GET    /api/admin/payments/dashboard           - Dashboard stats
GET    /api/admin/payments/transactions        - All transactions
GET    /api/admin/payments/subscriptions       - All subscriptions
POST   /api/admin/payments/refund/{id}         - Issue refund
POST   /api/admin/payments/cancel-subscription/{id} - Cancel sub
POST   /api/admin/payments/extend-subscription/{id} - Extend sub
GET    /api/admin/payments/webhook-events      - Webhook log
POST   /api/admin/payments/retry-webhook/{id}  - Retry webhook
GET    /api/admin/payments/failed-payments     - Failed payments
GET    /api/admin/payments/revenue-report      - Revenue report
```

---

## 🚀 Next Steps

1. ✅ **Complete Stripe Setup** (Products, Prices, Webhook)
2. ✅ **Update Environment Variables** with your values
3. ✅ **Reinitialize Database** with correct Price IDs
4. ✅ **Test Payment Flow** with test cards
5. ✅ **Test Webhook Events** with Stripe CLI
6. ✅ **Configure Email Notifications** (optional)
7. ✅ **Setup Production Webhook** when deploying
8. ✅ **Switch to Live Mode** when ready for production

---

## 🆘 Troubleshooting

### Webhook not receiving events:
- Check webhook URL is publicly accessible
- Verify webhook signing secret is correct
- Check webhook endpoint logs
- Use Stripe CLI for local testing

### Payment not activating subscription:
- Check webhook events in Stripe dashboard
- Verify metadata is passed correctly
- Check backend logs for errors
- Ensure database is accessible

### Proration not working:
- Verify subscription has valid `stripe_subscription_id`
- Check plan has valid `stripe_price_id`
- Ensure subscription is in `active` status

---

## 📝 Important Notes

### Free Plan:
- NO payment/card required
- Automatically activated
- No Stripe interaction
- Users can upgrade anytime

### Production Checklist:
- [ ] Switch to live Stripe keys
- [ ] Update webhook URL to production
- [ ] Test live payments with real cards
- [ ] Configure email notifications
- [ ] Setup monitoring and alerts
- [ ] Review Stripe radar rules
- [ ] Configure tax settings (if needed)
- [ ] Setup subscription dunning (retry failed payments)
- [ ] Add terms of service and privacy policy links
- [ ] Test refund flow
- [ ] Test dispute handling

---

## 💡 Pro Tips

1. **Enable Stripe Billing Portal** - Let customers manage their own subscriptions
2. **Setup Smart Retries** - Configure Stripe to auto-retry failed payments
3. **Use Metadata** - Store user/plan IDs in Stripe for easy reconciliation
4. **Monitor Webhooks** - Setup alerts for webhook failures
5. **Test Edge Cases** - Test concurrent webhooks, network failures, etc.
6. **Keep Audit Logs** - All payment events are logged for compliance
7. **Setup Email Notifications** - Notify users of payment success/failure
8. **Enable 3D Secure** - Better fraud protection
9. **Use Stripe Radar** - Automatic fraud detection
10. **Regular Reconciliation** - Compare Stripe data with your database

---

## 📞 Support

For Stripe-specific issues:
- Stripe Documentation: https://stripe.com/docs
- Stripe Support: https://support.stripe.com

For app-specific issues:
- Check `/var/log/supervisor/backend.err.log`
- Review webhook event logs in admin panel
- Use Stripe CLI for debugging

---

**🎉 Your complete Stripe payment system is ready to go!**
