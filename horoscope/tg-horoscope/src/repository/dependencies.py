import datetime
from telegram.ext import AIORateLimiter
from core.config import OVERALL_MAX_RATE, OVERALL_TIME_PERIOD, GROUP_TIME_PERIOD, GROUP_MAX_RATE, MAX_RETRIES
from repository.database.posts import PostsRepository
from repository.database.settings import SettingsRepository
from repository.schedule_logic import ScheduleRepository
from repository.chat_events import ChatEventsRepository


rate_limiter = AIORateLimiter(
    overall_max_rate=OVERALL_MAX_RATE,
    overall_time_period=OVERALL_TIME_PERIOD,
    group_max_rate=GROUP_MAX_RATE,
    group_time_period=GROUP_TIME_PERIOD,
    max_retries=MAX_RETRIES
)


async def schedule_task_startup():
    scheduler = ScheduleRepository.scheduler
    broadcasts = await PostsRepository.get_scheduled_broadcast(is_over=True)

    for broadcast in broadcasts:
        date = broadcast["sending_date"]
        if date >= datetime.datetime.now():
            ScheduleRepository.add_task(
                scheduler=scheduler,
                callback=ChatEventsRepository.send_message,
                run_time=date,
                to_send=broadcast,
            )

    ScheduleRepository.add_task(
        scheduler=scheduler,
        callback=ChatEventsRepository.send_message_on_hour,
        task_type="hourly",
    )

    ScheduleRepository.add_task(
        scheduler=scheduler,
        callback=ChatEventsRepository.delete_messages,
        task_type="hourly"
    )

    settings = await SettingsRepository.get_last()

    birthday_sending_time = settings.get("birthday_sending_time") if settings is not None and settings.get("birthday_sending_time") is not None else "10:00"
    ScheduleRepository.add_task(
        scheduler=scheduler,
        task_id="birthday_cron",
        callback=ChatEventsRepository.send_postcard,
        task_type="day",
        run_time=birthday_sending_time,
    )
    reminder_sending_time = settings.get("reminder_sending_time") if settings is not None and settings.get("reminder_sending_time") is not None else "10:00"
    ScheduleRepository.add_task(
        scheduler=scheduler,
        task_id="reminder_cron",
        callback=ChatEventsRepository.send_reminder,
        task_type="day",
        run_time=reminder_sending_time,
    )
