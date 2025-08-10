#!/bin/bash

echo "🔧 Setting up Telegram Backup Bot..."

# نصب پایتون اگر نصب نیست
if ! command -v python3 &> /dev/null; then
    echo "📦 Installing Python3..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

# نصب pip اگر نصب نیست
if ! command -v pip3 &> /dev/null; then
    echo "📦 Installing pip3..."
    sudo apt install -y python3-pip
fi

# نصب کتابخانه‌های مورد نیاز
echo "📦 Installing required packages..."
pip3 install -r requirements.txt

# قابل اجرا کردن فایل
chmod +x backup_bot.py

echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Run: python3 backup_bot.py --setup"
echo "2. Enter your bot token and group information"
echo "3. Run: python3 backup_bot.py --run (for manual backup)"
echo "4. Or add to crontab for automatic backups"
echo ""
echo "⏰ To setup automatic backups every 15 minutes:"
echo "   crontab -e"
echo "   Add line: */15 * * * * cd $(pwd) && python3 backup_bot.py --run >> backup.log 2>&1"
