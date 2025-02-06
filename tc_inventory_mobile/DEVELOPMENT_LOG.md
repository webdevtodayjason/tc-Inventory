# TC Inventory Mobile Development Log

## API Endpoints

### Authentication
- `POST /api/mobile/auth/login`
  - Authenticates user with username and PIN
  - Returns JWT token and user info
  - Token validity: 7 days
- `POST /api/mobile/auth/refresh`
  - Refreshes JWT token
  - Requires valid existing token
- `GET /api/mobile/auth/verify`
  - Verifies token validity
  - Returns user info if valid

### Search
- `GET /api/mobile/search/items/search`
  - Query params: `q` (search term), `page`, `limit`
  - Searches items by name, tracking ID, manufacturer, or MPN
  - Returns paginated results with tags, transactions, and category info
- `GET /api/mobile/search/systems/search`
  - Query params: `q` (search term), `page`, `limit`
  - Searches systems by tracking ID or model info
  - Returns paginated results with model and tag info

### Checkout Operations
- `GET /api/mobile/checkout/search/:barcode`
  - Searches for items/systems available for checkout
  - Returns 404 if item not found or not available
  - Checks quantity > 0 for items
  - Checks status == 'available' for systems
- `GET /api/mobile/checkout/reasons`
  - Retrieves list of valid checkout reasons
  - Returns reason ID, name, and description
- `POST /api/mobile/checkout`
  - Processes checkout transaction
  - Required fields: type (item/system), id, reason_id
  - Optional fields: quantity (for items), notes
  - Updates inventory quantities
  - Records transaction history
- `GET /api/mobile/checkout/history`
  - Retrieves user's checkout history
  - Shows both item and system checkouts
  - Sorted by date (most recent first)

### Item/System Details
- `GET /api/mobile/items/:id`
  - Retrieves detailed item information
  - Includes tags, transactions, category info
- `GET /api/mobile/systems/:id`
  - Retrieves detailed system information
  - Includes model, CPU, and tag info

## Features Implemented

### Authentication
- [x] Login with username/PIN
- [x] JWT token management
- [x] Token refresh mechanism
- [x] Secure token storage
- [x] Auto-logout on token expiration
- [x] Development/Production server toggle

### Search Functionality
- [x] Real-time search with debouncing
- [x] Infinite scroll pagination
- [x] Dual search modes (Items/Systems)
- [x] Rich search results display
- [x] Tag visualization
- [x] Status indicators
- [x] Loading states

### Item Details
- [x] Comprehensive item information display
- [x] Organized sections:
  - Basic Information
  - Product Information
  - Financial Information
  - System Information
  - Recent Checkouts
  - Purchase Links
- [x] Image display with error handling
- [x] Tag display with color support
- [x] Status color coding

### Barcode Scanning
- [x] Camera integration
- [x] Code128 format support
- [x] Barcode mapping storage
- [x] TC code format validation
- [x] Camera permission handling
- [x] Scan overlay UI
- [x] Torch/flash control
- [x] Zoom controls

### UI/UX Features
- [x] Dark mode support
- [x] Responsive layouts
- [x] Loading indicators
- [x] Error handling
- [x] User feedback
- [x] Portrait mode lock
- [x] iOS-style dialogs
- [x] Material Design 3 theming

## Theme Configuration

### Light Theme
```dart
colorScheme: ColorScheme.light(
  primary: Colors.blue,
  secondary: Colors.blueAccent,
  surface: Colors.white,
  background: Colors.grey[50]!,
)
```

### Dark Theme
```dart
colorScheme: ColorScheme.dark(
  primary: Colors.blue,
  secondary: Colors.lightBlue,
  surface: Color(0xFF303030),
  background: Color(0xFF121212),
)
```

## Dependencies
- `flutter_secure_storage: ^9.0.0` - Secure token storage
- `http: ^1.2.0` - API communication
- `mobile_scanner: ^6.0.0` - Barcode scanning
- `permission_handler: ^11.3.1` - Camera permissions
- `share_plus: ^10.1.4` - Sharing functionality

## Development Environment
- Flutter Version: 3.16.0
- Dart Version: 3.2.0
- Minimum iOS Version: 16.0
- Target Android SDK: 33

## Known Issues & Solutions
1. Dark Mode Visibility
   - Fixed tag contrast with white text and borders
   - Improved button visibility with elevated styling
   - Added card elevation for better depth

2. Camera Permissions
   - Implemented proper permission request flow
   - Added clear user messaging
   - Handled permanent denial case

3. Image Loading
   - Added error handling
   - Implemented placeholder
   - Added loading indicator

## Future Improvements
1. Offline Support
   - [ ] Local data caching
   - [ ] Offline barcode scanning
   - [ ] Background sync

2. Enhanced Search
   - [ ] Advanced filters
   - [ ] Sort options
   - [ ] Search history

3. User Experience
   - [ ] Batch checkout
   - [ ] Quick actions
   - [ ] Push notifications

## Security Considerations
1. Token Storage
   - Using secure storage for sensitive data
   - Token expiration handling
   - Automatic logout on security issues

2. API Communication
   - HTTPS enforcement
   - Token-based authentication
   - Request signing

3. Data Protection
   - No sensitive data in logs
   - Secure error handling
   - Input validation

## Testing Guidelines
1. Authentication
   - Test token expiration
   - Test invalid credentials
   - Test server switching

2. Search
   - Test pagination
   - Test empty results
   - Test special characters

3. Barcode Scanning
   - Test various lighting conditions
   - Test different barcode formats
   - Test permission scenarios

## Build & Deployment
1. iOS
   - Minimum iOS 16.0
   - Static framework linking
   - Camera usage description

2. Android
   - Target SDK 33
   - Camera permission in manifest
   - Network security config

## Server Configuration
### Development
- Host: 192.168.0.181
- Port: 5001
- Scheme: http

### Production
- Host: inventory.ticom.pro
- Port: 443
- Scheme: https

## Image Assets Configuration

### App Icons
Location: `ios/Runner/Assets.xcassets/AppIcon.appiconset/`
- **App Store Icon**: Icon-App-1024x1024@1x.png (1024x1024)
- **iPhone Icons**:
  - Icon-App-60x60@2x.png (120x120)
  - Icon-App-60x60@3x.png (180x180)
- **iPad Icons**:
  - Icon-App-76x76@2x.png (152x152)
  - Icon-App-83.5x83.5@2x.png (167x167)
- **Supporting Icons**:
  - Various sizes for settings, notifications, and spotlight

### Launch Images (iOS Native)
Location: `ios/Runner/Assets.xcassets/LaunchImage.imageset/`
- LaunchImage.png (Base resolution)
- LaunchImage@2x.png (2x resolution)
- LaunchImage@3x.png (3x resolution)
- Purpose: Shown immediately when app is launched, before Flutter engine starts

### Logo Images
Location: `assets/images/`
- logo.png (Base resolution - 260KB)
- logo@2x.png (2x resolution - 820KB)
- logo@3x.png (3x resolution - 1.5MB)
- Purpose: Used within the app for branding

### Splash Screens (Flutter)
Location: `assets/splash/`
- splash_screen.png (iPhone - 2.2MB)
- splash_screen_dark.png (iPhone Dark Mode - 2.2MB)
- splash_screen_tablet.png (iPad - 2.2MB)
- splash_screen_tablet_dark.png (iPad Dark Mode - 2.2MB)
- Purpose: Shown after Flutter engine starts, during app initialization

### Web Icons
Location: `web/icons/`
- Icon-192.png (192x192)
- Icon-512.png (512x512)
- Icon-maskable-192.png (192x192)
- Icon-maskable-512.png (512x512)
- favicon.png
- Purpose: Progressive Web App (PWA) support

### Android Icons
Location: `android/app/src/main/res/mipmap-*/`
- mipmap-mdpi/ic_launcher.png
- mipmap-hdpi/ic_launcher.png
- mipmap-xhdpi/ic_launcher.png
- mipmap-xxhdpi/ic_launcher.png
- mipmap-xxxhdpi/ic_launcher.png
- Purpose: Android platform app icons

### MacOS Icons
Location: `macos/Runner/Assets.xcassets/AppIcon.appiconset/`
- app_icon_16.png
- app_icon_32.png
- app_icon_64.png
- app_icon_128.png
- app_icon_256.png
- app_icon_512.png
- app_icon_1024.png
- Purpose: MacOS platform app icons

### Asset Configuration
File: `pubspec.yaml`
```yaml
flutter:
  assets:
    - assets/images/logo.png
    - assets/splash/splash_screen.png
    - assets/splash/splash_screen_dark.png
    - assets/splash/splash_screen_tablet.png
    - assets/splash/splash_screen_tablet_dark.png
```

### Image Loading Sequence
1. App Icon: Shown in device home screen
2. Launch Image: Shown immediately when app is tapped (iOS native)
3. Splash Screen: Shown while Flutter engine initializes
4. Logo: Shown within app UI after initialization

### Best Practices
- Keep image sizes optimized for their purpose
- Provide dark mode variants where needed
- Ensure consistent branding across all assets
- Follow platform-specific guidelines for icons
- Use appropriate resolutions for different device sizes 

## Beta Testing & Release Preparation

### Version Information
```yaml
version: 1.0.0+1  # Format: <major>.<minor>.<patch>+<build_number>
```

### iOS TestFlight Setup
1. **Xcode Configuration**
   - Bundle ID: `pro.ticom.tcinventory`
   - Version: 1.0.0
   - Build: 1
   - Minimum iOS: 16.0
   - Devices: iPhone, iPad
   - Orientation: Portrait only

2. **Required Screenshots**
   - 6.5" iPhone (1284 x 2778)
   - 5.5" iPhone (1242 x 2208)
   - 12.9" iPad Pro (2048 x 2732)
   - Dark mode variants for each

3. **Build Commands**
```bash
# Clean build
cd ios
rm -rf Pods Podfile.lock
pod deintegrate
pod cache clean --all
cd ..
flutter clean

# Get dependencies
flutter pub get
cd ios
pod install
cd ..

# Create release build
flutter build ios --release

# Archive and upload to TestFlight
# Open Xcode
open ios/Runner.xcworkspace
# Then use Xcode to archive and upload
```

### Android Beta Setup
1. **Build Configuration**
   ```gradle
   android {
       compileSdkVersion 33
       defaultConfig {
           applicationId "pro.ticom.tcinventory"
           minSdkVersion 24
           targetSdkVersion 33
           versionCode 1
           versionName "1.0.0"
       }
   }
   ```

2. **Required Screenshots**
   - Phone: 1080 x 1920 (portrait)
   - 7-inch tablet: 1200 x 1920
   - 10-inch tablet: 1920 x 1200
   - Dark mode variants for each

3. **Build Commands**
```bash
# Clean build
flutter clean
flutter pub get

# Create app bundle
flutter build appbundle --release

# Location of bundle:
# build/app/outputs/bundle/release/app-release.aab
```

### Pre-release Checklist
1. **Code Signing**
   - [x] iOS Distribution Certificate
   - [x] iOS Provisioning Profile
   - [x] Android Keystore
   - [x] Key properties file

2. **App Store Assets**
   - [x] App icons (all sizes)
   - [x] Screenshots
   - [x] App description
   - [x] Privacy policy URL
   - [x] Support URL

3. **Testing Requirements**
   - [x] TestFlight beta testers group created
   - [x] Play Store closed testing track configured
   - [x] Internal testing group set up
   - [x] Test accounts prepared

4. **Documentation**
   - [x] Beta testing instructions
   - [x] Known issues list
   - [x] Feedback collection form
   - [x] Support contact information

### Beta Testing Process
1. **Distribution**
   - iOS: TestFlight invites via email
   - Android: Play Store opt-in URL

2. **Feedback Collection**
   - In-app feedback form
   - TestFlight feedback
   - Play Store reviews
   - Bug report template

3. **Monitoring**
   - Crash reports
   - Analytics
   - User engagement
   - Performance metrics

4. **Update Cycle**
   - Weekly builds
   - Hotfixes as needed
   - Change log maintenance
   - Version control

### Release Notes (v1.0.0-beta.1)
```markdown
First beta release of TC Inventory Mobile

New Features:
- Complete inventory management system
- Barcode scanning with Code128 support
- Real-time search functionality
- Dark mode support
- Offline capability

Known Issues:
- Camera may require restart on first use
- Search might be slow with large datasets
- Dark mode switching has slight delay

Testing Focus Areas:
1. Barcode scanning in various lighting
2. Search performance with filters
3. Checkout process workflow
4. Network handling
5. Permission management
```

### Beta Tester Instructions
1. **Installation**
   - iOS: Accept TestFlight invite and install
   - Android: Join beta program and update

2. **Initial Setup**
   - Login with provided test credentials
   - Grant required permissions
   - Configure preferences

3. **Test Scenarios**
   - Inventory search
   - Barcode scanning
   - Item checkout
   - System management
   - Dark mode switching

4. **Reporting Issues**
   - Use provided bug report template
   - Include screenshots/recordings
   - Specify device and OS version
   - Describe reproduction steps 