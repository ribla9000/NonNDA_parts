import datetime

from repository.database.db import DatabaseRepository
from repository.tools import get_values


class StatisticsRepository(DatabaseRepository):

    @staticmethod
    async def get_stats():
        today = (datetime.datetime.now())
        query = """
                SELECT
(SELECT COUNT(*) FROM personal_info) AS ucount,
(SELECT COUNT(*) FROM users WHERE is_blocked = 't') AS ublocked,
(SELECT COUNT(*) FROM posts_sent JOIN posts ON posts_sent.post_id = posts.id WHERE posts.type = 'horoscope') AS hsent,
(SELECT COUNT(*) FROM posts_sent JOIN posts ON posts_sent.post_id = posts.id WHERE posts.type = 'ad') AS adsent,
(SELECT COUNT(*) FROM posts_sent JOIN posts ON posts_sent.post_id = posts.id WHERE posts.sending_date = CURRENT_DATE AND posts.type = 'horoscope') AS hsent_t,
(SELECT COUNT(*) FROM personal_info WHERE date_registered >= CURRENT_DATE - INTERVAL '1 day') AS ureg_t,
(SELECT COUNT(*) FROM personal_info WHERE date_registered >= CURRENT_DATE - INTERVAL '7 days') AS newu_w
                """
        result = await DatabaseRepository.fetch_one(query)
        return get_values(result)

