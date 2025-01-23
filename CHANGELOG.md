# TC Inventory System Changelog

All notable changes to this project will be documented in this file.

## [1.0.75] - 2025-01-23

### Added
- Added Microsoft Surface to computer types
- Enhanced CPU management with improved form validation
- Added CSRF token protection to CPU deletion
- Improved error handling and debug logging for CPU operations
- Added timezone configuration with CST as default
- Added proper timestamp handling in system logs

### Changed
- Updated CPU form to use proper form field rendering
- Enhanced error feedback for CPU operations
- Improved DataTables integration for CPU list
- Updated logging system to use configured timezone
- Standardized timestamp format across all logs

### Fixed
- Fixed CSRF token missing error in CPU deletion
- Fixed CPU form validation issues
- Fixed tag handling in computer systems
- Fixed timezone inconsistency in log timestamps

## [1.0.72] - 2025-01-15

### Added
- Implemented DataTables for Computer Models list
  - Added client-side sorting and pagination
  - Enhanced search functionality
  - Improved responsive design
  - Added custom labels for better user experience

### Changed
- Removed server-side pagination from Computer Models list in favor of DataTables
- Updated Computer Models route to return all models for DataTables processing

## [1.0.70] - 2025-01-10

### Added
- Implemented eager loading for system tags to improve performance
- Added debug logging for system tag operations
- Enhanced error handling for database operations

### Fixed
- Fixed system tags not being saved properly
- Fixed lazy loading issues with system tags
- Resolved database transaction issues

## [1.0.60] - 2025-01-05

### Added
- Enhanced DataTables implementation for Computer Systems
- Added sorting and filtering capabilities to Systems table
- Improved table responsiveness and styling

### Changed
- Updated table pagination to use DataTables
- Enhanced search functionality for Systems
- Improved mobile view for tables

### Fixed
- Fixed table width and alignment issues
- Resolved sorting issues in DataTables
- Fixed responsive design bugs

## [1.0.50] - 2024-12-28

### Added
- Implemented Roadmap feature with drag-and-drop functionality
- Added voting system for roadmap items
- Created new database tables for roadmap items and votes
- Added category badges with icons (Feature Request, Bug Report, Integration)
- Implemented admin controls for roadmap item status management

### Changed
- Enhanced dark mode styling for status indicators
- Improved badge styling with category-specific icons

## [1.0.49] - 2024-12-20

### Added
- Implemented DataTables for Items and Systems lists
- Added responsive layout for both tables
- Added custom search and filter functionality for DataTables
- Added proper table width styling for Systems table

### Changed
- Updated table pagination to use DataTables instead of Flask-SQLAlchemy pagination
- Improved table sorting functionality
- Enhanced search capabilities with DataTables integration

### Fixed
- Fixed Systems table width issue
- Fixed table responsiveness on mobile devices

## [1.0.48] - 2024-12-15

- Initial version tracking in changelog
- Base inventory management system functionality
- User authentication and authorization
- Item and Computer Systems management
- Wiki system integration
- Category management
- Tag system for items
- Search and filter functionality
- Responsive dashboard design 