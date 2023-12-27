import datetime

import sqlalchemy
from core.db import metadata


personal_info = sqlalchemy.Table(
    "personal_info",
    metadata,
)
