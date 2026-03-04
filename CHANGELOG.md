# Changelog

All notable changes to the DRB iOS app will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - 2026-03-03

### Added
- Complete Douay-Rheims Bible with all 73 books
- Haydock Commentary integration with lazy-loading
- App icon and launch screen
- GitHub Actions CI workflow for iOS builds
- Pre-push hook auto-install script
- Privacy policy and App Store compliance notes
- LICENSE and security gitignore patterns

### Changed
- Async loading, verse index, lazy commentary, shared commentary view for performance
- Haydock entries made @Published for reactive SwiftUI updates

### Fixed
- onChange updated to iOS 17 zero-parameter form in ChapterView
- parseData and parseSource marked nonisolated for pure parsing
- Domain updated from ecclesia.dev to ecclesiadev.com in PRIVACY.md
- Black screens during dialogue and floating character issues

### Accessibility
- Full accessibility audit and fixes
- Fixed hardcoded font sizes and marked decorative images hidden

### Credits
Built by Jerome, Augustine, Thomas, Luke, Giotto, Margaret, Albert, Alphonsus, Polycarp, Chrysostom. Reviewed by Bellarmine.
