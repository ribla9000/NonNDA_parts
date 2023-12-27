import os
from dotenv import load_dotenv

load_dotenv(".env")


SHOP_BOT_TOKEN = os.getenv("ENV_SHOP_BOT_TOKEN")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
API_BASE_URL = os.getenv("ENV_API_BASE_URL")
WEBHOOK_URL = os.getenv("ENV_WEBHOOK_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT")

BACK_BUTTON_TEXT = "«Back"
SUPERADMIN_IDS = os.getenv("ENV_SUPERADMIN_USERS").split(',')

BLOCKED_BY_USER = "Forbidden: bot was blocked by the user"
MESSAGE_NOT_FOUND = "Message to delete not found"