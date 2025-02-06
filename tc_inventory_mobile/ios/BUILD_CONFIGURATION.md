# iOS Build Configuration Guide

## Environment Requirements
- Flutter Version: 3.27.3
- Xcode Version: 16.2
- CocoaPods Version: 1.16.2
- Minimum iOS Version: 16.0
- Target Device: iPhone with iOS 16.0 or higher

## Critical Files Configuration

### 1. Podfile Configuration
Location: `ios/Podfile`
```ruby
platform :ios, '16.0'

# Key Requirements:
# - Use static frameworks to avoid dynamic framework issues
# - Set minimum iOS version to 16.0
# - Enable modular headers

target 'Runner' do
  use_frameworks! :linkage => :static  # Critical for Flutter
  use_modular_headers!
  flutter_install_all_ios_pods File.dirname(File.realpath(__FILE__))
end

post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
    target.build_configurations.each do |config|
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '16.0'
      config.build_settings['ENABLE_BITCODE'] = 'NO'
      config.build_settings['SWIFT_VERSION'] = '5.0'
      config.build_settings['BUILD_LIBRARY_FOR_DISTRIBUTION'] = 'YES'
      config.build_settings['DEAD_CODE_STRIPPING'] = 'YES'
    end
  end
end
```

### 2. XCConfig Files
Location: `ios/Flutter/Debug.xcconfig` and `ios/Flutter/Release.xcconfig`

Debug.xcconfig:
```xcconfig
#include? "Generated.xcconfig"
#include? "Pods/Target Support Files/Pods-Runner/Pods-Runner.debug.xcconfig"
```

Release.xcconfig:
```xcconfig
#include? "Pods/Target Support Files/Pods-Runner/Pods-Runner.release.xcconfig"
#include? "Pods/Target Support Files/Pods-Runner/Pods-Runner.profile.xcconfig"
#include? "Generated.xcconfig"
```

### 3. AppFrameworkInfo.plist
Location: `ios/Flutter/AppFrameworkInfo.plist`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>MinimumOSVersion</key>
  <string>16.0</string>
  <!-- Other standard keys remain unchanged -->
</dict>
</plist>
```

## Build Process

1. Clean Build Command Sequence:
```bash
cd ~/code/tcinvintory/tc_inventory_mobile
rm -rf ios/Pods ios/Podfile.lock ios/.symlinks ios/Flutter/Flutter.framework ios/Flutter/App.framework ios/Flutter/flutter_export_environment.sh build
flutter clean
flutter pub get
cd ios
pod deintegrate
pod cache clean --all
pod install
cd ..
flutter build ios
```

## Common Issues and Solutions

1. **Framework Not Found Error**
   - Solution: Ensure static framework linking is enabled in Podfile
   - Check: `use_frameworks! :linkage => :static`

2. **CocoaPods Base Configuration Warning**
   - Solution: Proper ordering of includes in xcconfig files
   - Ensure Generated.xcconfig is included
   - Include appropriate Pods-Runner xcconfig files

3. **Missing AppFrameworkInfo.plist**
   - Solution: Ensure file exists with correct iOS version
   - Must be created if missing after clean

## Maintenance Notes

1. **When Updating Flutter:**
   - Re-run complete clean build sequence
   - Check for any changes in minimum iOS version requirements
   - Update AppFrameworkInfo.plist if needed

2. **When Adding New Dependencies:**
   - Update Podfile if new dependencies require specific configurations
   - Run `pod install` after adding new Flutter packages
   - Check for any conflicts with existing static framework requirements

3. **Version Control:**
   - Keep these files in version control:
     - Podfile
     - Debug.xcconfig
     - Release.xcconfig
     - AppFrameworkInfo.plist
   - Do NOT commit:
     - Pods directory
     - Podfile.lock
     - Flutter/Flutter.framework
     - Flutter/App.framework
     - Flutter/flutter_export_environment.sh

## Testing

Always test builds on both:
1. Simulator
2. Physical device (iPhone with iOS 16.0 or higher)

## Support

For issues, refer to:
- [Flutter iOS Documentation](https://flutter.dev/docs/development/ios)
- [CocoaPods Documentation](https://guides.cocoapods.org) 