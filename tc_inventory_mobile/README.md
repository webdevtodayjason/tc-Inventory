# TC Inventory Mobile App

A Flutter-based mobile companion app for the TC Inventory System.

[![Flutter Version](https://img.shields.io/badge/flutter-3.16.0-blue.svg)](https://flutter.dev/)
[![Dart Version](https://img.shields.io/badge/dart-3.2.0-blue.svg)](https://dart.dev/)

## Features

- Barcode scanning with Code128 support for TC Inventory labels
- Quick item search and lookup
- Item details view
- Quick checkout functionality
- Dark mode support
- Camera zoom controls
- Flash/torch control for low light scanning

## Requirements

- Flutter 3.16.0 or higher
- iOS 12.0 or higher
- Xcode 14.0 or higher (for iOS builds)
- macOS (for iOS development)
- Android Studio (for Android development)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd tc_inventory_mobile
```

2. Install dependencies:
```bash
flutter pub get
```

3. Configure iOS permissions in `ios/Runner/Info.plist`:
```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to scan inventory item barcodes.</string>
```

4. Build and run:
```bash
# For iOS
flutter build ios
flutter run

# For Android
flutter build apk
flutter run
```

## Barcode Scanner Configuration

The app is configured to optimally scan TC Inventory barcodes:

### Scanner Settings
- Format: Code128 (optimized for TC Inventory barcodes)
- Initial zoom: 2.0x
- Scan window height: 150 pixels
- Detection speed: Normal
- Auto-focus enabled

### Scanning Tips
- Hold device 3-4 inches from barcode
- Keep phone parallel to label
- Ensure good lighting or use flash
- Center barcode in scan window

### Barcode Format
The scanner is optimized for TC Inventory's Code128 barcodes that follow the format:
- Pattern: `TC-XXXXXXXX` where X is alphanumeric
- Example: `TC-B95F49A3`

## Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  mobile_scanner: ^6.0.0
  http: ^1.2.0
  flutter_secure_storage: ^9.0.0
  permission_handler: ^11.3.1
  share_plus: ^10.1.4
```

## Configuration

Update `lib/config.dart` with your server settings:

```dart
class ApiConfig {
  static const String baseUrl = 'http://your-server:5001';
  static String itemEndpoint(String id) => '$baseUrl/api/items/$id';
  // ... other endpoints
}
```

## Build and Deploy

### iOS
1. Open `ios/Runner.xcworkspace` in Xcode
2. Configure signing
3. Build and archive

### Android
1. Configure `android/app/build.gradle`
2. Create keystore for release
3. Build APK/Bundle:
```bash
flutter build apk --release
# or
flutter build appbundle
```

## Troubleshooting

### Common Issues

1. Camera Permission
   - Ensure camera permission is granted
   - Check Info.plist configuration

2. Barcode Scanning
   - Verify proper distance (3-4 inches)
   - Check lighting conditions
   - Ensure barcode is Code128 format

3. Build Issues
   - Run `flutter clean`
   - Delete build folders
   - Re-run `flutter pub get`

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
