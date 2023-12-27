import asyncio
import os
import uvicorn
import sentry_sdk
from core.config import SHOP_BOT_TOKEN, WEBHOOK_URL, ENVIRONMENT
from core.db import database
from telegram import Update
from telegram.ext import Application
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
from handlers import ui_menu
from alembic.config import Config
from alembic import command


async def bot_startup_webhook():

    async def start_hooking(request: Request):
        await application.update_queue.put(
            Update.de_json(data=await request.json(), bot=application.bot)
        )
        return Response()

    application = Application.builder().token(SHOP_BOT_TOKEN).updater(None).build()
    ui_menu.add_handlers(application)
    await application.bot.set_webhook(url=WEBHOOK_URL, allowed_updates=Update.ALL_TYPES)
    starlette_app = Starlette(
        routes=[
            Route(f"/webhooks/", start_hooking, methods=["POST"]),
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


def bot_startup_polling():
    application = Application.builder().token(SHOP_BOT_TOKEN).build()
    ui_menu.add_handlers(application)
    loop = asyncio.get_event_loop()
    loop.create_task(startup())
    loop.create_task(application.run_polling(allowed_updates=Update.ALL_TYPES))


async def main():
    await startup()
    await bot_startup_webhook()


if __name__ == "__main__":
    alembic_cfg = Config("./alembic.ini")
    command.upgrade(alembic_cfg, "head")
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    if ENVIRONMENT == "development":
        bot_startup_polling()
    else:
        asyncio.run(main())