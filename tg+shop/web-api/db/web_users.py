import sqlalchemy
from core.db import metadata
from enum import Enum


class WebRoles(Enum):
    GUEST = "guest"
    CLIENT = "client"
    PARTNER = "partner"
    ADMIN = "admin"


web_users = sqlalchemy.Table(
    "web_users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("tg_user_id", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("email", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("role", sqlalchemy.Enum(WebRoles), nullable=False),
)
