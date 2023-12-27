import datetime
from core.config import DATETIME_FORMAT
from db.signs import SIGNS
from db.posts import posts, POST_TYPE
from db.users import users
from db.posts_sent import posts_sent
from repository.database.db import DatabaseRepository
from repository.tools import get_values
import sqlalchemy


class PostsRepository(DatabaseRepository):

    @staticmethod
    async def update(id: int, values: dict):
        query = posts.update().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_reminder():
        query = (sqlalchemy.select(posts)
                 .order_by(sqlalchemy.desc(posts.c.id))
                 .where(posts.c.type == POST_TYPE.REMINDER))
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def get_join_notification():
        query = (sqlalchemy.select(posts)
                 .order_by(sqlalchemy.desc(posts.c.id))
                 .where(posts.c.type == POST_TYPE.NOTIFICATION))
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def get_postcard():
        query = (sqlalchemy.select(posts)
                 .order_by(sqlalchemy.desc(posts.c.id))
                 .where(posts.c.type == POST_TYPE.POSTCARD))
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def get_by_id(id: int):
        query = posts.select().where(posts.c.id == id)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def get_by_date(date: datetime.datetime, limit: int = 14, skip: int = 0):
        query = (posts.select()
                 .where(posts.c.sending_date == date)
                 .limit(limit)
                 .offset(skip*limit)
                 )
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def create(values: dict):
        query = posts.insert().values(values)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_scheduled_broadcast(date: str = None, is_over: bool = False):
        _date = datetime.datetime.now() if date is None else date
        _date = _date.strftime(DATETIME_FORMAT)
        _date = datetime.datetime.strptime(_date, DATETIME_FORMAT)

        query = posts.select().order_by(sqlalchemy.desc(posts.c.sending_date)).where(posts.c.sending_date <= _date, posts.c.type == POST_TYPE.AD)
        if is_over:
            query = posts.select().order_by(sqlalchemy.desc(posts.c.sending_date)).where(posts.c.sending_date >= _date, posts.c.type == POST_TYPE.AD)

        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def get_count(id: int):
        query = (sqlalchemy.select(sqlalchemy.func.count(posts_sent.c.id))
                 .where(posts_sent.c.post_id == id))
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def make_sent(post_id: int, user_id: int):
        query = posts_sent.insert().values(post_id=post_id, user_id=user_id)
        result = await DatabaseRepository.execute(query)
        return result

    @staticmethod
    async def get_by_sign(sign_id: int, date: datetime):
        query = (posts.select()
                 .order_by(sqlalchemy.desc(posts.c.id))
                 .where(posts.c.sign_id == sign_id,
                        posts.c.sending_date == date)
                 )
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def get_horoscope_by_date(sign_id: int, date: datetime):
        query = posts.select().where(posts.c.sign_id == sign_id, posts.c.sending_date == date)
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def get_scheduled_horoscope(date: str = None, is_over: bool = False, limit: int = 14, skip: int = 0):
        _date = datetime.datetime.now() if date is None else date
        _date = _date.strftime(DATETIME_FORMAT)
        _date = datetime.datetime.strptime(_date, DATETIME_FORMAT).date()

        query = (posts.select()
                 .order_by(sqlalchemy.desc(posts.c.sending_date))
                 .where(posts.c.sending_date < _date, posts.c.type == POST_TYPE.HOROSCOPE)
                 .limit(limit)
                 .offset(skip * limit)
                 )

        if is_over:
            query = (posts.select()
                     .order_by(sqlalchemy.desc(posts.c.sending_date))
                     .where(posts.c.sending_date >= _date, posts.c.type == POST_TYPE.HOROSCOPE)
                     .limit(limit)
                     .offset(skip * limit)
                     )

        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def get_closest_date_without_horoscope():
        next_day = ""
        subquery = sqlalchemy.select([posts.c.sending_date]).order_by(posts.c.sending_date.desc()).limit(
            1).scalar_subquery()

        for sign_id in range(1, 13):
            query = (sqlalchemy.select(posts)
                     .order_by(sqlalchemy.desc(posts.c.sending_date))
                     .where(sqlalchemy.and_(posts.c.sign_id == sign_id, posts.c.sending_date == subquery)))
            no_posts = await DatabaseRepository.fetch_one(query)
            no_posts = get_values(no_posts)

            if no_posts is None and sign_id == 1:
                next_day = datetime.datetime.now().date() + datetime.timedelta(days=1)
                return {"sending_date": next_day, "sign": SIGNS["aries"]["sign"], "sign_id": 1}
            elif no_posts is not None and sign_id == 1:
                next_day = no_posts["sending_date"]
                continue
            elif no_posts is None:
                return {"sending_date": next_day, "sign": list(SIGNS.values())[sign_id - 1]["sign"], "sign_id": sign_id}
            elif sign_id == 12 and no_posts is not None:
                next_day = next_day + datetime.timedelta(days=1)
                return {"sending_date": next_day, "sign": SIGNS["aries"]["sign"], "sign_id": 1}

    @staticmethod
    async def get_dates(is_over: bool = True, limit: int = 14, skip: int = 0):
        _posts = await PostsRepository.get_scheduled_horoscope(is_over=is_over, limit=limit, skip=skip)
        values = {}

        for post in _posts:
            query = (sqlalchemy.select(sqlalchemy.func.count(posts.c.id))
                     .where(posts.c.sending_date == post["sending_date"]))
            result = await DatabaseRepository.fetch_one(query)
            result = get_values(result)
            value = {f"{post['sending_date']}": {"date": post["sending_date"],
                                              "count": result["count_1"]}}

            values.update(value)
        return values

    @staticmethod
    async def get_last_sent(chat_id: str):
        query = (posts_sent.select()
                 .order_by(sqlalchemy.desc(posts_sent.c.id))
                 .where(users.c.chat_id == chat_id,
                        posts_sent.c.user_id == users.c.id))
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

    @staticmethod
    async def get_scheduled_current_date(date: datetime):
        query = posts.select().where(posts.c.sending_date == date, posts.c.type == POST_TYPE.HOROSCOPE)
        result = await DatabaseRepository.fetch_all(query)
        return get_values(result)

    @staticmethod
    async def select_single(sign_id: int):
        query = posts.select().order_by(sqlalchemy.desc(posts.c.sending_date)).where(posts.c.sign_id == sign_id)
        result = await DatabaseRepository.fetch_one(query)
        result = get_values(result)
        if result is None or result["sending_date"] is None:
            return datetime.datetime.now().date() + datetime.timedelta(days=1)
        next_date = result["sending_date"] + datetime.timedelta(days=1)
        return next_date.date()
