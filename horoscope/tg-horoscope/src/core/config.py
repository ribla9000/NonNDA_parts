import os
from dotenv import load_dotenv

load_dotenv(".env")


HOROSCOPE_BOT_TOKEN = os.getenv("ENV_HOROSCOPE_BOT_TOKEN")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
SENTRY_TOKEN = os.getenv("ENV_SENTRY_TOKEN")
WEBHOOK_URL = os.getenv("ENV_WEBHOOK_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT")
USERDATA_FOLDER = os.getenv("ENV_USERDATA_FOLDER")

BACK_BUTTON_TEXT = "«Назад"
ARROW_LEFT = "⬅️"
ARROW_RIGHT = "➡️"
DATETIME_FORMAT = "%d-%m-%Y %H:%M"
TIME_24_HOURS_FORMAT = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00",
                        "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
                        "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]

SUPERADMIN_IDS = os.getenv("ENV_SUPERADMIN_USERS").split(',')

BLOCKED_BY_USER = "Forbidden: bot was blocked by the user"
MESSAGE_NOT_FOUND = "Message to delete not found"
BEFORE_CONTENT = ""
AFTER_CONTENT = ""
OVERALL_MAX_RATE = 30
OVERALL_TIME_PERIOD = 1
GROUP_MAX_RATE = 20
GROUP_TIME_PERIOD = 60
MAX_RETRIES = 0
