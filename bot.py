import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from database import init_db
from handlers.start import (
    start_handler,
    check_membership_callback,
    status_handler,
    my_link_handler,
    prizes_handler,
    admin_button_handler,
)
from handlers.admin import (
    stats_handler,
    eligible_handler,
    draw_handler,
    announce_handler,
    shutdown_handler,
    admin_stats_button,
    admin_eligible_button,
    admin_draw_button,
    admin_announce_button,
    admin_shutdown_button,
    back_to_main_handler,
)

# تنظیم لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        # لاگ‌های اضافی سرور health را چاپ نکن
        pass


def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"Health server started on port {port}")
    server.serve_forever()


def main():
    # ساخت دیتابیس
    init_db()

    # ساخت اپلیکیشن
    application = Application.builder().token(BOT_TOKEN).build()

    # دستورات کاربر
    application.add_handler(CommandHandler("start", start_handler))

    # دکمه‌های شیشه‌ای
    application.add_handler(
        CallbackQueryHandler(check_membership_callback, pattern="^check_membership$")
    )

    # دکمه‌های کیبورد کاربر
    application.add_handler(MessageHandler(filters.Regex("^📊 وضعیت من$"), status_handler))
    application.add_handler(MessageHandler(filters.Regex("^🔗 لینک من$"), my_link_handler))
    application.add_handler(MessageHandler(filters.Regex("^🎁 جوایز$"), prizes_handler))
    application.add_handler(MessageHandler(filters.Regex("^🛠 Admin$"), admin_button_handler))

    # دکمه‌های پنل ادمین
    application.add_handler(MessageHandler(filters.Regex("^📊 آمار$"), admin_stats_button))
    application.add_handler(MessageHandler(filters.Regex("^🎯 واجدین شرایط$"), admin_eligible_button))
    application.add_handler(MessageHandler(filters.Regex("^🎲 قرعه‌کشی$"), admin_draw_button))
    application.add_handler(MessageHandler(filters.Regex("^📢 اعلام نتایج$"), admin_announce_button))
    application.add_handler(MessageHandler(filters.Regex("^🔴 خاموش کردن ربات$"), admin_shutdown_button))
    application.add_handler(MessageHandler(filters.Regex("^🔙 بازگشت$"), back_to_main_handler))

    # دستورات متنی ادمین (برای سازگاری)
    application.add_handler(CommandHandler("stats", stats_handler))
    application.add_handler(CommandHandler("eligible", eligible_handler))
    application.add_handler(CommandHandler("draw", draw_handler))
    application.add_handler(CommandHandler("announce", announce_handler))
    application.add_handler(CommandHandler("shutdown", shutdown_handler))

    # راه‌اندازی سرور health در thread جدا
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    logger.info("🤖 ربات در حال راه‌اندازی...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
