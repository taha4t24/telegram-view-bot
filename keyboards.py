from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# =========================
# منوی اصلی کاربران
# =========================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["📈 سفارش بازدید", "🤖 سفارش بازدید خودکار"],

        ["👤 حساب من", "💰 افزایش موجودی"],

        ["💰 تعرفه محصولات", "💸 انتقال سکه"],

        ["📦 سفارشات فعال", "📜 خرید های من"],

        ["🛠 پشتیبانی"]
    ],
    resize_keyboard=True
)

# =========================
# پنل مدیریت
# =========================

admin_panel = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "📊 داشبورد",
                callback_data="dashboard"
            )
        ],

        [
            InlineKeyboardButton(
                "💳 موجودی API",
                callback_data="api_balance"
            ),

            InlineKeyboardButton(
                "📦 سفارش ها",
                callback_data="orders"
            )
        ],

        [
            InlineKeyboardButton(
                "👤 جستجوی کاربر",
                callback_data="search_user"
            ),

            InlineKeyboardButton(
                "➕ شارژ کاربر",
                callback_data="charge_user"
            )
        ],

        [
            InlineKeyboardButton(
                "🚫 بن کاربر",
                callback_data="ban_user"
            ),

            InlineKeyboardButton(
                "✅ آنبن کاربر",
                callback_data="unban_user"
            )
        ],

        [
            InlineKeyboardButton(
                "💰 سود امروز",
                callback_data="today_profit"
            ),

            InlineKeyboardButton(
                "💵 سود کل",
                callback_data="total_profit"
            )
        ],

        [
            InlineKeyboardButton(
                "📨 ارسال همگانی",
                callback_data="broadcast"
            )
        ]
    ]
)
