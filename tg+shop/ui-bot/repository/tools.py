import asyncio
import datetime
import time
import requests
import random
import string
from core.config import API_BASE_URL


def keyboard_cols(buttons, cols):
    menu = [buttons[i:i + cols] for i in range(0, len(buttons), cols)]
    return menu


def get_values(values):
    if values is None:
        return None
    return [dict(value) for value in values] if isinstance(values, list) else dict(values)


def create_unique_key():
    letters = string.ascii_letters
    unique_key = ''.join(random.choice(letters) for _ in range(16))
    return unique_key

