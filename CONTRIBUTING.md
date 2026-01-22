# Contributing to FantasmaWiFi-Pro

Thank you for your interest in contributing to FantasmaWiFi-Pro! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

This project operates under the principle of **Digital Sovereignty** - creating tools that empower users to control their own digital infrastructure. We expect all contributors to:

- Be respectful and inclusive
- Focus on constructive feedback
- Prioritize user empowerment and privacy
- Write clear, maintainable code

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Git
- Basic understanding of networking concepts
- Familiarity with your target platform (macOS/Linux/Windows/Termux)

### Development Setup

1. **Fork the repository**
   ```bash
   # Go to https://github.com/Blackmvmba88/FantasmaWiFi-Pro
   # Click "Fork" button
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/FantasmaWiFi-Pro.git
   cd FantasmaWiFi-Pro
   ```

3. **Set up remote**
   ```bash
   git remote add upstream https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

#### 1. Bug Reports 🐛

Found a bug? Please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Platform and version info
- Relevant logs/screenshots

#### 2. Feature Requests 💡

Have an idea? Open an issue with:
- Clear description of the feature
- Use cases and benefits
- Proposed implementation (if you have ideas)

#### 3. Code Contributions 💻

##### Adding a New Platform Adapter

If you want to add support for a new platform:

```python
# adapters/my_platform_adapter.py
from fantasma_core import PlatformAdapter, NetworkInterface

class MyPlatformAdapter(PlatformAdapter):
    """Adapter for MyPlatform"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "MyPlatform"
    
    # Implement required methods:
    # - detect_interfaces()
    # - start_hotspot()
    # - start_bridge()
    # - stop_sharing()
    # - get_status()
```

See [TUTORIALS.md](TUTORIALS.md#custom-platform-adapter) for detailed guide.

##### Improving Existing Adapters

- Fix bugs in platform-specific code
- Add better error handling
- Improve performance
- Add new features

##### Web UI Improvements

- Enhance existing pages
- Add new visualizations
- Improve responsiveness
- Add accessibility features

##### API Enhancements

- Add new endpoints
- Improve documentation
- Add example integrations

#### 4. Documentation 📚

- Fix typos and unclear explanations
- Add tutorials and guides
- Translate documentation
- Create video tutorials

#### 5. Testing 🧪

- Write unit tests
- Test on different platforms
- Report compatibility issues
- Improve test coverage

## Coding Standards

### Python Style

We follow PEP 8 with some flexibility:

```python
# Good
def start_sharing(config: FantasmaConfig) -> bool:
    """
    Start network sharing with given configuration.
    
    Args:
        config: Configuration object with source/target interfaces
        
    Returns:
        True if started successfully, False otherwise
    """
    try:
        # Implementation
        return True
    except Exception as e:
        self.logger.error(f"Failed to start: {e}")
        return False

# Bad
def start(c):  # No type hints, unclear name
    return True  # No error handling
```

### Code Organization

- **Core logic** → `fantasma_core.py`
- **Platform adapters** → `adapters/`
- **CLI interface** → `fantasma_cli.py`
- **Web interface** → `fantasma_web.py`
- **API utilities** → `fantasma_api.py`
- **Plugins** → `fantasma_plugins.py`

### Logging

Use consistent logging:

```python
import logging

logger = logging.getLogger(__name__)

# Info for normal operations
logger.info("Starting hotspot on wlan0")

# Warning for recoverable issues
logger.warning("Interface already configured, skipping")

# Error for failures
logger.error(f"Failed to start hostapd: {error}")

# Debug for detailed info (use --verbose flag)
logger.debug(f"Running command: {cmd}")
```

### Error Handling

Always handle errors gracefully:

```python
# Good
try:
    result = subprocess.run(cmd, check=True, capture_output=True)
except subprocess.CalledProcessError as e:
    logger.error(f"Command failed: {e.stderr.decode()}")
    return False

# Bad
result = subprocess.run(cmd)  # No error handling
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_adapters.py

# Run with coverage
python -m pytest --cov=.
```

### Writing Tests

Create test files in `tests/` directory:

```python
# tests/test_my_feature.py
import pytest
from fantasma_core import FantasmaConfig, NetworkMode

def test_config_validation():
    """Test configuration validation"""
    config = FantasmaConfig(
        source_interface="en0",
        target_interface="en1",
        mode=NetworkMode.HOTSPOT
    )
    assert config.validate()

def test_invalid_config():
    """Test that invalid config raises error"""
    with pytest.raises(ValueError):
        config = FantasmaConfig(
            source_interface="",  # Invalid
            target_interface="en1",
            mode=NetworkMode.HOTSPOT
        )
```

### Platform Testing

Since adapters are platform-specific, test on your target platform:

```bash
# macOS
./fantasma_cli.py list
sudo ./fantasma_cli.py start -s en0 -t en1 --ssid Test --password test1234

# Linux
./fantasma_cli.py list
sudo ./fantasma_cli.py start -s wlan0 -t wlan1 --ssid Test --password test1234
```

## Pull Request Process

### Before Submitting

1. **Update your fork**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Test your changes**
   - Run existing tests
   - Test manually on your platform
   - Check for errors/warnings

3. **Update documentation**
   - Update README if needed
   - Add docstrings to new functions
   - Update CHANGELOG.md

4. **Commit with clear messages**
   ```bash
   git commit -m "Add: Support for OpenWRT platform adapter"
   git commit -m "Fix: Memory leak in status broadcast task"
   git commit -m "Docs: Add tutorial for USB tethering"
   ```

### Commit Message Format

Use clear, descriptive commit messages:

```
Type: Short description (50 chars max)

Longer explanation if needed (wrap at 72 chars).
Explain what and why, not how.

- Bullet points are fine
- Reference issues: Fixes #123
```

Types:
- `Add:` New feature
- `Fix:` Bug fix
- `Docs:` Documentation
- `Refactor:` Code refactoring
- `Test:` Adding tests
- `Style:` Formatting changes

### Submitting PR

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Go to GitHub repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

3. **PR Description should include:**
   - What changes were made
   - Why the changes were needed
   - How to test the changes
   - Screenshots (for UI changes)
   - Related issues

### Review Process

- Maintainer will review your PR
- May request changes or clarifications
- Once approved, PR will be merged
- Your contribution will be in the next release!

### After PR is Merged

1. **Update your fork**
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

2. **Delete feature branch**
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

## Development Tips

### Testing Without Root

Some features require root/admin privileges. To test without privileges:

```python
# Use dry-run mode (planned feature)
./fantasma_cli.py start --dry-run ...

# Or mock system commands in tests
from unittest.mock import patch

@patch('subprocess.run')
def test_start_hotspot(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    # Test your code
```

### Debugging

Enable verbose logging:

```bash
./fantasma_cli.py start --verbose ...
```

Or in Python:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Pitfalls

1. **Platform-specific assumptions**
   - Don't assume interface names (en0 vs wlan0)
   - Check if tools exist before using them
   - Handle different network tool versions

2. **Permissions**
   - Many operations require root/admin
   - Provide clear error messages
   - Document permission requirements

3. **Error handling**
   - Network operations can fail in many ways
   - Always handle exceptions
   - Provide recovery suggestions

## Community

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community chat
- **Documentation**: README, ARCHITECTURE, TUTORIALS

### Recognition

Contributors will be recognized in:
- CHANGELOG.md for each release
- README.md contributors section (if significant contribution)
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (Sovereignty License - see LICENSE_SOVEREIGNTY.md).

---

## Quick Reference

```bash
# Setup
git clone https://github.com/YOUR_USERNAME/FantasmaWiFi-Pro.git
cd FantasmaWiFi-Pro
git remote add upstream https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git

# Before each contribution
git checkout main
git pull upstream main
git checkout -b feature/new-feature

# After changes
git add .
git commit -m "Add: New feature description"
git push origin feature/new-feature

# Create PR on GitHub
# Wait for review
# Address feedback if needed

# After merge
git checkout main
git pull upstream main
git branch -d feature/new-feature
```

---

**Thank you for contributing to Digital Sovereignty!** 🕸️
