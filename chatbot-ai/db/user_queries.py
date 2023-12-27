import sqlalchemy
from core.db import metadata


user_queries = sqlalchemy.Table(
    "user_queries",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("user_id", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("query", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=True, default=sqlalchemy.func.now()),
)
