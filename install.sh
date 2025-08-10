#!/bin/bash

# One-line installer for Telegram File Backup Bot
echo "🚀 Installing Telegram File Backup Bot..."

# Define repo details
REPO_URL="https://github.com/mehrshadmadani/telegram-downloader-bot-backup.git"
REPO_DIR="telegram-downloader-bot-backup"

# Clone the repository
if ! git clone "$REPO_URL"; then
    echo "❌ Failed to clone the repository. Please check the URL and your internet connection."
    exit 1
fi

# Change into the directory
cd "$REPO_DIR" || { echo "❌ Failed to enter the repository directory."; exit 1; }

# Make setup script executable and run it
if [ -f "setup.sh" ]; then
    chmod +x setup.sh
    ./setup.sh
else
    echo "⚠️ setup.sh not found. Please run the setup steps manually."
fi

echo "🎉 Installation finished."
echo "Navigate to the '$REPO_DIR' directory and run 'python3 backup_bot.py' to start."
