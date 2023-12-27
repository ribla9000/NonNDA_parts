import asyncio
from telegram.ext import ContextTypes
from telegram import Update


def auto_delete_message(f):
    async def wrapper(*args: tuple, **kwargs: dict):

        async def try_to_delete():
            for message_number in range(1, 20):
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=message.id-message_number)
                except:
                    pass

        update: Update = args[0]
        context: ContextTypes.DEFAULT_TYPE = args[1]
        message = update.message
        query = update.callback_query

        if message is not None: #delete user's message
            chat_id = str(message.chat_id)

            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message.id)
            except:
                pass

        elif query is not None: #delete each message
            chat_id = str(query.from_user.id)
            message = query.message
            asyncio.create_task(try_to_delete())

        return await f(*args, **kwargs)
    return wrapper

