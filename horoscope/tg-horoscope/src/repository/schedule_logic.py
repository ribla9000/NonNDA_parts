from apscheduler.schedulers.asyncio import AsyncIOScheduler


class ScheduleRepository:

    @staticmethod
    def initialize():
        scheduler = AsyncIOScheduler()
        scheduler.start()
        return scheduler

    @staticmethod
    def add_task(callback: callable,
                 scheduler: AsyncIOScheduler,
                 run_time: str = None,
                 task_id: str = None,
                 task_type: str = "specific_time",
                 *args,
                 **kwargs):

        if task_type == "specific_time":
            scheduler.add_job(func=callback, trigger="date", run_date=run_time, id=task_id, args=args, kwargs=kwargs, misfire_grace_time=120)
        elif task_type == "hourly":
            scheduler.add_job(func=callback, trigger='cron', hour='0-23', id=task_id, args=args, kwargs=kwargs)
        elif task_type == "5sec":
            scheduler.add_job(func=callback, trigger='interval', seconds=5, id=task_id, args=args, kwargs=kwargs)
        elif task_type == "day":
            data = run_time.split(":")
            hour, minute = str(data[0]), str(int(data[1]))
            scheduler.add_job(func=callback, trigger='cron', hour=hour, minute=minute, id=task_id, args=args, kwargs=kwargs)

        return scheduler

    @staticmethod
    def delete_task(scheduler: AsyncIOScheduler, task_id: str):
        try:
            scheduler.remove_job(task_id)
            return scheduler
        except Exception as e:
            print(f"Error deleting task with id {task_id}: {e}")
            return scheduler


ScheduleRepository.scheduler: AsyncIOScheduler = ScheduleRepository.initialize()
