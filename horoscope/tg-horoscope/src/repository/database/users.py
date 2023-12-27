import datetime
from db.users import users, ROLES
from repository.database.db import DatabaseRepository
from repository.tools import get_values


class UsersRepository(DatabaseRepository):

    @staticmethod
    async def get_unblocked():
        query = users.select().where(users.c.is_blocked == False)
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def get_all():
        query = users.select()
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def get_by_chat_id(chat_id: str):
        query = users.select().where(users.c.chat_id == chat_id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def create(values: dict):
        query = users.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def update(values: dict, id: int):
        query = users.update().values(values).where(users.c.id == id)
        result = await DatabaseRepository.execute(query)
        return result