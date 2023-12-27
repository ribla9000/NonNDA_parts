import sqlalchemy
from core.db import metadata


chats = sqlalchemy.Table(
    "chats",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("user_query_id", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("prompt", sqlalchemy.ARRAY(sqlalchemy.JSON), nullable=True, server_default="{}"),
    sqlalchemy.Column("user_query", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("assistant_answer", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=True, default=sqlalchemy.func.now()),
)
