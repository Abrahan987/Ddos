#!/bin/bash

echo "⚡ Installing HTTP Storm..."

# Detect system
if command -v pkg &> /dev/null; then
    # Termux
    echo "📱 Termux detected"
    pkg update
    pkg install -y python git
elif command -v apt &> /dev/null; then
    # Debian/Ubuntu  
    echo "🐧 Linux detected"
    sudo apt update
    sudo apt install -y python3 python3-pip git
else
    echo "❌ Unsupported system"
    exit 1
fi

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
mkdir -p logs results config

# Set permissions
chmod +x *.py
chmod +x scripts/*.sh

# Create default config if not exists
if [ ! -f "config/storm_config.json" ]; then
    cp config/storm_config.json config/local_config.json
    echo "📄 Default config created at config/local_config.json"
fi

echo ""
echo "✅ HTTP Storm installed successfully!"
echo ""
echo "🚀 Quick start:"
echo "   python storm.py https://httpbin.org/get"
echo ""
echo "📖 Full help:"
echo "   python storm.py --help"
echo ""
echo "⚙️  Edit config:"
echo "   nano config/storm_config.json"
