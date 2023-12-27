import sqlalchemy
from core.db import metadata


class MESSAGE_TYPES:
    DIALOG = "dialog"
    HOROSCOPE = "horoscope"
    BROADCAST = "broadcast"
    PRESENT_NOTIFY = "present_notify"


messages_to_delete = sqlalchemy.Table(
    "messages_to_delete",
    metadata,
)
