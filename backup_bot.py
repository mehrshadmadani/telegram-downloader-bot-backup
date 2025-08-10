#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import aiohttp
import tarfile
import tempfile
import sys
import json
from datetime import datetime

# --- پیکربندی ---
CONFIG_FILE = "backup_config.json"
# حداکثر حجم فایل تلگرام 50 مگابایت است، ما برای اطمینان 45 مگابایت در نظر می‌گیریم
MAX_FILE_SIZE = 45 * 1024 * 1024

# --- توابع کمکی ---

def load_config():
    """بارگذاری تنظیمات از فایل JSON."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"❌ خطا در بارگذاری فایل کانفیگ: {e}")
            return None
    return None

def save_config(config):
    """ذخیره تنظیمات در فایل JSON."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"✅ تنظیمات با موفقیت در فایل {CONFIG_FILE} ذخیره شد")
        return True
    except IOError as e:
        print(f"❌ خطا در ذخیره فایل کانفیگ: {e}")
        return False

def setup_cron_job():
    """راه اندازی تعاملی cron job برای بکاپ‌های خودکار."""
    print("\n--- ⏰ تنظیم بکاپ خودکار ---")
    
    script_path = os.path.abspath(sys.argv[0])
    script_dir = os.path.dirname(script_path)
    python_executable = os.path.join(script_dir, 'venv/bin/python3')
    log_file = os.path.join(script_dir, 'backup.log')

    if not os.path.exists(python_executable):
        print(f"⚠️ هشدار: مفسر پایتون در آدرس {python_executable} یافت نشد")
        print("لطفاً اطمینان حاصل کنید که محیط مجازی با نام 'venv' در همین پوشه قرار دارد.")
        python_executable = 'python3'

    enable_cron = input("آیا مایل به تنظیم بکاپ خودکار هستید؟ (y/n): ").strip().lower()
    if enable_cron not in ['y', 'yes']:
        print("ℹ️ شما می‌توانید بعداً به صورت دستی cron job را تنظیم کنید.")
        return

    while True:
        try:
            minutes = int(input("فاصله زمانی بکاپ به دقیقه را وارد کنید (مثال: 15, 30, 60): ").strip())
            if minutes > 0:
                break
            else:
                print("❌ فاصله زمانی باید یک عدد مثبت باشد.")
        except ValueError:
            print("❌ لطفاً یک عدد معتبر وارد کنید.")

    cron_command = f"*/{minutes} * * * * cd {script_dir} && {python_executable} {script_path} >> {log_file} 2>&1"
    
    try:
        current_crontab = os.popen('crontab -l 2>/dev/null').read()
        new_crontab = '\n'.join([line for line in current_crontab.split('\n') if script_path not in line])

        if new_crontab and not new_crontab.endswith('\n'):
            new_crontab += '\n'
        new_crontab += cron_command + '\n'

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write(new_crontab)
            tmp_path = tmp.name
        
        os.system(f'crontab {tmp_path}')
        os.unlink(tmp_path)

        print("\n✅ Cron job با موفقیت تنظیم شد!")
        print(f"🔄 بکاپ‌ها به صورت خودکار هر {minutes} دقیقه اجرا خواهند شد.")
        print(f"شما می‌توانید خروجی را در لاگ بررسی کنید: tail -f {log_file}")
        print("برای ویرایش یا حذف، از دستور crontab -e استفاده کنید")

    except Exception as e:
        print(f"\n❌ تنظیم خودکار cron job با شکست مواجه شد: {e}")
        print("لطفاً آن را به صورت دستی با اجرای 'crontab -e' و افزودن این خط، اضافه کنید:")
        print(f"   {cron_command}")

def interactive_setup():
    """اجرای راه اندازی تعاملی برای دریافت تنظیمات کاربر."""
    print("--- 🔧 راه اندازی تعاملی ---")
    config = {}
    config['bot_token'] = input("🤖 توکن ربات خود را وارد کنید: ").strip()
    config['admin_id'] = input("👤 آیدی عددی تلگرام خود را وارد کنید: ").strip()
    config['source_path'] = input("📁 آدرس کامل پوشه برای بکاپ را وارد کنید: ").strip()
    
    if all(config.values()):
        if save_config(config):
            setup_cron_job()
    else:
        print("❌ تمام فیلدها الزامی هستند. راه اندازی لغو شد.")

# --- منطق اصلی ---

async def send_to_telegram(bot_token, admin_id, file_path, original_folder_name):
    """ارسال فایل فشرده به ادمین از طریق تلگرام."""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    compressed_filename = os.path.basename(file_path)
    
    caption = f"📦 بکاپ خودکار پوشه: {original_folder_name}\n" \
              f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                form_data = aiohttp.FormData()
                form_data.add_field('chat_id', str(admin_id))
                form_data.add_field('caption', caption)
                form_data.add_field('document', f, filename=compressed_filename)
                
                print(f"📤 در حال آپلود بکاپ {compressed_filename}...")
                async with session.post(url, data=form_data) as response:
                    result = await response.json()
                    if response.status == 200 and result.get('ok'):
                        print("✅ بکاپ با موفقیت ارسال شد!")
                        return True
                    else:
                        error_msg = result.get('description', 'خطای نامشخص')
                        print(f"❌ ارسال بکاپ با شکست مواجه شد: {error_msg}")
                        return False
    except Exception as e:
        print(f"❌ خطایی هنگام ارسال رخ داد: {e}")
        return False

def compress_directory_to_targz(source_path):
    """فشرده‌سازی یک پوشه کامل در یک فایل موقت .tar.gz."""
    if not os.path.isdir(source_path):
        print(f"❌ خطا: پوشه‌ای در آدرس '{source_path}' یافت نشد.")
        return None

    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp_file:
        archive_path = tmp_file.name

    original_folder_name = os.path.basename(source_path.rstrip('/'))
    print(f"📦 در حال فشرده‌سازی پوشه '{original_folder_name}'...")
    
    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(source_path, arcname=original_folder_name)
        
        file_size = os.path.getsize(archive_path)
        size_mb = file_size / (1024 * 1024)
        print(f"� فشرده‌سازی کامل شد. حجم فایل: {size_mb:.2f} مگابایت")

        if file_size > MAX_FILE_SIZE:
            print(f"⚠️ هشدار: حجم فایل فشرده ({size_mb:.2f} مگابایت) از حد مجاز تلگرام بیشتر است.")
            print("❌ بکاپ به دلیل حجم بالای فایل لغو شد.")
            os.unlink(archive_path)
            return None

        return archive_path
    except Exception as e:
        print(f"❌ فشرده‌سازی پوشه با خطا مواجه شد: {e}")
        if os.path.exists(archive_path):
            os.unlink(archive_path)
        return None

async def run_backup_process(config):
    """اجرای منطق اصلی بکاپ با استفاده از تنظیمات داده شده."""
    bot_token = config.get('bot_token')
    admin_id = config.get('admin_id')
    source_path = config.get('source_path')

    if not all([bot_token, admin_id, source_path]):
        print("❌ تنظیمات ناقص است. لطفاً با --setup اجرا کنید.")
        return

    print(f"\n▶️ شروع فرآیند بکاپ برای پوشه: {source_path}")
    compressed_path = compress_directory_to_targz(source_path)

    if not compressed_path:
        print("💥 فرآیند بکاپ هنگام فشرده‌سازی متوقف شد.")
        return

    success = await send_to_telegram(bot_token, admin_id, compressed_path, os.path.basename(source_path.rstrip('/')))

    if os.path.exists(compressed_path):
        os.unlink(compressed_path)
        print("🗑️ فایل آرشیو موقت حذف شد.")

    if success:
        print("\n🎉 فرآیند بکاپ با موفقیت انجام شد!")
    else:
        print("\n💥 فرآیند بکاپ با شکست مواجه شد.")

# --- نقطه ورود اصلی ---

async def main():
    """تابع اصلی برای مدیریت آرگومان‌ها و اجرای ربات."""
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        interactive_setup()
        return

    print(f"--- 🚀 ربات بکاپ تلگرام | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    config = load_config()
    
    if not config:
        print("تنظیمات یافت نشد!")
        print("لطفاً ابتدا راه اندازی تعاملی را اجرا کنید:")
        print(f"  python3 {sys.argv[0]} --setup")
        return
    
    await run_backup_process(config)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 فرآیند توسط کاربر متوقف شد.")
        sys.exit(0)
�
