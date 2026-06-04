import sqlite3
from datetime import datetime

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =========================
# کاربران
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    banned INTEGER DEFAULT 0,
    register_date TEXT
)
""")

# =========================
# سفارشات
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    service TEXT,

    link TEXT,

    quantity INTEGER,

    price INTEGER,

    status TEXT,

    created_at TEXT

)
""")

conn.commit()

# =========================
# افزودن کاربر
# =========================

def add_user(user_id):

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:

        cursor.execute(
            """
            INSERT INTO users(
                user_id,
                register_date
            )
            VALUES(
                ?,
                ?
            )
            """,
            (
                user_id,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )

        conn.commit()

# =========================
# دریافت موجودی
# =========================

def get_balance(user_id):

    cursor.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    return 0

# =========================
# تغییر موجودی
# =========================

def change_balance(
    user_id,
    amount
):

    current_balance = get_balance(user_id)

    new_balance = current_balance + amount

    cursor.execute(
        """
        UPDATE users
        SET balance=?
        WHERE user_id=?
        """,
        (
            new_balance,
            user_id
        )
    )

    conn.commit()

# =========================
# بن کاربر
# =========================

def ban_user(user_id):

    cursor.execute(
        """
        UPDATE users
        SET banned=1
        WHERE user_id=?
        """,
        (user_id,)
    )

    conn.commit()

# =========================
# آنبن کاربر
# =========================

def unban_user(user_id):

    cursor.execute(
        """
        UPDATE users
        SET banned=0
        WHERE user_id=?
        """,
        (user_id,)
    )

    conn.commit()

# =========================
# وضعیت بن
# =========================

def is_banned(user_id):

    cursor.execute(
        """
        SELECT banned
        FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    if result:
        return result[0] == 1

    return False

# =========================
# ثبت سفارش
# =========================

def add_order(
    user_id,
    service,
    link,
    quantity,
    price
):

    cursor.execute(
        """
        INSERT INTO orders(

            user_id,
            service,
            link,
            quantity,
            price,
            status,
            created_at

        )
        VALUES(
            ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            user_id,
            service,
            link,
            quantity,
            price,
            "درحال انجام",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )

    conn.commit()

# =========================
# سفارشات کاربر
# =========================

def get_user_orders(user_id):

    cursor.execute(
        """
        SELECT
            id,
            service,
            quantity,
            price,
            status
        FROM orders
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    return cursor.fetchall()

# =========================
# سفارشات فعال
# =========================

def get_active_orders(user_id):

    cursor.execute(
        """
        SELECT
            id,
            service,
            quantity,
            status
        FROM orders
        WHERE user_id=?
        AND status='درحال انجام'
        ORDER BY id DESC
        """,
        (user_id,)
    )

    return cursor.fetchall()

# =========================
# تغییر وضعیت سفارش
# =========================

def update_order_status(
    order_id,
    status
):

    cursor.execute(
        """
        UPDATE orders
        SET status=?
        WHERE id=?
        """,
        (
            status,
            order_id
        )
    )

    conn.commit()
