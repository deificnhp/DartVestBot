from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus
from config import CHANNEL_1, CHANNEL_2, REQUIRED_REFERRALS, ADMIN_IDS
from keyboards import membership_keyboard, main_keyboard, admin_keyboard
from config import CHANNEL_1, CHANNEL_2, REQUIRED_REFERRALS
from database import (
    get_user, add_user, update_user_membership, update_user_info,
    add_referral, mark_referral_valid, increase_referrals_count,
    get_valid_referrals_count, set_eligible
)
from messages import (
    MSG_NOT_MEMBER, MSG_MEMBERSHIP_SUCCESS,
    MSG_ALREADY_REGISTERED, MSG_NEED_MEMBERSHIP_FIRST,
    MSG_REFERRAL_LINK, MSG_PRIZES,
    get_referral_link, format_status
)
from keyboards import membership_keyboard, main_keyboard

async def check_membership(bot, user_id: int) -> tuple[bool, bool]:
    """وضعیت عضویت کاربر در دو کانال را چک می‌کند"""
    try:
        member1 = await bot.get_chat_member(chat_id=CHANNEL_1, user_id=user_id)
        is_member1 = member1.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ]
    except Exception:
        is_member1 = False

    try:
        member2 = await bot.get_chat_member(chat_id=CHANNEL_2, user_id=user_id)
        is_member2 = member2.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ]
    except Exception:
        is_member2 = False

    return is_member1, is_member2

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username
    full_name = user.full_name

    # پردازش deep link (رفرال)
    referred_by = None
    if context.args:
        try:
            referred_by = int(context.args[0])
            if referred_by == user_id:
                referred_by = None
        except (ValueError, TypeError):
            referred_by = None

    existing_user = get_user(user_id)

    if existing_user:
        update_user_info(user_id, username=username, full_name=full_name)
    else:
        # کاربر جدید
        add_user(
            telegram_id=user_id,
            username=username,
            full_name=full_name,
            referred_by=referred_by
        )
        if referred_by:
            add_referral(referrer_id=referred_by, referred_id=user_id)

    # چک عضویت
    is_member1, is_member2 = await check_membership(context.bot, user_id)
    update_user_membership(user_id, channel1=is_member1, channel2=is_member2)

    if is_member1 and is_member2:
        # عضو هر دو کانال هست → مستقیم لینک بده
        await process_successful_membership(update, context, user_id, is_new=not existing_user)
    else:
        # عضو نیست → فقط پیام کوتاه + دکمه‌های عضویت
        await update.message.reply_text(
            MSG_NOT_MEMBER,
            reply_markup=membership_keyboard(is_member1, is_member2)
        )

async def process_successful_membership(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, is_new: bool = False):
    """بعد از تأیید عضویت کامل اجرا می‌شود"""
    
    # اگر این کاربر از طریق رفرال آمده، رفرال را معتبر کن
    referrer_id = mark_referral_valid(user_id)
    if referrer_id:
        increase_referrals_count(referrer_id)
        count = get_valid_referrals_count(referrer_id)
        if count >= REQUIRED_REFERRALS:
            set_eligible(referrer_id, True)
            try:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text="🎉 تبریک! شما با تکمیل ۳ رفرال معتبر، وارد لیست قرعه‌کشی شدید."
                )
            except Exception:
                pass

    referral_link = get_referral_link(user_id)

    if is_new or not get_user(user_id).get("is_member_channel1"):
        # اولین بار که عضویت تأیید می‌شود
        text = MSG_MEMBERSHIP_SUCCESS.format(referral_link=referral_link)
    else:
        # قبلاً عضو بوده
        text = MSG_ALREADY_REGISTERED.format(referral_link=referral_link)

    if update.callback_query:
        await update.callback_query.edit_message_text(text)
        await update.callback_query.message.reply_text(
            "از دکمه‌های زیر استفاده کنید:",
            reply_markup=main_keyboard(user_id)
        )
    else:
        await update.message.reply_text(text, reply_markup=main_keyboard(user_id))

async def check_membership_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    is_member1, is_member2 = await check_membership(context.bot, user_id)
    update_user_membership(user_id, channel1=is_member1, channel2=is_member2)

    if is_member1 and is_member2:
        await process_successful_membership(update, context, user_id, is_new=True)
    else:
        missing = []
        if not is_member1:
            missing.append("Daxvision")
        if not is_member2:
            missing.append("DartVestCh")
        
        await query.edit_message_text(
            f"❌ هنوز عضو کانال‌های زیر نیستید:\n" + "\n".join(f"• {m}" for m in missing) + 
            "\n\nلطفاً عضو شوید و دوباره بررسی کنید.",
            reply_markup=membership_keyboard(is_member1, is_member2)
        )

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not user:
        await update.message.reply_text("ابتدا باید با دستور /start ثبت‌نام کنید.")
        return

    is_member1, is_member2 = await check_membership(context.bot, user_id)
    
    if not (is_member1 and is_member2):
        await update.message.reply_text(
            MSG_NEED_MEMBERSHIP_FIRST,
            reply_markup=membership_keyboard(is_member1, is_member2)
        )
        return

    count = get_valid_referrals_count(user_id)
    is_eligible = bool(user["is_eligible"]) or count >= REQUIRED_REFERRALS
    
    if count >= REQUIRED_REFERRALS and not user["is_eligible"]:
        set_eligible(user_id, True)
        is_eligible = True

    referral_link = get_referral_link(user_id)
    text = format_status(count, is_eligible, referral_link)
    await update.message.reply_text(text)

async def my_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not user:
        await update.message.reply_text("ابتدا باید با دستور /start ثبت‌نام کنید.")
        return

    is_member1, is_member2 = await check_membership(context.bot, user_id)
    
    if not (is_member1 and is_member2):
        await update.message.reply_text(
            MSG_NEED_MEMBERSHIP_FIRST,
            reply_markup=membership_keyboard(is_member1, is_member2)
        )
        return

    referral_link = get_referral_link(user_id)
    await update.message.reply_text(
        MSG_REFERRAL_LINK.format(referral_link=referral_link)
    )

async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ دسترسی ندارید.")
        return

    await update.message.reply_text(
        "🛠 پنل مدیریت\n\nیکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=admin_keyboard()
    )

async def prizes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MSG_PRIZES)