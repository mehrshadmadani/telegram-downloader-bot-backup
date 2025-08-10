# Telegram Backup Bot 🤖

این اسکریپت به صورت خودکار فایل‌های پروژه شما را فشرده کرده و به تلگرام ارسال می‌کند.

## 🚀 نصب تک-خطی

```bash
git clone https://github.com/mehrshadmadani/telegram-downloader-bot-backup.git && cd telegram-downloader-bot-backup && chmod +x setup.sh && ./setup.sh && python3 backup_bot.py --setup
```

یا با curl:

```bash
curl -s https://raw.githubusercontent.com/mehrshadmadani/telegram-downloader-bot-backup/main/install.sh | bash
```

## ✨ ویژگی‌ها

- 📦 فشرده‌سازی خودکار فایل‌ها (زیر 50MB)
- 🚀 ارسال خودکار به گروه/کانال تلگرام
- 📌 پشتیبانی از ارسال به تاپیک خاص
- 🗑️ حذف خودکار فایل‌های غیرضروری
- ⚙️ پیکربندی آسان با سوالات تعاملی
- ⏰ تنظیم خودکار cron job (هر چند دقیقه که بخواهید)

## 📋 پیش‌نیازها

1. **ربات تلگرام**: از [@BotFather](https://t.me/BotFather) یک ربات بسازید
2. **اضافه کردن ربات**: ربات را به گروه اضافه کنید و Admin کنید
3. **پایتون 3.7+**: روی سرور نصب باشد

## 🛠️ راه‌اندازی مرحله به مرحله

### 1. ساخت ربات تلگرام
- به [@BotFather](https://t.me/BotFather) پیام دهید
- دستور `/newbot` را ارسال کنید
- نام و یوزرنیم ربات را انتخاب کنید
- **Bot Token** را کپی کنید

### 2. اضافه کردن ربات به گروه
- ربات را به گروه اضافه کنید
- ربات را **Admin** کنید (برای ارسال فایل)

### 3. دریافت Group ID
**روش 1:** استفاده از [@userinfobot](https://t.me/userinfobot)
- @userinfobot را به گروه اضافه کنید
- Group ID را کپی کنید (مثل `-1001234567890`)

**روش 2:** از طریق لینک گروه
- اگر لینک گروه `t.me/c/1234567890/1` باشد
- Group ID برابر است با: `-1001234567890`

### 4. دریافت Topic ID (اختیاری)
- روی تاپیک مورد نظر کلیک راست کنید
- "Copy Link" را انتخاب کنید
- آیدی عددی انتهای لینک همان Topic ID است

### 5. اجرای اسکریپت
```bash
git clone https://github.com/mehrshadmadani/telegram-downloader-bot-backup.git && cd telegram-downloader-bot-backup && chmod +x setup.sh && ./setup.sh && python3 backup_bot.py --setup
```

اطلاعات زیر را وارد کنید:
- **Bot Token**: از BotFather
- **Group ID**: آیدی عددی گروه 
- **Topic ID**: آیدی تاپیک (اختیاری)
- **Source Directory**: مسیر پوشه برای بکاپ (پیش‌فرض: پوشه فعلی)
- **Backup Interval**: هر چند دقیقه بکاپ ارسال شود (15، 30، 60)

## 🎯 نحوه استفاده

### دستورات اصلی:
```bash
# راه‌اندازی اولیه
python3 backup_bot.py --setup

# اجرای دستی بکاپ
python3 backup_bot.py --run

# اجرای معمولی (اگر کانفیگ وجود داشته باشد)
python3 backup_bot.py
```

### مشاهده لاگ‌ها:
```bash
# مشاهده لاگ‌های بکاپ
tail -f backup.log

# مشاهده cron jobs
crontab -l
```

## 📁 ساختار فایل‌ها

```
telegram-downloader-bot-backup/
├── backup_bot.py          # اسکریپت اصلی
├── install.sh            # نصب تک-خطی
├── setup.sh              # نصب dependencies
├── requirements.txt       # کتابخانه‌های مورد نیاز
├── README.md             # راهنما
├── backup_config.json    # فایل تنظیمات (خودکار ساخته می‌شود)
└── backup.log            # لاگ‌های بکاپ
```

## 🗂️ فایل‌های حذف شده از بکاپ

- `__pycache__/` - فایل‌های کش پایتون
- `.git/` - مخزن گیت
- `.venv/`, `venv/` - محیط‌های مجازی
- `node_modules/` - کتابخانه‌های Node.js
- `*.pyc`, `*.pyo` - فایل‌های کامپایل شده
- `*.log`, `*.tmp` - فایل‌های موقت و لاگ
- `backup_config.json` - فایل تنظیمات

## 🐛 عیب‌یابی

### ❌ خطای "Chat not found"
- بررسی کنید ربات در گروه Admin باشد
- Group ID را مجدداً بررسی کنید (باید شروع به `-100` شود)

### ❌ خطای "File too large"
- اسکریپت خودکار فایل‌های غیرضروری را حذف می‌کند
- در صورت بزرگ بودن، فقط فایل‌های اصلی (.py, .json, .txt) بکاپ می‌شوند

### ❌ خطای "Invalid bot token"
- توکن ربات را از BotFather مجدداً دریافت کنید
- بررسی کنید هیچ کاراکتر اضافی نداشته باشد

### ❌ cron job کار نمی‌کند
```bash
# بررسی وضعیت cron
sudo systemctl status cron

# مشاهده لاگ‌های cron
sudo tail -f /var/log/cron.log

# تست دستی
cd /path/to/backup-bot && python3 backup_bot.py --run
```

## 🔧 تنظیمات پیشرفته

### تغییر فاصله زمانی بکاپ:
```bash
# ویرایش cron job
crontab -e

# مثال‌ها:
*/15 * * * *   # هر 15 دقیقه
0 */2 * * *    # هر 2 ساعت
0 0 * * *      # روزانه در ساعت 00:00
```

### تنظیمات دستی:
فایل `backup_config.json` را ویرایش کنید:
```json
{
  "bot_token": "1234567890:ABCD...",
  "group_id": -1001234567890,
  "topic_id": 123456,
  "source_dir": "/root/telegram-downloader-bot"
}
```

## 📞 پشتیبانی

اگر مشکلی داشتید:
1. لاگ‌های `backup.log` را بررسی کنید
2. دستور `python3 backup_bot.py --run` را به صورت دستی اجرا کنید
3. بررسی کنید ربات دسترسی‌های لازم را داشته باشد

## 📄 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

---

**نکته:** این ربات برای بکاپ خودکار پروژه‌ها طراحی شده و نه برای استفاده تجاری. از آن مسئولانه استفاده کنید.
