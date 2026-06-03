from telegram import Update

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from config import *
from database import *
from keyboards import *

# =========================
# استارت
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    add_user(user_id)

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
{balance:,} تومان
        """
    )

# =========================
# افزایش موجودی
# =========================

async def increase_balance(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    balance = get_balance(user_id)

    await update.message.reply_text(
        f"""
💰 موجودی کیف پول شما:

{balance:,} تومان

مبلغ مورد نظر برای شارژ را ارسال کنید.

حداقل شارژ:
{MIN_CHARGE:,} تومان
        """
    )

    context.user_data["waiting_charge_amount"] = True

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
        "👑 پنل مدیریت",
        reply_markup=admin_panel
    )

# =========================
# دکمه ها
# =========================

# =========================
# دکمه ها
# =========================

async def buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    await update.message.reply_text(
        f"DEBUG: {text}"
    )

    if text == "👤 حساب من":
        await my_account(update, context)

    elif text == "💰 افزایش موجودی":
        await increase_balance(update, context)

# =========================
# اجرای ربات
# =========================

app = ApplicationBuilder().token(
    BOT_TOKEN
).build()

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
    MessageHandler(
        filters.TEXT,
        buttons
    )
)

print("Bot Started...")

app.run_polling()
