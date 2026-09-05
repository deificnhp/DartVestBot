import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

DB_NAME = "dart_vest.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            referred_by INTEGER,
            referrals_count INTEGER DEFAULT 0,
            is_eligible INTEGER DEFAULT 0,
            is_member_channel1 INTEGER DEFAULT 0,
            is_member_channel2 INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_id INTEGER UNIQUE,
            created_at TEXT,
            is_valid INTEGER DEFAULT 0,
            FOREIGN KEY (referrer_id) REFERENCES users (telegram_id),
            FOREIGN KEY (referred_id) REFERENCES users (telegram_id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ دیتابیس با موفقیت ساخته شد.")

# ==================== مدیریت کاربر ====================

def get_user(telegram_id: int) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_user(telegram_id: int, username: str = None, full_name: str = None, referred_by: int = None) -> bool:
    """کاربر جدید را اضافه می‌کند. اگر قبلاً وجود داشته باشد False برمی‌گرداند."""
    if get_user(telegram_id):
        return False

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (telegram_id, username, full_name, referred_by, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (telegram_id, username, full_name, referred_by, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True

def update_user_membership(telegram_id: int, channel1: bool = None, channel2: bool = None):
    """وضعیت عضویت کاربر در کانال‌ها را آپدیت می‌کند."""
    conn = get_connection()
    cursor = conn.cursor()

    if channel1 is not None:
        cursor.execute(
            "UPDATE users SET is_member_channel1 = ? WHERE telegram_id = ?",
            (1 if channel1 else 0, telegram_id)
        )
    if channel2 is not None:
        cursor.execute(
            "UPDATE users SET is_member_channel2 = ? WHERE telegram_id = ?",
            (1 if channel2 else 0, telegram_id)
        )

    conn.commit()
    conn.close()

def update_user_info(telegram_id: int, username: str = None, full_name: str = None):
    """آپدیت یوزرنیم و نام کامل کاربر"""
    conn = get_connection()
    cursor = conn.cursor()
    if username is not None:
        cursor.execute("UPDATE users SET username = ? WHERE telegram_id = ?", (username, telegram_id))
    if full_name is not None:
        cursor.execute("UPDATE users SET full_name = ? WHERE telegram_id = ?", (full_name, telegram_id))
    conn.commit()
    conn.close()

def set_eligible(telegram_id: int, status: bool = True):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET is_eligible = ? WHERE telegram_id = ?",
        (1 if status else 0, telegram_id)
    )
    conn.commit()
    conn.close()

def increase_referrals_count(telegram_id: int):
    """تعداد رفرال معتبر کاربر را یکی افزایش می‌دهد"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET referrals_count = referrals_count + 1 WHERE telegram_id = ?",
        (telegram_id,)
    )
    conn.commit()
    conn.close()

# ==================== مدیریت رفرال ====================

def add_referral(referrer_id: int, referred_id: int) -> bool:
    """
    یک رفرال جدید ثبت می‌کند.
    اگر referred_id قبلاً ثبت شده باشد یا referrer_id == referred_id باشد False برمی‌گرداند.
    """
    if referrer_id == referred_id:
        return False

    # چک کردن اینکه قبلاً ثبت نشده باشد
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM referrals WHERE referred_id = ?", (referred_id,))
    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute("""
        INSERT INTO referrals (referrer_id, referred_id, created_at, is_valid)
        VALUES (?, ?, ?, 0)
    """, (referrer_id, referred_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True

def mark_referral_valid(referred_id: int) -> Optional[int]:
    """
    رفرال مربوط به referred_id را معتبر می‌کند و referrer_id را برمی‌گرداند.
    اگر رفرال پیدا نشود یا قبلاً معتبر باشد None برمی‌گرداند.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT referrer_id, is_valid FROM referrals WHERE referred_id = ?",
        (referred_id,)
    )
    row = cursor.fetchone()

    if not row or row["is_valid"] == 1:
        conn.close()
        return None

    referrer_id = row["referrer_id"]

    cursor.execute(
        "UPDATE referrals SET is_valid = 1 WHERE referred_id = ?",
        (referred_id,)
    )
    conn.commit()
    conn.close()
    return referrer_id

def get_valid_referrals_count(telegram_id: int) -> int:
    """تعداد رفرال‌های معتبر یک کاربر را برمی‌گرداند"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) as count FROM referrals WHERE referrer_id = ? AND is_valid = 1",
        (telegram_id,)
    )
    count = cursor.fetchone()["count"]
    conn.close()
    return count

def get_user_referrals(telegram_id: int) -> List[Dict]:
    """لیست تمام رفرال‌های یک کاربر را برمی‌گرداند"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, u.username, u.full_name
        FROM referrals r
        LEFT JOIN users u ON r.referred_id = u.telegram_id
        WHERE r.referrer_id = ?
        ORDER BY r.created_at DESC
    """, (telegram_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ==================== آمار و ادمین ====================

def get_stats() -> Dict:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    total_users = cursor.fetchone()["total_users"]

    cursor.execute("SELECT COUNT(*) as eligible_users FROM users WHERE is_eligible = 1")
    eligible_users = cursor.fetchone()["eligible_users"]

    cursor.execute("SELECT COUNT(*) as total_referrals FROM referrals WHERE is_valid = 1")
    total_referrals = cursor.fetchone()["total_referrals"]

    cursor.execute("SELECT COUNT(*) as pending_referrals FROM referrals WHERE is_valid = 0")
    pending_referrals = cursor.fetchone()["pending_referrals"]

    conn.close()

    return {
        "total_users": total_users,
        "eligible_users": eligible_users,
        "total_referrals": total_referrals,
        "pending_referrals": pending_referrals
    }

def get_eligible_users() -> List[Dict]:
    """لیست تمام کاربران واجد شرایط را برمی‌گرداند"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT telegram_id, username, full_name, referrals_count, created_at
        FROM users
        WHERE is_eligible = 1
        ORDER BY created_at ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_users() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]