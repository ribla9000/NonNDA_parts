import sqlalchemy
from db.chats import chats
from repository.database.database import DatabaseRepository
from repository.tools import get_values


class ChatsRepository(DatabaseRepository):

    @staticmethod
    async def create(values: dict):
        query = chats.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def update(id: int, values: dict):
        query = chats.update().values(values).where(chats.c.id == id)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_by_id(id: int):
        query = chats.select().where(chats.c.id == id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)
