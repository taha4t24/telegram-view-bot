from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

import requests
import sqlite3

# =========================
# تنظیمات
# =========================

BOT_TOKEN = "8667603518:AAFxT66irkdxIzpcJVrKmS2XPIdwDI1acHc"
API_KEY = "x5PLaG2rO6KIMwz4"

ADMIN_ID = 8019491735

BASE_URL = "https://api.power-tel.ir/apic.php"

LINK, COUNT = range(2)

# =========================
# دیتابیس
# =========================

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    banned INTEGER DEFAULT 0
)
""")

conn.commit()

# =========================
# کیبورد ها
# =========================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["📈 ثبت ویو", "💰 موجودی"],
        ["👤 حساب من"],
        ["❌ لغو"]
    ],
    resize_keyboard=True
)

admin_keyboard = ReplyKeyboardMarkup(
    [
        ["📊 آمار", "📨 پیام همگانی"],
        ["➕ شارژ کاربر", "🚫 بن کاربر"],
        ["✅ آنبن کاربر"],
        ["⬅️ بازگشت"]
    ],
    resize_keyboard=True
)

# =========================
# توابع دیتابیس
# =========================

def add_user(user_id):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()

def get_balance(user_id):
    cursor.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    return 0

def change_balance(user_id, amount):
    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id=?",
        (amount, user_id)
    )

    conn.commit()

def is_banned(user_id):
    cursor.execute(
        "SELECT banned FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    if result:
        return result[0] == 1

    return False

def ban_user(user_id):
    cursor.execute(
        "UPDATE users SET banned=1 WHERE user_id=?",
        (user_id,)
    )

    conn.commit()

def unban_user(user_id):
    cursor.execute(
        "UPDATE users SET banned=0 WHERE user_id=?",
        (user_id,)
    )

    conn.commit()

# =========================
# استارت
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    add_user(user_id)

    if is_banned(user_id):
        await update.message.reply_text(
            "شما از ربات مسدود شده‌اید ❌"
        )
        return

    await update.message.reply_text(
        """به ربات تلگرامی Pulse+SP خوش آمدید

⬅️ به منوی اصلی بازگشتید""",
        reply_markup=main_keyboard
    )

# =========================
# موجودی
# =========================

async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if is_banned(user_id):
        return

    params = {
        "type": "amount",
        "apikey": API_KEY
    }

    r = requests.get(BASE_URL, params=params)
    data = r.json()

    await update.message.reply_text(
        f"💰 موجودی پنل:\n{data['amount']}",
        reply_markup=main_keyboard
    )

# =========================
# حساب من
# =========================

async def my_account(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    balance = get_balance(user_id)

    await update.message.reply_text(
        f"""👤 حساب شما

🆔 آیدی:
{user_id}

💰 موجودی:
{balance} تومان""",
        reply_markup=main_keyboard
    )

# =========================
# ثبت ویو
# =========================

async def view_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if is_banned(user_id):
        return ConversationHandler.END

    await update.message.reply_text("لینک پست را ارسال کن:")
    return LINK

async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["link"] = update.message.text

    await update.message.reply_text("تعداد ویو را وارد کن:")
    return COUNT

async def get_count(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        link = context.user_data["link"]
        count = int(update.message.text)

        parts = link.split("/")
        channel = parts[-2]
        post_id = int(parts[-1])

        params = {
            "apikey": API_KEY,
            "typeseen": "en",
            "type": "view",
            "count": count,
            "runs": 1,
            "speed": 100,
            "period": 5,
            "channel": channel,
            "id": post_id
        }

        r = requests.get(BASE_URL, params=params)
        data = r.json()

        msg = (
            "✅ سفارش ثبت شد\n\n"
            f"🆔 شماره سفارش: {data['order']}\n"
            f"👁 تعداد: {data['count']}\n"
            f"📢 کانال: @VPNPulseX"
        )

        await update.message.reply_text(
            msg,
            reply_markup=main_keyboard
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            "خطا ❌",
            reply_markup=main_keyboard
        )

    return ConversationHandler.END

# =========================
# پنل ادمین
# =========================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "👑 پنل مدیریت",
        reply_markup=admin_keyboard
    )

# =========================
# آمار
# =========================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")

    users = cursor.fetchone()[0]

    await update.message.reply_text(
        f"📊 تعداد کاربران:\n{users}",
        reply_markup=admin_keyboard
    )

# =========================
# لغو
# =========================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "عملیات لغو شد ❌",
        reply_markup=main_keyboard
    )

    return ConversationHandler.END

# =========================
# دکمه ها
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "📈 ثبت ویو":
        return await view_start(update, context)

    elif text == "💰 موجودی":
        await amount(update, context)

    elif text == "👤 حساب من":
        await my_account(update, context)

    elif text == "📊 آمار":
        await stats(update, context)

    elif text == "⬅️ بازگشت":
        await start(update, context)

# =========================
# اجرای ربات
# =========================

app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^📈 ثبت ویو$"), view_start)
    ],
    states={
        LINK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_link)
        ],
        COUNT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_count)
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^❌ لغو$"), cancel)
    ],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))

app.add_handler(conv_handler)

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler)
)

print("Bot started...")
app.run_polling()
