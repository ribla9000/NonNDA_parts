import sqlalchemy
from db.business_data import business_data
from typing import Union
from repository.database.database import DatabaseRepository
from repository.tools import get_values


class BusinessDataRepository(DatabaseRepository):

    @staticmethod
    async def create(values: dict):
        query = business_data.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def update(id: int, values: dict):
        query = business_data.update().values(values).where(business_data.c.id == id)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_by_id(id: int):
        query = business_data.select().where(business_data.c.id == id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def get_by_external_id(external_id: str):
        query = business_data.select().where(business_data.c.external_id == external_id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def get_by_closest_l2_distance(embedding: list, user_id: Union[None, str], limit: int = 5):
        if user_id is None:
            query = (sqlalchemy
                     .select(business_data.c.content,
                             business_data.c.embedding.max_inner_product(embedding).label("score"))
                     .order_by(sqlalchemy.asc(business_data.c.embedding.max_inner_product(embedding)))
                     .where(business_data.c.embedding.max_inner_product(embedding) < -0.7)
                     .limit(limit)
                     )
        else:
            query = (sqlalchemy
                     .select(business_data.c.content, business_data.c.embedding.max_inner_product(embedding).label("score"))
                     .order_by(sqlalchemy.asc(business_data.c.embedding.max_inner_product(embedding)))
                     .where(business_data.c.user_id == user_id, business_data.c.embedding.max_inner_product(embedding) < -0.2)
                     .limit(limit)
                     )
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)
