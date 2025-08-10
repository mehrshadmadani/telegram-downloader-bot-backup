#!/bin/bash

# One-line installer for Telegram Backup Bot
echo "🚀 Installing Telegram Backup Bot..." && git clone https://github.com/mehrshadmadani/telegram-downloader-bot-backup.git && cd telegram-downloader-bot-backup && chmod +x setup.sh && ./setup.sh && python3 backup_bot.py --setup
