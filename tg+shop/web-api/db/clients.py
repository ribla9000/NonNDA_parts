from core.db import metadata
from enum import Enum
import sqlalchemy


class Payments(Enum):
    CARD = "card"
    CASH = "cash"


clients = sqlalchemy.Table(
    "clients",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True),
    sqlalchemy.Column("first_name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("last_name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("email", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("phone_number", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("delivery_type", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("courier_street", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("courier_apt", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("courier_home", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("courier_floor", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("city", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("post_office_number", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("payment", sqlalchemy.Enum(Payments), nullable=False),
)
