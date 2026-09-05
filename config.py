import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
CHANNEL_1_USERNAME = os.getenv("CHANNEL_1_USERNAME")
CHANNEL_2_USERNAME = os.getenv("CHANNEL_2_USERNAME")
REQUIRED_REFERRALS = int(os.getenv("REQUIRED_REFERRALS", 3))
BOT_USERNAME = os.getenv("BOT_USERNAME")

# برای استفاده راحت‌تر در چک عضویت
CHANNEL_1 = f"@{CHANNEL_1_USERNAME}"
CHANNEL_2 = f"@{CHANNEL_2_USERNAME}"