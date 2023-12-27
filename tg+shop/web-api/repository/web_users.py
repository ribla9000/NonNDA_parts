from repository.database import DatabaseRepository
from repository.tools import get_values
from db.web_users import web_users


class UsersRepository(DatabaseRepository):

    @staticmethod
    async def create(values: dict):
        query = web_users.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def update(values: dict):
        query = web_users.update().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_by_id(id: int):
        query = web_users.select().where(web_users.c.id == id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

