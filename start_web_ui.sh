#!/bin/bash
# FantasmaWiFi-Pro Web UI Quick Start Script

echo "================================================"
echo "🕸️  FantasmaWiFi-Pro Web UI v7.5"
echo "================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed"
    echo "Please install pip3"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""
echo "🚀 Starting Web UI server..."
echo ""

# Start the web server
python3 fantasma_web.py "$@"
