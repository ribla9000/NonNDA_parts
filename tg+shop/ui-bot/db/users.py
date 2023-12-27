import sqlalchemy
from core.db import metadata

ROLES = {
    "PARTNER": "partner",
    "ADMIN": "admin",
}


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("nickname", sqlalchemy.String),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("chat_id", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("role", sqlalchemy.String, nullable=False, server_default=ROLES["PARTNER"]),
    sqlalchemy.Column("ukey", sqlalchemy.String, nullable=True)
)
