import sqlalchemy
from core.db import metadata


products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("price", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("url", sqlalchemy.String, nullable=False),
)
