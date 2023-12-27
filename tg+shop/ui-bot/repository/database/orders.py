from db.orders import orders
from repository.database.db import DatabaseRepository
from repository.tools import get_values
import sqlalchemy


class OrdersRepository(DatabaseRepository):

    @staticmethod
    async def create(values: dict):
        query = orders.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_by_user(user_id: int, skip: int = 0):
        query = (orders.select()
                 .where(orders.c.user_id == user_id)
                 .limit(5)
                 .offset(skip * 5)
                 )
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def get_count(status: str, user_id: int, product_id: int):
        query = (sqlalchemy.select(sqlalchemy.func.count(orders.c.id))
                 .where(orders.c.user_id == user_id, orders.c.status == status, orders.c.product_id == product_id))
        result = await DatabaseRepository.fetch_one(query)
        if result is None:
            return 0
        return get_values(result)["count_1"]