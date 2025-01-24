# TC Inventory Mobile App Development Log

## 2025-01-23: Initial Backend API Setup

### Database Models Created
1. `MobileCheckoutReason` Model
   - Purpose: Store predefined checkout reasons for mobile app
   - Fields:
     - id (Primary Key)
     - name (String, required)
     - description (Text)
     - is_active (Boolean)
     - created_at, updated_at (Timestamps)

2. `MobileDeviceToken` Model
   - Purpose: Store device tokens for push notifications
   - Fields:
     - id (Primary Key)
     - user_id (Foreign Key to users)
     - device_token (String, required)
     - device_type (String: ios/android)
     - is_active (Boolean)
     - created_at, last_used (Timestamps)

### API Endpoints Implemented
1. Authentication Endpoints
   - POST `/api/mobile/auth/login` - Login with username/PIN
   - POST `/api/mobile/auth/refresh` - Refresh JWT token
   - GET `/api/mobile/auth/verify` - Verify token validity

2. Item/System Lookup Endpoints
   - GET `/api/mobile/item/<barcode>` - Get item details
   - GET `/api/mobile/system/<barcode>` - Get system details

3. Checkout Endpoints
   - GET `/api/mobile/checkout/reasons` - List checkout reasons
   - POST `/api/mobile/checkout` - Process checkout
   - GET `/api/mobile/user/history` - Get user's checkout history

### Security Features
1. JWT Token Authentication
   - Token generation with 24-hour expiration
   - Token refresh capability
   - Token verification middleware

2. PIN-based Authentication
   - Uses existing PIN from user model
   - Required for initial login

3. CORS Configuration
   - Enabled for all mobile API endpoints
   - Origin: * (all origins allowed)

### Database Changes
1. New Tables Added:
   - mobile_checkout_reasons
   - mobile_device_tokens

2. Modified Existing Tables:
   - Added is_mobile flag to transactions table

### Dependencies Added
- PyJWT==2.8.0 (JWT token handling)
- Flask-CORS==4.0.0 (CORS support)

## Next Steps
1. Run Database Migrations
   ```bash
   flask db upgrade
   ```

2. Add Initial Checkout Reasons:
   - CLIENT INSTALL
   - REPLACEMENT
   - INTERNAL

3. Begin Flutter Mobile App Development
   - Set up Flutter project
   - Implement authentication screens
   - Add barcode scanning capability 