import sqlalchemy
from core.db import metadata


content = sqlalchemy.Table(
    "content",
    metadata,
)
