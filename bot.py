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

async def buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    # دریافت مبلغ شارژ
    if context.user_data.get("waiting_charge_amount"):

        if text.isdigit():

            amount = int(text)

            if amount < MIN_CHARGE:

                await update.message.reply_text(
                    f"حداقل شارژ {MIN_CHARGE:,} تومان است."
                )

                return

            fee = int(amount * CHARGE_FEE_PERCENT / 100)

            total_amount = amount + fee

            context.user_data["charge_amount"] = amount
            context.user_data["waiting_charge_amount"] = False
            context.user_data["waiting_receipt"] = True

            await update.message.reply_text(
                f"""
💳 اطلاعات پرداخت

👤 صاحب کارت:
{CARD_OWNER}

💳 شماره کارت:
{CARD_NUMBER}

━━━━━━━━━━━━━━

💰 مبلغ درخواستی:
{amount:,} تومان

📈 کارمزد:
{fee:,} تومان

💵 مبلغ قابل پرداخت:
{total_amount:,} تومان

📸 پس از واریز عکس رسید را ارسال کنید.
                """
            )

            return

    # دکمه حساب من
    if text == "👤 حساب من":
        await my_account(update, context)

    # دکمه افزایش موجودی
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
