# Environment Key Management System - Admin Guide

## Overview
The MJ SEO application now includes a secure environment key management system that allows superadmins to manage all API keys and sensitive configuration directly from the Admin Dashboard.

## Features

### 🔐 Security
- **Encryption**: All keys are encrypted using Fernet (AES) with PBKDF2HMAC-SHA256
- **Access Control**: Only superadmin users can access and manage environment keys
- **Audit Trail**: Tracks who last updated each key
- **Hidden Values**: Key values are masked by default (••••••••••••)
- **Secure Viewing**: Values only decrypted when explicitly requested

### 🎯 Key Categories
- **Payment**: Stripe, Razorpay API keys
- **AI**: Groq, Exa.ai, OpenAI API keys
- **Email**: Email service API keys
- **Database**: Database connection strings
- **Other**: General configuration keys

## How to Use

### Accessing Environment Keys
1. Log in as superadmin (superadmin@test.com)
2. Navigate to Admin Dashboard
3. Click on "Environment Keys" tab

### Initialize Default Keys
**Important**: Before adding your Stripe Price IDs, initialize the keys from the current .env file:

1. Click "Initialize from .env" button
2. System will import all existing keys from backend/.env
3. Only non-placeholder values will be imported
4. Keys are automatically encrypted during import

### Add New Environment Key
1. Click "Add New Key" button
2. Fill in the form:
   - **Key Name**: Use UPPERCASE with underscores (e.g., `STRIPE_SECRET_KEY`)
   - **Key Value**: Enter the actual secret key value
   - **Category**: Select appropriate category
   - **Description**: Explain what this key is used for
3. Click "Create Key"
4. Key will be encrypted and stored
5. Runtime environment will be updated immediately

### Edit Existing Key
1. Click the edit icon (pencil) next to any key
2. Modify the fields (key name cannot be changed)
3. To update value, enter new value (leave empty to keep existing)
4. Click "Update Key"

### View/Hide Key Values
1. Click the eye icon to reveal encrypted value
2. System fetches and decrypts the value
3. Click eye-off icon to hide again
4. Use copy icon to copy value to clipboard

### Delete Environment Key
1. Click the trash icon next to any key
2. Confirm deletion
3. Key will be removed from database and runtime environment

## Managing Stripe Price IDs

### Via Environment Keys Tab
1. Go to Environment Keys tab
2. Find `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
3. Click edit icon for each
4. Update with your actual Stripe keys
5. Save changes

### Via Plans Tab
1. Go to Plans tab
2. Each plan card shows current Stripe Price ID
3. Click edit icon (top-right of plan card)
4. Update the "Stripe Price ID" field with your actual price ID from Stripe Dashboard
5. Save changes

### Getting Stripe Price IDs
1. Go to https://dashboard.stripe.com
2. Navigate to **Products** section
3. Click on your product
4. Under **Pricing**, you'll see the Price ID (e.g., `price_1234567890abcdef`)
5. Copy each Price ID for:
   - Basic Plan ($29/month)
   - Pro Plan ($99/month)
   - Enterprise Plan ($299/month)
6. Update in Plans tab

## Default Environment Keys

The system can import these keys from your .env file:

| Key Name | Category | Description |
|----------|----------|-------------|
| STRIPE_SECRET_KEY | payment | Stripe API secret key for payment processing |
| STRIPE_PUBLISHABLE_KEY | payment | Stripe publishable key (client-side) |
| STRIPE_WEBHOOK_SECRET | payment | Stripe webhook signing secret |
| RAZORPAY_KEY_ID | payment | Razorpay key ID for payment processing |
| RAZORPAY_KEY_SECRET | payment | Razorpay secret key |
| GROQ_API_KEY | ai | Groq API key for LLM (Llama 3.3 70B) |
| EXA_API_KEY | ai | Exa.ai API key for research tasks |
| SECRET_KEY | other | Application secret key for JWT and encryption |

## API Endpoints

### List All Keys (Values Hidden)
```
GET /api/admin/env-keys
Authorization: Bearer {superadmin_token}
```

### Get Specific Key (With Value)
```
GET /api/admin/env-keys/{key_id}
Authorization: Bearer {superadmin_token}
```

### Create New Key
```
POST /api/admin/env-keys
Authorization: Bearer {superadmin_token}
Content-Type: application/json

{
  "key_name": "NEW_API_KEY",
  "key_value": "secret_value_here",
  "description": "Description of what this key does",
  "category": "payment"
}
```

### Update Key
```
PUT /api/admin/env-keys/{key_id}
Authorization: Bearer {superadmin_token}
Content-Type: application/json

{
  "key_value": "new_secret_value",
  "description": "Updated description",
  "is_active": true
}
```

### Delete Key
```
DELETE /api/admin/env-keys/{key_id}
Authorization: Bearer {superadmin_token}
```

### Initialize from .env
```
POST /api/admin/env-keys/initialize-defaults
Authorization: Bearer {superadmin_token}
```

## Best Practices

### Security
1. ✅ Never share your superadmin credentials
2. ✅ Always use production API keys in production environment
3. ✅ Regularly rotate API keys
4. ✅ Use webhook secrets for payment integrations
5. ✅ Keep your SECRET_KEY secure and unique

### Key Management
1. ✅ Add descriptions to all keys for documentation
2. ✅ Use consistent naming conventions (UPPERCASE_WITH_UNDERSCORES)
3. ✅ Set appropriate categories for easy filtering
4. ✅ Test keys in test mode before using in production
5. ✅ Disable inactive keys rather than deleting them

### Stripe Integration
1. ✅ Use test keys during development (sk_test_...)
2. ✅ Switch to live keys in production (sk_live_...)
3. ✅ Create a webhook endpoint in Stripe Dashboard
4. ✅ Configure webhook to point to your backend URL
5. ✅ Update STRIPE_WEBHOOK_SECRET with actual signing secret

## Troubleshooting

### Keys Not Working After Update
- Restart backend service: `sudo supervisorctl restart backend`
- Check backend logs: `tail -f /var/log/supervisor/backend.*.log`
- Verify key value is correct (view in UI)

### Cannot See Environment Keys Tab
- Ensure you're logged in as superadmin
- Only superadmin@test.com can access this feature
- Regular users will not see this tab

### Stripe Payments Not Working
1. Verify all 3 Stripe keys are set correctly
2. Check Price IDs match your Stripe Dashboard
3. Ensure webhook secret is configured
4. Test with Stripe test cards first

### Backend Error After Adding Key
- Check backend logs for specific error
- Ensure key name doesn't contain spaces
- Verify encryption service is working
- Restart backend if needed

## Production Deployment Checklist

Before deploying to production:

- [ ] Initialize all environment keys from .env
- [ ] Update all test API keys to production keys
- [ ] Configure Stripe Price IDs for each plan
- [ ] Set up Stripe webhook endpoint
- [ ] Update webhook secret
- [ ] Test payment flow end-to-end
- [ ] Verify all admin panel features work
- [ ] Change default SECRET_KEY
- [ ] Change default superadmin password
- [ ] Test audit creation and report generation

## Support

For issues or questions:
- Check backend logs: `/var/log/supervisor/backend.*.log`
- Check frontend logs: `/var/log/supervisor/frontend.*.log`
- Review Stripe Dashboard for payment issues
- Contact system administrator

## Version History

### v1.0.0 (Current)
- Initial environment key management system
- Fernet encryption implementation
- Superadmin UI for key management
- Stripe Price ID management in Plans tab
- Secure API endpoints
- Audit trail for key updates
