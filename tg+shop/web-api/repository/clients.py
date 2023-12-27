from repository.database import DatabaseRepository
from repository.tools import get_values
from db.clients import clients


class ClientsRepository(DatabaseRepository):

    @staticmethod
    async def create(values: dict):
        query = clients.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def update(values: dict):
        query = clients.update().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_by_id(id: int):
        query = clients.select().where(clients.c.id == id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

