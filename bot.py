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
import datetime

# =========================
# تنظیمات
# =========================

BOT_TOKEN = "توکن ربات"

API_KEY = "API"

ADMIN_ID = 8019491735

BASE_URL = "https://api.power-tel.ir/apic.php"

LINK, COUNT = range(2)

# =========================
# دیتابیس
# =========================

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = conn.cursor()

# کاربران
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    banned INTEGER DEFAULT 0,
    inviter INTEGER DEFAULT 0
)
""")

# سفارشات
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    channel TEXT,
    count INTEGER,
    order_id TEXT,
    price INTEGER,
    date TEXT
)
""")

# لاگ
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    date TEXT
)
""")

# کد تخفیف
cursor.execute("""
CREATE TABLE IF NOT EXISTS discounts (
    code TEXT,
    percent INTEGER
)
""")

conn.commit()

# =========================
# کیبورد ها
# =========================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["📈 ثبت ویو", "💰 موجودی پنل"],
        ["👤 حساب من", "💳 افزایش موجودی"],
        ["📜 سفارش های من"],
        ["❌ لغو"]
    ],
    resize_keyboard=True
)

admin_keyboard = ReplyKeyboardMarkup(
    [
        ["📊 آمار", "📨 ارسال همگانی"],
        ["➕ شارژ کاربر", "🚫 بن کاربر"],
        ["✅ آنبن کاربر", "📋 سفارش ها"],
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

def save_order(
    user_id,
    channel,
    count,
    order_id,
    price
):

    cursor.execute(
        """
        INSERT INTO orders
        (
            user_id,
            channel,
            count,
            order_id,
            price,
            date
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            channel,
            count,
            order_id,
            price,
            str(datetime.datetime.now())
        )
    )

    conn.commit()

def save_log(text):

    cursor.execute(
        """
        INSERT INTO logs
        (
            text,
            date
        )
        VALUES (?, ?)
        """,
        (
            text,
            str(datetime.datetime.now())
        )
    )

    conn.commit()

# =========================
# استارت
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    add_user(user_id)

    if is_banned(user_id):

        await update.message.reply_text(
            "شما از ربات مسدود شده‌اید ❌"
        )

        return

    await update.message.reply_text(
        """
به ربات تلگرامی Pulse+SP خوش آمدید

⬅️ به منوی اصلی بازگشتید
        """,
        reply_markup=main_keyboard
    )

# =========================
# حساب من
# =========================

async def my_account(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    balance = get_balance(user_id)

    await update.message.reply_text(
        f"""
👤 حساب شما

🆔 آیدی:
{user_id}

💰 موجودی:
{balance} تومان
        """,
        reply_markup=main_keyboard
    )

# =========================
# موجودی پنل
# =========================

async def amount(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    params = {
        "type": "amount",
        "apikey": API_KEY
    }

    r = requests.get(
        BASE_URL,
        params=params
    )

    data = r.json()

    await update.message.reply_text(
        f"""
💰 موجودی پنل:

{data['amount']}
        """,
        reply_markup=main_keyboard
    )

# =========================
# افزایش موجودی
# =========================

async def increase_balance(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        """
💳 افزایش موجودی

مبلغ را به کارت زیر واریز کنید:

6037-xxxx-xxxx-xxxx

بعد از پرداخت رسید را برای ادمین ارسال کنید.
        """,
        reply_markup=main_keyboard
    )

# =========================
# ثبت ویو
# =========================

async def view_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if is_banned(user_id):

        return ConversationHandler.END

    await update.message.reply_text(
        "لینک پست را ارسال کن:"
    )

    return LINK

async def get_link(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["link"] = update.message.text

    await update.message.reply_text(
        "تعداد ویو را وارد کن:"
    )

    return COUNT

async def get_count(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        user_id = update.effective_user.id

        count = int(update.message.text)

        price = count

        balance = get_balance(user_id)

        if balance < price:

            await update.message.reply_text(
                "موجودی شما کافی نیست ❌",
                reply_markup=main_keyboard
            )

            return ConversationHandler.END

        link = context.user_data["link"]

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

        r = requests.get(
            BASE_URL,
            params=params
        )

        data = r.json()

        change_balance(
            user_id,
            -price
        )

        save_order(
            user_id,
            channel,
            count,
            data["order"],
            price
        )

        save_log(
            f"new order user:{user_id}"
        )

        # نوتیف برای ادمین
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""
📦 سفارش جدید

👤 کاربر:
{user_id}

📢 کانال:
{channel}

👁 تعداد:
{count}
            """
        )

        await update.message.reply_text(
            f"""
✅ سفارش ثبت شد

🆔 شماره سفارش:
{data['order']}

👁 تعداد:
{count}

📢 کانال:
@VPNPulseX

💰 هزینه:
{price} تومان
            """,
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
# سفارش های من
# =========================

async def my_orders(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    cursor.execute(
        """
        SELECT channel,count,price,date
        FROM orders
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 10
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    if not rows:

        await update.message.reply_text(
            "سفارشی ندارید ❌"
        )

        return

    text = "📜 سفارش های شما\n\n"

    for row in rows:

        text += (
            f"📢 {row[0]}\n"
            f"👁 {row[1]}\n"
            f"💰 {row[2]}\n"
            f"📅 {row[3]}\n\n"
        )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# =========================
# پنل ادمین
# =========================

async def admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        """
👑 پنل مدیریت
        """,
        reply_markup=admin_keyboard
    )

# =========================
# آمار
# =========================

async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    users = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM orders"
    )

    orders = cursor.fetchone()[0]

    cursor.execute(
        "SELECT SUM(price) FROM orders"
    )

    income = cursor.fetchone()[0]

    if income is None:
        income = 0

    await update.message.reply_text(
        f"""
📊 آمار کامل ربات

👤 کاربران:
{users}

📦 سفارش ها:
{orders}

💰 درآمد:
{income} تومان
        """,
        reply_markup=admin_keyboard
    )

# =========================
# شارژ حساب
# =========================

async def addbalance(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        user_id = int(
            context.args[0]
        )

        amount = int(
            context.args[1]
        )

        change_balance(
            user_id,
            amount
        )

        await update.message.reply_text(
            "موجودی افزایش یافت ✅"
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=f"""
💰 حساب شما شارژ شد

مبلغ:
{amount} تومان
            """
        )

    except:

        await update.message.reply_text(
            "خطا ❌"
        )

# =========================
# بن کاربر
# =========================

async def ban(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        user_id = int(
            context.args[0]
        )

        ban_user(user_id)

        await update.message.reply_text(
            "کاربر بن شد ✅"
        )

    except:

        await update.message.reply_text(
            "خطا ❌"
        )

# =========================
# آنبن
# =========================

async def unban(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        user_id = int(
            context.args[0]
        )

        unban_user(user_id)

        await update.message.reply_text(
            "کاربر آزاد شد ✅"
        )

    except:

        await update.message.reply_text(
            "خطا ❌"
        )

# =========================
# سفارش ها
# =========================

async def orders_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute(
        """
        SELECT user_id,channel,count,price
        FROM orders
        ORDER BY id DESC
        LIMIT 10
        """
    )

    rows = cursor.fetchall()

    text = "📋 آخرین سفارش ها\n\n"

    for row in rows:

        text += (
            f"👤 {row[0]}\n"
            f"📢 {row[1]}\n"
            f"👁 {row[2]}\n"
            f"💰 {row[3]}\n\n"
        )

    await update.message.reply_text(
        text,
        reply_markup=admin_keyboard
    )

# =========================
# ارسال همگانی
# =========================

async def broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        text = " ".join(
            context.args
        )

        cursor.execute(
            "SELECT user_id FROM users"
        )

        users = cursor.fetchall()

        sent = 0

        for user in users:

            try:

                await context.bot.send_message(
                    chat_id=user[0],
                    text=text
                )

                sent += 1

            except:
                pass

        await update.message.reply_text(
            f"""
📨 ارسال همگانی انجام شد

تعداد:
{sent}
            """
        )

    except:

        await update.message.reply_text(
            "خطا ❌"
        )

# =========================
# کد تخفیف
# =========================

async def add_discount(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        code = context.args[0]

        percent = int(
            context.args[1]
        )

        cursor.execute(
            """
            INSERT INTO discounts
            (code,percent)
            VALUES (?,?)
            """,
            (
                code,
                percent
            )
        )

        conn.commit()

        await update.message.reply_text(
            "کد تخفیف ساخته شد ✅"
        )

    except:

        await update.message.reply_text(
            "خطا ❌"
        )
   "python id="v2kq9m"
# =========================
# زیرمجموعه گیری
# =========================

async def referral(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    bot = await context.bot.get_me()

    link = f"https://t.me/{bot.username}?start={user_id}"

    await update.message.reply_text(
        f"""
👥 لینک زیرمجموعه گیری شما

{link}

به ازای هر خرید زیرمجموعه پورسانت میگیرید 😎
        """
    )

# =========================
# لغو
# =========================

async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "عملیات لغو شد ❌",
        reply_markup=main_keyboard
    )

    return ConversationHandler.END

# =========================
# دکمه ها
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    if text == "📈 ثبت ویو":

        return await view_start(
            update,
            context
        )

    elif text == "💰 موجودی پنل":

        await amount(
            update,
            context
        )

    elif text == "👤 حساب من":

        await my_account(
            update,
            context
        )

    elif text == "💳 افزایش موجودی":

        await increase_balance(
            update,
            context
        )

    elif text == "📜 سفارش های من":

        await my_orders(
            update,
            context
        )

    elif text == "📊 آمار":

        await stats(
            update,
            context
        )

    elif text == "📋 سفارش ها":

        await orders_list(
            update,
            context
        )

    elif text == "⬅️ بازگشت":

        await start(
            update,
            context
        )

# =========================
# اجرای ربات
# =========================

app = ApplicationBuilder().token(
    BOT_TOKEN
).build()

# =========================
# کانورسیشن
# =========================

conv_handler = ConversationHandler(

    entry_points=[

        MessageHandler(
            filters.Regex("^📈 ثبت ویو$"),
            view_start
        )
    ],

    states={

        LINK: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_link
            )
        ],

        COUNT: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_count
            )
        ],
    },

    fallbacks=[

        MessageHandler(
            filters.Regex("^❌ لغو$"),
            cancel
        )
    ],
)

# =========================
# هندلر ها
# =========================

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CommandHandler(
        "admin",
        admin
    )
)

app.add_handler(
    CommandHandler(
        "ban",
        ban
    )
)

app.add_handler(
    CommandHandler(
        "unban",
        unban
    )
)

app.add_handler(
    CommandHandler(
        "addbalance",
        addbalance
    )
)

app.add_handler(
    CommandHandler(
        "broadcast",
        broadcast
    )
)

app.add_handler(
    CommandHandler(
        "discount",
        add_discount
    )
)

app.add_handler(
    CommandHandler(
        "ref",
        referral
    )
)

app.add_handler(
    conv_handler
)

app.add_handler(

    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        button_handler
    )
)

print("Bot started...")

app.run_polling()
```
