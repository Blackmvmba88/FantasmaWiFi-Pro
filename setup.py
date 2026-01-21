"""
FantasmaWiFi-Pro Setup Script
"""

from setuptools import setup, find_packages

with open("README_NEW.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fantasmawifi-pro",
    version="7.0.0",
    author="Iyari Cancino Gomez",
    description="Multi-platform WiFi hotspot and network bridge tool",
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
    entry_points={
        "console_scripts": [
            "fantasma=fantasma_cli:main",
        ],
    },
)
