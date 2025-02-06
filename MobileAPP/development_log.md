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

## 2024-01-24
- ✓ Added Swagger/OpenAPI documentation for the mobile API
  - Implemented using Flask-RESTX
  - Added documentation for all API endpoints including:
    - Authentication routes (login, refresh, verify)
    - Item/System lookup routes
    - Checkout process routes
    - User history routes
  - Added security scheme for Bearer token authentication
  - Added API documentation link to admin navigation
  - Tested all endpoints through Swagger UI

## 2024-01-25: Mobile Development Framework Decision
- Selected Flutter as the mobile development framework after careful consideration:
  - Perfect fit for barcode scanning requirements
  - Excellent performance and native compilation
  - Strong offline capabilities for inventory management
  - Single codebase for iOS and Android
  - Rich widget library for custom UI/UX
  - Growing enterprise adoption and long-term support
  - Cost-effective for cross-platform development

### Flutter Project Setup Progress
1. ✓ Initial Setup
   - ✓ Installed Flutter SDK via Homebrew
   - ✓ Created new Flutter project: tc_inventory_mobile
   - ✓ Basic project structure generated

2. Development Environment Setup (In Progress)
   Required installations:
   - Android Studio (for Android development)
   - Xcode (for iOS development)
   - CocoaPods (for iOS dependencies)
   
3. Next Steps After Tool Installation:
   - Configure Android SDK
   - Set up iOS development certificates
   - Install Flutter plugins in Android Studio/VS Code
   - Configure project dependencies
   - Set up version control for mobile project

4. Planned Initial Dependencies:
   - http/dio: For API integration
   - flutter_barcode_scanner: For barcode scanning
   - flutter_secure_storage: For JWT token storage
   - provider/riverpod: For state management
   - sqflite/hive: For local database
   - flutter_offline: For offline capabilities

## Next Steps
1. Run Database Migrations
   ```