"""
FantasmaWiFi-Pro Setup Script
"""

from setuptools import setup, find_packages
import os

# Read version from _version.py safely
version = {}
version_file = "_version.py"
with open(version_file, "r") as f:
    version_content = f.read()
    # Parse version without exec for security
    for line in version_content.split('\n'):
        if line.startswith('__version__'):
            version['__version__'] = line.split('=')[1].strip().strip('"').strip("'")

with open("README_NEW.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fantasmawifi-pro",
    version=version["__version__"],
    author="Iyari Cancino Gomez",
    description="Multi-platform WiFi hotspot and network bridge tool with Web UI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Blackmvmba88/FantasmaWiFi-Pro",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Android",
    ],
    python_requires=">=3.7",
    install_requires=[
        "flask>=2.3.2",
        "flask-socketio>=5.3.0",
        "python-socketio>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "fantasma=fantasma_cli:main",
            "fantasma-web=fantasma_web:main",
            "fantasma-doctor=fantasma_doctor:main",
        ],
    },
)
