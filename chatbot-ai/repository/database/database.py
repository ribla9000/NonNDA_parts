from databases import Database
import typing
from sqlalchemy.sql.elements import ClauseElement
from core.db import database


class DatabaseRepository:
    def __init__(self, database: Database):
        self.database = database

    @staticmethod
    def fetch_all(query: typing.Union[ClauseElement, str], values: typing.Optional[dict] = None, ):
        return Database.fetch_all(self=database, query=query, values=values)

    @staticmethod
    def fetch_one(query: typing.Union[ClauseElement, str], values: typing.Optional[dict] = None, ):
        return Database.fetch_one(self=database, query=query, values=values)

    @staticmethod
    def execute(query: typing.Union[ClauseElement, str], values: typing.Optional[dict] = None, ):
        return Database.execute(self=database, query=query, values=values)
