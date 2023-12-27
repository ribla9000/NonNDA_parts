import sqlalchemy
from core.db import metadata


class BROADCAST_TYPE:
    AD = "ad"
    HOROSCOPE = "horoscope"
    POSTCARD = "postcard"
    NOTIFICATION = "notification"
    REMINDER = "reminder"


broadcasts = sqlalchemy.Table(
    "broadcasts",
    metadata,
)
