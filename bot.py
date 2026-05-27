ffrom telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
import requests

# ===== تنظیمات =====
BOT_TOKEN = "8667603518:AAFxT66irkdxIzpcJVrKmS2XPIdwDI1acHc"
API_KEY = "x5PLaG2rO6KIMwz4"

# آیدی عددی خودت را بگذار
ALLOWED_USER_ID = 8019491735

BASE_URL = "https://api.power-tel.ir/apic.php"

LINK, COUNT = range(2)

# کیبورد اصلی
main_keyboard = ReplyKeyboardMarkup(
    [["📈 ثبت ویو", "💰 موجودی"],
     ["❌ لغو"]],
    resize_keyboard=True
)


def is_allowed(update):
    return update.effective_user.id == ALLOWED_USER_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await update.message.reply_text("دسترسی ندارید ❌")
        return

    await update.message.reply_text(
        "ربات روشنه ✅\nیکی از گزینه‌ها را انتخاب کن:",
        reply_markup=main_keyboard
    )


async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await update.message.reply_text("دسترسی ندارید ❌")
        return

    params = {"type": "amount", "apikey": API_KEY}
    r = requests.get(BASE_URL, params=params)
    data = r.json()

    await update.message.reply_text(
        f"💰 موجودی شما:\n{data['amount']}",
        reply_markup=main_keyboard
    )


async def view_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await update.message.reply_text("دسترسی ندارید ❌")
        return ConversationHandler.END

    await update.message.reply_text("لینک پست را بفرست:")
    return LINK


async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["link"] = update.message.text
    await update.message.reply_text("تعداد ویو را بفرست:")
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
            f"📢 کانال: {data['channel']}"
        )

        await update.message.reply_text(
            msg,
            reply_markup=main_keyboard
        )

    except:
        await update.message.reply_text(
            "خطا ❌ دوباره امتحان کن",
            reply_markup=main_keyboard
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "عملیات لغو شد ❌",
        reply_markup=main_keyboard
    )
    return ConversationHandler.END


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📈 ثبت ویو":
        return await view_start(update, context)

    elif text == "💰 موجودی":
        await amount(update, context)

    elif text == "❌ لغو":
        await cancel(update, context)


app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📈 ثبت ویو$"), view_start)],
    states={
        LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_link)],
        COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_count)],
    },
    fallbacks=[MessageHandler(filters.Regex("^❌ لغو$"), cancel)],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

print("Bot started...")
app.run_polling()