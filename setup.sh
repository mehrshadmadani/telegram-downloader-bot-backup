#!/bin/bash

echo "🔧 Setting up Telegram File Backup Bot..."

# Check for Python3
if ! command -v python3 &> /dev/null; then
    echo "📦 Python3 not found. Please install it first."
    # Example for Debian/Ubuntu: sudo apt update && sudo apt install -y python3
    exit 1
fi

# Check for pip3
if ! command -v pip3 &> /dev/null; then
    echo "📦 pip3 not found. Please install it first."
    # Example for Debian/Ubuntu: sudo apt install -y python3-pip
    exit 1
fi

# Install required Python packages from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "📦 Installing required Python packages..."
    pip3 install -r requirements.txt
else
    echo "⚠️ requirements.txt not found. Skipping package installation."
fi

# Make the main script executable
chmod +x backup_bot.py

echo ""
echo "✅ Setup is complete!"
echo ""
echo "👉 To run the bot, simply execute:"
echo "   python3 backup_bot.py"
echo ""
