from config import REQUIRED_REFERRALS, BOT_USERNAME

MSG_PRIZES = """سلام و خوش اومدی به Dart Vest Bot 👋

اینجا قراره در کنار کامیونیتی تریدینگ Dart Vest، در کمپین رفرال هم شرکت کنی و شانس ورود به قرعه‌کشی رو به دست بیاری. 🎯

🎁 جایزه کمپین: ده حساب Prop با سرمایه $1,000 از سرمایه‌گذاربرتر (SGB) برای برندگان قرعه‌کشی

با دعوت از دوستانت و تکمیل ۳ رفرال معتبر، وارد لیست قرعه‌کشی می‌شی.

موفق باشی. 📈"""


MSG_NOT_MEMBER = """برای استفاده از ربات، ابتدا باید در هر دو کانال زیر عضو شوید:"""

MSG_MEMBERSHIP_SUCCESS = """عضویت شما تأیید شد. ✅

🔗 لینک اختصاصی رفرال شما:
{referral_link}

با دعوت ۳ نفر، وارد قرعه‌کشی می‌شوید."""

MSG_ALREADY_REGISTERED = """لینک رفرال شما:

{referral_link}"""

MSG_STATUS = """📊 وضعیت شما در Dart Vest

👤 رفرال‌های موفق: {referral_count}/{required}
🎯 وضعیت قرعه‌کشی: {eligibility_status}

🔗 لینک رفرال:
{referral_link}

{status_message}"""

MSG_NEED_MEMBERSHIP_FIRST = "ابتدا باید در هر دو کانال عضو شوید."

MSG_REFERRAL_LINK = """🔗 لینک اختصاصی رفرال شما:

{referral_link}"""

def get_referral_link(user_id: int) -> str:
    return f"https://t.me/{BOT_USERNAME}?start={user_id}"

def format_status(referral_count: int, is_eligible: bool, referral_link: str) -> str:
    eligibility_status = "✅ واجد شرایط قرعه‌کشی" if is_eligible else "❌ هنوز واجد شرایط نیستید"
    
    if is_eligible:
        status_message = "🎉 تبریک! شما با موفقیت وارد لیست قرعه‌کشی شدید."
    elif referral_count >= REQUIRED_REFERRALS:
        status_message = "در حال بررسی نهایی..."
    else:
        remaining = REQUIRED_REFERRALS - referral_count
        status_message = f"برای ورود به قرعه‌کشی به {remaining} رفرال معتبر دیگر نیاز دارید."

    return MSG_STATUS.format(
        referral_count=referral_count,
        required=REQUIRED_REFERRALS,
        eligibility_status=eligibility_status,
        referral_link=referral_link,
        status_message=status_message
    )



MSG_ADMIN_ONLY = "⛔ این بخش فقط برای ادمین قابل دسترسی است."

MSG_STATS = """📊 آمار Dart Vest

👥 کاربران ثبت‌نام‌شده: {total_users}
🎯 کاربران واجد شرایط: {eligible_users}
🔗 رفرال‌های موفق: {total_referrals}
⏳ رفرال‌های در انتظار: {pending_referrals}"""

MSG_NO_ELIGIBLE = "در حال حاضر هیچ کاربری واجد شرایط شرکت در قرعه‌کشی نیست. 🎯"

MSG_ELIGIBLE_LIST_HEADER = "🎯 لیست کاربران واجد شرایط قرعه‌کشی"

MSG_DRAW_USAGE = """🎲 راهنمای قرعه‌کشی

برای انتخاب برندگان، تعداد برندگان را بعد از دستور /draw وارد کنید.

مثال:
/draw 1"""

MSG_DRAW_INVALID = """⚠️ تعداد برندگان نامعتبر است.

لطفاً یک عدد صحیح و بزرگ‌تر از صفر وارد کنید.

مثال:
/draw 1"""

MSG_DRAW_SUCCESS = """🎉 قرعه‌کشی با موفقیت انجام شد.

تعداد برندگان: {winner_count}

🏆 برندگان:
{winners}

برای اعلام عمومی نتایج، از دستور /announce استفاده کنید."""

MSG_ANNOUNCE_NO_WINNERS = """⚠️ هنوز هیچ قرعه‌کشی‌ای انجام نشده یا برنده‌ای برای اعلام وجود ندارد.

ابتدا با استفاده از دستور /draw برندگان را انتخاب کنید."""

MSG_ANNOUNCE_PUBLIC = """🎉 نتایج قرعه‌کشی Dart Vest اعلام شد!

از تمام افرادی که در کمپین Referral همراه ما بودند، ممنونیم. 🤝

🏆 برندگان:
{winners}

🎁 جایزه این کمپین:
یک حساب Prop با سرمایه $1,000 از SGB

به برندگان تبریک می‌گوییم و برایشان در مسیر ترید آرزوی موفقیت داریم. 📈"""

MSG_ANNOUNCE_PRIVATE = """🎉 تبریک! شما یکی از برندگان قرعه‌کشی Dart Vest هستید. 🏆

🎁 جایزه شما:
حساب Prop با سرمایه $1,000 از SGB

برای دریافت جایزه، لطفاً مراحل اعلام‌شده توسط تیم Dart Vest را دنبال کنید.

موفق باشید و امیدواریم این جایزه شروع خوبی برای مسیر ترید شما باشد. 📈"""

MSG_SHUTDOWN = """🔴 ربات Dart Vest در حال خاموش شدن است.

لطفاً تا راه‌اندازی مجدد ربات، کمی صبر کنید."""
