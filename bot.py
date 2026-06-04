from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
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

    # انتخاب سرویس
    if context.user_data.get("waiting_service"):

        if text not in SERVICES:

            await update.message.reply_text(
                "❌ سرویس معتبر نیست."
            )

            return

        context.user_data["service"] = text

        context.user_data["waiting_service"] = False
        context.user_data["waiting_link"] = True

        await update.message.reply_text(
            "🔗 لینک پست را ارسال کنید."
        )

        return

    # دریافت مبلغ شارژ
    if context.user_data.get("waiting_charge_amount"):

        if text.isdigit():

            amount = int(text)

            if amount < MIN_CHARGE:

                await update.message.reply_text(
                    f"حداقل شارژ {MIN_CHARGE:,} تومان است."
                )

                return

            fee = int(
                amount * CHARGE_FEE_PERCENT / 100
            )

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

        else:

            await update.message.reply_text(
                "❌ فقط عدد وارد کنید."
            )

            return

    # حساب من
    if text == "👤 حساب من":

        await my_account(update, context)

    # افزایش موجودی
    elif text == "💰 افزایش موجودی":

        await increase_balance(update, context)

    # سفارش بازدید
    elif text == "📈 سفارش بازدید":

        await update.message.reply_text(
            """
سرویس مورد نظر را انتخاب کنید:

بازدید ارزان
بازدید دقیق
بازدید فیک
بازدید تبلیغاتی

نام سرویس را ارسال کنید.
            """
        )

        context.user_data["waiting_service"] = True

    # سفارش خودکار
    elif text == "🤖 سفارش بازدید خودکار":

        await update.message.reply_text(
            "🚧 این بخش هنوز فعال نشده است."
        )

    # انتقال سکه
    elif text == "💸 انتقال سکه":

        await update.message.reply_text(
            "🚧 این بخش هنوز فعال نشده است."
        )

    # سفارشات فعال
    elif text == "📦 سفارشات فعال":

        await update.message.reply_text(
            "🚧 هنوز سفارشی ثبت نشده است."
        )

    # خریدهای من
    elif text == "📜 خرید های من":

        await update.message.reply_text(
            "🚧 هنوز خریدی ثبت نشده است."
        )

    # تعرفه محصولات
    elif text == "💰 تعرفه محصولات":

        await update.message.reply_text(
            """
💰 تعرفه محصولات به شرح زیر میباشد 👇

💬 بازدید ارزان #آنی : 600
⚡️ پنل اختصاصی دقیق #آنی 👀 : 750
🇺🇸 بازدید فیک #آنی : 800
📊 بازدید مخصوص تبلیغات در کانال (با لینک) : 850

━━━━━━━━━━━━━━

❤️ ریکشن : 10000
📊 نظرسنجی : 25000
👍 لایک : 24000

━━━━━━━━━━━━━━

💡 قیمت‌های فوق برای هر 1000 عدد می‌باشد.
            """
        )

    # پشتیبانی
    elif text == "🛠 پشتیبانی":

        await update.message.reply_text(
            "📩 برای پشتیبانی به ادمین پیام دهید."
        )
        
# =========================
# دریافت رسید
# =========================

async def receipt_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not context.user_data.get("waiting_receipt"):
        return

    photo = update.message.photo[-1].file_id

    amount = context.user_data.get(
        "charge_amount",
        0
    )

    user_id = update.effective_user.id

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ تایید",
                    callback_data=f"accept_{user_id}_{amount}"
                ),

                InlineKeyboardButton(
                    "❌ رد",
                    callback_data=f"reject_{user_id}"
                )
            ]
        ]
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=f"""
💳 درخواست شارژ جدید

👤 کاربر:
{user_id}

💰 مبلغ:
{amount:,} تومان
        """,
        reply_markup=keyboard
    )

    await update.message.reply_text(
        "✅ رسید شما ارسال شد."
    )

    context.user_data["waiting_receipt"] = False


# =========================
# تایید یا رد شارژ
# =========================

async def admin_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    if data.startswith("accept_"):

        parts = data.split("_")

        user_id = int(parts[1])

        amount = int(parts[2])

        change_balance(
            user_id,
            amount
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=f"""
✅ شارژ شما تایید شد

💰 مبلغ:
{amount:,} تومان

به موجودی شما اضافه شد.
            """
        )

        await query.edit_message_caption(
            caption="✅ شارژ تایید شد"
        )

    elif data.startswith("reject_"):

        user_id = int(
            data.split("_")[1]
        )

        await context.bot.send_message(
            chat_id=user_id,
            text="""
❌ رسید شما رد شد

لطفاً دوباره رسید صحیح ارسال کنید.
            """
        )

        await query.edit_message_caption(
            caption="❌ شارژ رد شد"
        )

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

app.add_handler(
    MessageHandler(
        filters.PHOTO,
        receipt_handler
    )
)

app.add_handler(
    CallbackQueryHandler(
        admin_callback
    )
)

print("Bot Started...")

app.run_polling()
