from db.posts import posts
from repository.database.db import DatabaseRepository
from repository.tools import get_values
import sqlalchemy


class PostsRepository(DatabaseRepository):

    @staticmethod
    async def create(values: dict):
        query = posts.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_by_product(product_id: int, is_ad: bool = False):
        query = (posts.select()
                 .where(posts.c.product_id == product_id, posts.c.is_ad == is_ad))
        result = await DatabaseRepository.fetch_one(query)

        if is_ad:
            result = await DatabaseRepository.fetch_all(query)

        return get_values(result)

    @staticmethod
    async def get_by_id(id: int):
        query = posts.select().where(posts.c.id == id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)
