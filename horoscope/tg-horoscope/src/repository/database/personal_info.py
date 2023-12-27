from db.personal_info import personal_info
from db.users import users
from repository.database.db import DatabaseRepository
from repository.tools import get_values
import sqlalchemy
import datetime


class PersonalInfoRepository(DatabaseRepository):

    @staticmethod
    async def get_by_chat_id(chat_id: str):
        query = personal_info.select().where(users.c.chat_id == chat_id,
                                             personal_info.c.user_id == users.c.id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def create(values: dict):
        query = personal_info.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_by_time(time: str):
        query = (sqlalchemy.select(personal_info, users.c.chat_id)
                 .where(personal_info.c.broadcast_time == time,
                        personal_info.c.user_id == users.c.id,))
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def delete(id: int):
        query = personal_info.delete().where(personal_info.c.id == id)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def delete_by_user(user_id: int):
        query = personal_info.delete().where(personal_info.c.user_id == user_id)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def update(values: dict, user_id: int):
        query = personal_info.update().values(values).where(personal_info.c.user_id == user_id)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_by_birthday(birthday: str):
        query = sqlalchemy.select(personal_info, users.c.chat_id).where(
            sqlalchemy.func.cast(sqlalchemy.func.substr(personal_info.c.date_birthday, 1, 5), sqlalchemy.String) == birthday,
            personal_info.c.user_id == users.c.id
        )
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def get_without_personal():
        query = (sqlalchemy.select(users.c.chat_id)
                 .where(~users.c.id.in_(sqlalchemy.select(personal_info.c.user_id)))
                 )

        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)
