from repository.database.db import DatabaseRepository
from repository.tools import get_values
from db.settings import settings
import sqlalchemy
import datetime


class SettingsRepository(DatabaseRepository):

    @staticmethod
    async def create(values: dict):
        query = settings.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_last():
        query = settings.select().order_by(sqlalchemy.desc(settings.c.id))
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)