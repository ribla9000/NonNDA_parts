import datetime
import sqlalchemy
from core.db import metadata



users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("is_blocked", sqlalchemy.Boolean, nullable=False, default=sqlalchemy.sql.expression.false())
)
