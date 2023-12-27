import os
from dotenv import load_dotenv

load_dotenv(".env")


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
ENVIRONMENT = os.getenv("ENVIRONMENT")
WEBHOOK_URL = os.getenv("ENV_WEBHOOK_URL")
MONOBANK_SIGNATURE_TOKEN = os.getenv("ENV_MONOBANK_SIGNATURE_TOKEN")
MONOBANK_PUBKEY = os.getenv("ENV_MONOBANK_PUBKEY")
MONOBANK_HEADERS = {
    "X-Token": MONOBANK_SIGNATURE_TOKEN
}