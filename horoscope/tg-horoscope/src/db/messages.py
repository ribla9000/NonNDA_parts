import sqlalchemy
from core.db import metadata


messages = sqlalchemy.Table(
    "messages",
    metadata,
)
