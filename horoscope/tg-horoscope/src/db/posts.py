import sqlalchemy
from core.db import metadata


class POST_TYPE:
    AD = "ad"
    HOROSCOPE = "horoscope"
    POSTCARD = "postcard"
    NOTIFICATION = "notification"
    REMINDER = "reminder"


posts = sqlalchemy.Table(
    "posts",
    metadata,
)
