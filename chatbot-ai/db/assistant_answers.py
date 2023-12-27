import sqlalchemy
from core.db import metadata


assistant_answers = sqlalchemy.Table(
    "assistant_answers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("prompt", sqlalchemy.ARRAY(sqlalchemy.JSON), nullable=True, server_default="{}"),
    sqlalchemy.Column("answer", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=True, default=sqlalchemy.func.now()),
)
