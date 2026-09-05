from telegram import ReplyKeyboardMarkup, KeyboardButton
from config import CHANNEL_1, CHANNEL_2, ADMIN_IDS

def membership_keyboard(is_member1: bool = False, is_member2: bool = False):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = []

    join_buttons = []
    if not is_member1:
        join_buttons.append(
            InlineKeyboardButton("📢 عضویت در Daxvision", url=f"https://t.me/{CHANNEL_1.replace('@', '')}")
        )
    if not is_member2:
        join_buttons.append(
            InlineKeyboardButton("📢 عضویت در DartVestCh", url=f"https://t.me/{CHANNEL_2.replace('@', '')}")
        )

    if join_buttons:
        if len(join_buttons) == 2:
            keyboard.append(join_buttons)
        else:
            keyboard.append(join_buttons)

    keyboard.append([
        InlineKeyboardButton("✅ عضو شدم، بررسی کن", callback_data="check_membership")
    ])

    return InlineKeyboardMarkup(keyboard)

def main_keyboard(user_id: int = None) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("🎁 جوایز"), KeyboardButton("📊 وضعیت من")],
        [KeyboardButton("🔗 لینک من")]
    ]

    if user_id and user_id in ADMIN_IDS:
        keyboard.append([KeyboardButton("🛠 Admin")])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("📊 آمار"), KeyboardButton("🎯 واجدین شرایط")],
        [KeyboardButton("🎲 قرعه‌کشی"), KeyboardButton("📢 اعلام نتایج")],
        [KeyboardButton("🔴 خاموش کردن ربات")],
        [KeyboardButton("🔙 بازگشت")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)