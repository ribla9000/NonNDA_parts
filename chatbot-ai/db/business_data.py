import sqlalchemy
from pgvector.sqlalchemy import Vector
from core.db import metadata


business_data = sqlalchemy.Table(
    "business_data",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("external_id", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("user_id", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("content", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("embedding", Vector(1536), nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=True, default=sqlalchemy.func.now()),
)
