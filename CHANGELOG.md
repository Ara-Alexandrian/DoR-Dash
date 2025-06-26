# Changelog

All notable changes to the DoR-Dash project will be documented in this file.

## [Unreleased] - 2025-01-26

### Added
- **About Page**: Comprehensive system architecture documentation with interactive Mermaid diagrams
- **Brain-Lightbulb Easter Egg**: Intuitive navigation icon next to DoR-Dash title for About page discovery
- **MCP Puppeteer Integration**: Visual testing and UI validation capabilities for automated accessibility testing
- **Enhanced Theme Support**: Improved color contrast compliance across all themes (dracula, MBP, LSU)
- **Database Avatar Storage**: Avatar images now stored in PostgreSQL with Redis caching for better performance

### Changed
- **Navigation Cleanup**: Removed "About" from main navigation menu in favor of easter egg discovery
- **Dashboard Reorganization**: Moved presentation assignments to top of dashboard, moved roadmap to About page
- **Color Contrast**: Upgraded text colors to meet WCAG AAA accessibility standards (10.3+ contrast ratio)
- **Card Backgrounds**: Dark themes now use appropriate dark backgrounds instead of bright colored ones

### Fixed
- **Avatar Upload Issues**: Resolved positioning and soft edge preservation during avatar cropping
- **Cache Invalidation**: Fixed avatar cache clearing after upload
- **Text Readability**: Resolved font contrast issues across all dark theme variants
- **Mermaid Diagrams**: Fixed Svelte parsing conflicts with curly brace syntax in decision nodes

### Technical Improvements
- Added MCP Puppeteer server for visual testing
- Enhanced MCP server configuration with 9 total servers
- Improved theme class management and CSS specificity
- Database migration for avatar storage fields

## Previous Versions

See git history for detailed changes in previous versions.