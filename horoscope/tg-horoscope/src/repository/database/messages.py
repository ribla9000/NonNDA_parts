import datetime
from repository.database.db import DatabaseRepository
from db.messages import messages
from db.messages_to_delete import messages_to_delete, MESSAGE_TYPES
from repository.tools import get_values
import sqlalchemy


class MessagesRepository(DatabaseRepository):

    @staticmethod
    async def get_by_id(id: int):
        query = messages.select().where(messages.c.id == id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def create(values: dict):
        query = messages.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def to_delete(values: dict):
        query = messages_to_delete.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_all(chat_id: str, except_message_id: int = None):
        query = (sqlalchemy.select(messages).where(messages.c.to_chat_id == chat_id,messages.c.message_id != except_message_id))
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def get_by_type(chat_id: str, type: str, except_id: int = None):
        query = (sqlalchemy.select(messages_to_delete)
                 .where(
                        messages.c.to_chat_id == chat_id,
                        messages.c.message_id != except_id,
                        messages_to_delete.c.message_id == messages.c.id,
                        messages_to_delete.c.is_deleted != True,
                        messages_to_delete.c.type == type,
                 )
        )
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def make_deleted(message_id: int):
        query = messages_to_delete.update().values({"is_deleted": True}).where(messages_to_delete.c.message_id == message_id)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_to_delete():
        now = datetime.datetime.now()
        query = (messages.select()
                 .where(messages.c.id == messages_to_delete.c.message_id,
                        messages_to_delete.c.deleting_date <= now,
                        messages_to_delete.c.is_deleted == False)
                 )
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def get_by_chat_id(chat_id: str):
        query = messages.select().where(messages.c.to_chat_id == chat_id)
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)
