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
# تلگرام محدودیت 50 مگابایتی دارد، اما برای اطمینان کمی کمتر در نظر گرفته شده است
MAX_FILE_SIZE = 45 * 1024 * 1024

async def send_to_telegram(bot_token, admin_id, file_path, original_filename):
    """فایل را از طریق تلگرام برای ادمین مشخص شده ارسال می‌کند."""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    # نام فایل فشرده شده
    compressed_filename = os.path.basename(file_path)
    
    caption = f"📦 بکاپ فایل: {original_filename}\n" \
              f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    try:
        async with aiohttp.ClientSession() as session:
            # از open معمولی استفاده می‌کنیم چون aiohttp خودش فایل را به صورت غیرهمزمان می‌خواند
            with open(file_path, 'rb') as f:
                form_data = aiohttp.FormData()
                form_data.add_field('chat_id', str(admin_id))
                form_data.add_field('caption', caption)
                form_data.add_field('document', f, filename=compressed_filename)
                
                print(f"📤 در حال آپلود فایل {compressed_filename} به تلگرام برای ادمین {admin_id}...")
                async with session.post(url, data=form_data) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get('ok'):
                        print("✅ فایل با موفقیت ارسال شد!")
                        return True
                    else:
                        error_msg = result.get('description', 'خطای نامشخص')
                        print(f"❌ ارسال فایل با شکست مواجه شد: {error_msg}")
                        if "bot can't initiate conversation" in error_msg.lower():
                            print("💡 راهنمایی: لطفاً ابتدا ربات را استارت کنید (یک پیام یا دستور /start برای آن ارسال کنید).")
                        return False
    except Exception as e:
        print(f"❌ خطایی هنگام ارسال رخ داد: {e}")
        return False

def compress_file_to_targz(source_path):
    """یک فایل مشخص را در یک فایل موقت با فرمت .tar.gz فشرده می‌کند."""
    if not os.path.isfile(source_path):
        print(f"❌ خطا: فایل منبع در آدرس '{source_path}' یافت نشد.")
        return None

    # یک فایل موقت برای آرشیو ایجاد می‌کنیم
    # از delete=False استفاده می‌کنیم تا بتوانیم مسیر آن را برگردانیم
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp_file:
        archive_path = tmp_file.name

    original_filename = os.path.basename(source_path)
    archive_basename = os.path.basename(archive_path)
    print(f"📦 در حال فشرده‌سازی '{original_filename}' به فایل '{archive_basename}'...")
    
    try:
        # فایل را با فرمت tar.gz باز کرده و فشرده می‌کنیم
        with tarfile.open(archive_path, "w:gz") as tar:
            # فایل را به آرشیو اضافه می‌کنیم. arcname باعث می‌شود فایل در ریشه آرشیو قرار گیرد
            tar.add(source_path, arcname=original_filename)
        
        file_size = os.path.getsize(archive_path)
        size_mb = file_size / (1024 * 1024)
        print(f"📊 فشرده‌سازی کامل شد. حجم فایل: {size_mb:.2f} مگابایت")

        if file_size > MAX_FILE_SIZE:
            print(f"⚠️ هشدار: حجم فایل فشرده ({size_mb:.2f} مگابایت) بیشتر از حد مجاز 45 مگابایت برای تلگرام است.")
            proceed = input("آیا می‌خواهید به هر حال برای آپلود تلاش کنید؟ (y/n): ").strip().lower()
            if proceed not in ['y', 'yes']:
                os.unlink(archive_path)  # پاک کردن فایل موقت
                print("عملیات توسط کاربر لغو شد.")
                return None

        return archive_path
    except Exception as e:
        print(f"❌ فشرده‌سازی فایل با خطا مواجه شد: {e}")
        if os.path.exists(archive_path):
            os.unlink(archive_path)  # پاک کردن فایل موقت
        return None

async def main():
    """تابع اصلی برای اجرای فرآیند بکاپ."""
    print("🚀 ربات بکاپ فایل در تلگرام 🚀")
    print("=" * 30)

    # ۱. دریافت توکن ربات
    bot_token = ""
    while not bot_token:
        token = input("🤖 توکن ربات خود را وارد کنید (دریافت از @BotFather): ").strip()
        if ':' in token and len(token) > 20:
            bot_token = token
        else:
            print("❌ فرمت توکن ربات نامعتبر است. لطفاً دوباره تلاش کنید.")

    # ۲. دریافت آیدی عددی ادمین
    admin_id = ""
    while not admin_id:
        try:
            aid = input("👤 آیدی عددی تلگرام خود را وارد کنید (آیدی ادمین): ").strip()
            admin_id = int(aid)
        except ValueError:
            print("❌ آیدی نامعتبر است. لطفاً یک آیدی عددی وارد کنید.")

    # ۳. دریافت آدرس فایل
    file_path = ""
    while not file_path:
        path = input("📁 آدرس کامل فایلی که می‌خواهید بکاپ بگیرید را وارد کنید: ").strip()
        if os.path.isfile(path):
            file_path = path
        else:
            print(f"❌ فایلی در آدرس '{path}' یافت نشد. لطفاً آدرس را بررسی کرده و دوباره تلاش کنید.")
    
    # ۴. فشرده‌سازی فایل
    original_filename = os.path.basename(file_path)
    compressed_path = compress_file_to_targz(file_path)

    if not compressed_path:
        print("💥 فرآیند بکاپ به دلیل خطا در فشرده‌سازی یا لغو توسط کاربر، متوقف شد.")
        return

    # ۵. ارسال به تلگرام
    success = await send_to_telegram(bot_token, admin_id, compressed_path, original_filename)

    # ۶. پاک کردن فایل موقت
    if os.path.exists(compressed_path):
        os.unlink(compressed_path)
        print("🗑️ فایل آرشیو موقت حذف شد.")

    if success:
        print("\n🎉 فرآیند بکاپ با موفقیت انجام شد!")
    else:
        print("\n💥 فرآیند بکاپ با شکست مواجه شد.")

if __name__ == "__main__":
    try:
        # اجرای تابع اصلی به صورت غیرهمزمان
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 فرآیند توسط کاربر متوقف شد.")
        sys.exit(0)
