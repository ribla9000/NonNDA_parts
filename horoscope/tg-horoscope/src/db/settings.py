import sqlalchemy
from core.db import metadata


settings = sqlalchemy.Table(
    "settings",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
)
