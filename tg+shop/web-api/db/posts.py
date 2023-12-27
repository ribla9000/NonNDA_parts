import sqlalchemy
from core.db import metadata


posts = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("product_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("html", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("is_ad", sqlalchemy.Boolean, nullable=False),
)
