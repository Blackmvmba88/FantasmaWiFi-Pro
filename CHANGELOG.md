# Changelog

All notable changes to FantasmaWiFi-Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [7.6.0] - 2026-01-22 (Q1 2026 - Zero Friction Product)

### Added
- **Strategic Roadmap**: Comprehensive 2026 roadmap with quarterly objectives (ROADMAP_2026.md)
- **Technical Backlog**: Detailed technical task tracking (BACKLOG_TECHNICAL.md)
- **Marketing Backlog**: Community and marketing strategy (BACKLOG_MARKETING.md)
- **GitHub Milestones**: Issue tracking structure (GITHUB_MILESTONES.md)
- **Doctor Command**: `fantasma doctor` system diagnostics tool
  - Multi-platform support (Linux, macOS, Windows, Termux)
  - Interface detection and capability checking
  - Dependency verification
  - Known issues detection with fix suggestions
  - JSON output for automation
  - Comprehensive documentation (DOCTOR_GUIDE.md)
- **Installation Infrastructure**:
  - Complete installation guide (INSTALLATION.md)
  - Windows PowerShell installer (install_windows.ps1)
  - macOS Bash installer (install_macos.sh)
  - Termux/Android Bash installer (install_termux.sh)
- **Entry Points**: Added `fantasma-doctor` command to setup.py
- **Q1 Summary**: Implementation summary document (Q1_2026_SUMMARY.md)

### Changed
- Updated README.md with Q1 2026 features and installation instructions
- Enhanced CLI with doctor command integration
- Improved version to 7.6.0 reflecting Q1 deliverables
- Updated documentation structure with cross-references

### Fixed
- Code review issues: specific exception handling in fantasma_doctor.py
- Enum comparison: proper equality check in fantasma_cli.py
- Module references: corrected doctor module path in installer scripts
- Shebang portability: improved Termux script compatibility

### Security
- Zero vulnerabilities found in CodeQL security scan
- Proper exception handling implemented
- Type-safe enum comparisons

## [7.5.0] - 2026-01-22

### Added
- REST API for programmatic control
- API authentication and rate limiting
- Plugin system for custom adapters
- Semantic versioning infrastructure
- Comprehensive changelog
- PyPI packaging improvements

### Changed
- Reorganized package structure for better imports
- Improved setup.py with proper metadata

### Fixed
- N/A

## [7.5.0] - 2024 (Previous Release)

### Added
- Web UI Control Panel with browser-based interface
- Real-time monitoring via WebSocket
- Configuration profile management
- Multi-device access support

## [7.0.0] - 2024

### Added
- Multi-platform architecture (macOS, Linux, Windows, Termux)
- Dual operation modes (Hotspot and Bridge)
- Clean adapter-based architecture
- Unified CLI interface
- Platform-specific adapters

### Changed
- Complete rewrite from bash to Python
- Abstracted platform-specific implementations

## [1.0.0] - 2023

### Added
- Initial macOS bash scripts
- Basic hotspot functionality
- Bridge mode support
