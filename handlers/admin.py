import random
from telegram import Update
from telegram.ext import ContextTypes

from keyboards import admin_keyboard, main_keyboard
from config import ADMIN_IDS
from config import ADMIN_IDS
from database import get_stats, get_eligible_users, get_all_users
from messages import (
    MSG_ADMIN_ONLY, MSG_STATS, MSG_NO_ELIGIBLE,
    MSG_ELIGIBLE_LIST_HEADER, MSG_DRAW_USAGE, MSG_DRAW_INVALID,
    MSG_DRAW_SUCCESS, MSG_ANNOUNCE_NO_WINNERS,
    MSG_ANNOUNCE_PUBLIC, MSG_ANNOUNCE_PRIVATE, MSG_SHUTDOWN
)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MSG_ADMIN_ONLY)
        return

    stats = get_stats()
    text = MSG_STATS.format(**stats)
    await update.message.reply_text(text)

async def eligible_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MSG_ADMIN_ONLY)
        return

    users = get_eligible_users()

    if not users:
        await update.message.reply_text(MSG_NO_ELIGIBLE)
        return

    text = MSG_ELIGIBLE_LIST_HEADER + "\n\n"
    for i, user in enumerate(users, 1):
        name = user["full_name"] or "بدون نام"
        username = f"@{user['username']}" if user["username"] else "بدون یوزرنیم"
        text += f"{i}. {name} ({username})\n"
        text += f"   آیدی: `{user['telegram_id']}` | رفرال: {user['referrals_count']}\n\n"

    # اگر لیست خیلی طولانی شد، تلگرام ممکنه قطع کنه (حداکثر حدود ۴۰۹۶ کاراکتر)
    if len(text) > 4000:
        text = text[:3900] + "\n\n... (لیست طولانی بود و کوتاه شد)"

    await update.message.reply_text(text, parse_mode="Markdown")

async def draw_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MSG_ADMIN_ONLY)
        return

    if not context.args:
        await update.message.reply_text(MSG_DRAW_USAGE)
        return

    try:
        n = int(context.args[0])
        if n <= 0:
            raise ValueError
    except (ValueError, TypeError):
        await update.message.reply_text(MSG_DRAW_INVALID)
        return

    eligible = get_eligible_users()

    if not eligible:
        await update.message.reply_text(MSG_NO_ELIGIBLE)
        return

    if n > len(eligible):
        n = len(eligible)

    winners = random.sample(eligible, n)

    # ذخیره برندگان در bot_data برای استفاده در /announce
    context.bot_data["winners"] = winners

    winners_text = ""
    for i, w in enumerate(winners, 1):
        name = w["full_name"] or "بدون نام"
        username = f"@{w['username']}" if w["username"] else "بدون یوزرنیم"
        winners_text += f"{i}. {name} ({username}) - `{w['telegram_id']}`\n"

    text = MSG_DRAW_SUCCESS.format(
        winner_count=n,
        winners=winners_text
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def announce_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MSG_ADMIN_ONLY)
        return

    winners = context.bot_data.get("winners")

    if not winners:
        await update.message.reply_text(MSG_ANNOUNCE_NO_WINNERS)
        return

    # ساخت متن لیست برندگان
    winners_text = ""
    for i, w in enumerate(winners, 1):
        name = w["full_name"] or "بدون نام"
        username = f"@{w['username']}" if w["username"] else ""
        winners_text += f"{i}. {name} {username}\n"

    public_text = MSG_ANNOUNCE_PUBLIC.format(winners=winners_text)

    # ارسال پیام خصوصی به برندگان
    for w in winners:
        try:
            await context.bot.send_message(
                chat_id=w["telegram_id"],
                text=MSG_ANNOUNCE_PRIVATE
            )
        except Exception:
            pass  # اگر کاربر ربات رو بلاک کرده باشه

    # ارسال پیام عمومی به همه کاربران
    all_users = get_all_users()
    success = 0
    fail = 0

    await update.message.reply_text("در حال ارسال پیام اعلام نتایج به کاربران...")

    for user in all_users:
        try:
            await context.bot.send_message(
                chat_id=user["telegram_id"],
                text=public_text
            )
            success += 1
        except Exception:
            fail += 1

    await update.message.reply_text(
        f"✅ اعلام نتایج انجام شد.\n"
        f"ارسال موفق: {success}\n"
        f"ناموفق: {fail}"
    )

async def admin_stats_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    stats = get_stats()
    text = MSG_STATS.format(**stats)
    await update.message.reply_text(text)

async def admin_eligible_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    users = get_eligible_users()
    if not users:
        await update.message.reply_text(MSG_NO_ELIGIBLE)
        return

    text = MSG_ELIGIBLE_LIST_HEADER + "\n\n"
    for i, user in enumerate(users, 1):
        name = user["full_name"] or "بدون نام"
        username = f"@{user['username']}" if user["username"] else "بدون یوزرنیم"
        text += f"{i}. {name} ({username})\n"
        text += f"   آیدی: `{user['telegram_id']}` | رفرال: {user['referrals_count']}\n\n"

    if len(text) > 4000:
        text = text[:3900] + "\n\n... (لیست طولانی بود)"

    await update.message.reply_text(text, parse_mode="Markdown")

async def admin_draw_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    await update.message.reply_text(MSG_DRAW_USAGE)

async def admin_announce_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    # از همان منطق قبلی announce استفاده می‌کنیم
    await announce_handler(update, context)

async def admin_shutdown_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    await shutdown_handler(update, context)

async def back_to_main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        "به منوی اصلی بازگشتید.",
        reply_markup=main_keyboard(user_id)
    )

async def shutdown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(MSG_ADMIN_ONLY)
        return

    await update.message.reply_text(MSG_SHUTDOWN)
    
    # خاموش کردن ربات
    context.application.stop_running()