#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import aiohttp
import tarfile
import tempfile
import sys
from datetime import datetime

# حداکثر حجم فایل برای آپلود در تلگرام (45 مگابایت)
MAX_FILE_SIZE = 45 * 1024 * 1024

async def send_to_telegram(bot_token, admin_id, file_path, original_folder_name):
    """فایل فشرده را از طریق تلگرام برای ادمین ارسال می‌کند."""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    compressed_filename = os.path.basename(file_path)
    
    caption = f"📦 بکاپ پوشه: {original_folder_name}\n" \
              f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                form_data = aiohttp.FormData()
                form_data.add_field('chat_id', str(admin_id))
                form_data.add_field('caption', caption)
                form_data.add_field('document', f, filename=compressed_filename)
                
                print(f"📤 در حال آپلود بکاپ {compressed_filename} به تلگرام برای ادمین {admin_id}...")
                async with session.post(url, data=form_data) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get('ok'):
                        print("✅ بکاپ با موفقیت ارسال شد!")
                        return True
                    else:
                        error_msg = result.get('description', 'خطای نامشخص')
                        print(f"❌ ارسال بکاپ با شکست مواجه شد: {error_msg}")
                        if "bot can't initiate conversation" in error_msg.lower():
                            print("💡 راهنمایی: لطفاً ابتدا ربات را استارت کنید (یک پیام یا دستور /start برای آن ارسال کنید).")
                        return False
    except Exception as e:
        print(f"❌ خطایی هنگام ارسال رخ داد: {e}")
        return False

def compress_directory_to_targz(source_path):
    """یک پوشه کامل را در یک فایل موقت با فرمت .tar.gz فشرده می‌کند."""
    if not os.path.isdir(source_path):
        print(f"❌ خطا: پوشه منبع در آدرس '{source_path}' یافت نشد.")
        return None

    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp_file:
        archive_path = tmp_file.name

    original_folder_name = os.path.basename(source_path)
    print(f"📦 در حال فشرده‌سازی پوشه '{original_folder_name}'...")
    
    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_path, arcname=original_folder_name)
        
        file_size = os.path.getsize(archive_path)
        size_mb = file_size / (1024 * 1024)
        print(f"📊 فشرده‌سازی کامل شد. حجم فایل: {size_mb:.2f} مگابایت")

        if file_size > MAX_FILE_SIZE:
            print(f"⚠️ هشدار: حجم فایل فشرده ({size_mb:.2f} مگابایت) بیشتر از حد مجاز تلگرام است.")
            proceed = input("آیا می‌خواهید به هر حال برای آپلود تلاش کنید؟ (y/n): ").strip().lower()
            if proceed not in ['y', 'yes']:
                os.unlink(archive_path)
                print("عملیات توسط کاربر لغو شد.")
                return None

        return archive_path
    except Exception as e:
        print(f"❌ فشرده‌سازی پوشه با خطا مواجه شد: {e}")
        if os.path.exists(archive_path):
            os.unlink(archive_path)
        return None

async def main():
    """تابع اصلی برای اجرای فرآیند بکاپ."""
    print("🚀 ربات بکاپ پوشه در تلگرام 🚀")
    print("=" * 30)

    bot_token = input("🤖 توکن ربات خود را وارد کنید: ").strip()
    admin_id = input("👤 آیدی عددی تلگرام خود را وارد کنید: ").strip()
    source_path = input("📁 آدرس کامل پوشه‌ای که می‌خواهید بکاپ بگیرید را وارد کنید: ").strip()

    if not all([bot_token, admin_id, source_path]):
        print("❌ تمام اطلاعات (توکن، آیدی و آدرس پوشه) باید وارد شوند.")
        return

    original_folder_name = os.path.basename(source_path.rstrip('/'))
    compressed_path = compress_directory_to_targz(source_path)

    if not compressed_path:
        print("💥 فرآیند بکاپ متوقف شد.")
        return

    success = await send_to_telegram(bot_token, admin_id, compressed_path, original_folder_name)

    if os.path.exists(compressed_path):
        os.unlink(compressed_path)
        print("🗑️ فایل آرشیو موقت حذف شد.")

    if success:
        print("\n🎉 فرآیند بکاپ با موفقیت انجام شد!")
    else:
        print("\n💥 فرآیند بکاپ با شکست مواجه شد.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 فرآیند توسط کاربر متوقف شد.")
        sys.exit(0)
