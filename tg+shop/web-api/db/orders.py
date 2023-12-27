import sqlalchemy
from core.db import metadata

STATUS: dict ={
    "NEW": "new",
    "INTRASIT": "in transit",
    "DELIVERED": "delivered",
    "COMPLETED": "completed",
    "CANCELED": "canceled"
}


orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("product_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("tg_user_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("status", sqlalchemy.String, nullable=False, server_default=STATUS["NEW"]),
)
