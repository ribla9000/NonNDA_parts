import sqlalchemy
from core.db import metadata


posts_sent = sqlalchemy.Table(
    "posts_sent",
    metadata,
)
