import sqlalchemy
from core.db import metadata


content_sent = sqlalchemy.Table(
    "content_sent",
    metadata,

)
