import asyncio
import datetime
import os
import uvicorn
import sentry_sdk
from alembic.config import Config
from alembic import command
from core.config import HOROSCOPE_BOT_TOKEN, WEBHOOK_URL, SENTRY_TOKEN, ENVIRONMENT
from core.db import database
from telegram import Update
from telegram.ext import Application
from handlers import ui_menu
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
from repository.dependencies import rate_limiter, schedule_task_startup


sentry_sdk.init(
    dsn=SENTRY_TOKEN,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    environment=ENVIRONMENT
)


async def bot_startup_webhook():

    async def start_hooking(request: Request):
        await application.update_queue.put(
            Update.de_json(data=await request.json(), bot=application.bot)
        )
        return Response()

    application = Application.builder().token(HOROSCOPE_BOT_TOKEN).rate_limiter(rate_limiter).updater(None).build()
    ui_menu.add_handlers(application)
    await application.bot.set_webhook(url=WEBHOOK_URL, allowed_updates=Update.ALL_TYPES)
    starlette_app = Starlette(
        routes=[
            Route(f"/{HOROSCOPE_BOT_TOKEN}", start_hooking, methods=["POST"]),
        ]
    )

    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            reload=True,
            port=8443,
            use_colors=True,
            host="0.0.0.0",
        )
    )

    async with application:
        await application.start()
        await webserver.serve()
        await application.stop()


async def startup():
    await database.connect()
    await schedule_task_startup()


def bot_startup_polling():
    print("hour now:",(datetime.datetime.now()).strftime("%H:00"))
    print("launch time:",datetime.datetime.now())
    application = Application.builder().token(HOROSCOPE_BOT_TOKEN).rate_limiter(rate_limiter).build()
    ui_menu.add_handlers(application)
    loop = asyncio.get_event_loop()
    loop.create_task(startup())
    loop.create_task(application.run_polling(allowed_updates=Update.ALL_TYPES))


async def main():
    await startup()
    await bot_startup_webhook()


if __name__ == "__main__":
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    alembic_cfg = Config("./alembic.ini")
    command.upgrade(alembic_cfg, "head")
    if ENVIRONMENT == "development":
        bot_startup_polling()
    else:
        asyncio.run(main())
