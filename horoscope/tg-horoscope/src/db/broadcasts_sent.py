import sqlalchemy
from core.db import metadata


broadcasts_sent = sqlalchemy.Table(
    "broadcasts_sent",
)
