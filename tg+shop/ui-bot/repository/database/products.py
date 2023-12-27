from db.products import products
from repository.database.db import DatabaseRepository
from repository.tools import get_values
import sqlalchemy


class ProductRepository(DatabaseRepository):

    @staticmethod
    async def get_all():
        query = products.select()
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def create(values: dict):
        query = products.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_by_id(id: int):
        query = products.select().where(products.c.id == id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)
