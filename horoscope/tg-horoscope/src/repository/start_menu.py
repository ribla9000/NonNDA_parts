import asyncio
import datetime
from db.signs import SIGNS
from repository.database.users import UsersRepository, ROLES
from repository.database.personal_info import PersonalInfoRepository
from repository.database.posts import PostsRepository, POST_TYPE
from repository.admin_menu import AdminMenu
from repository.tools import (
    keyboard_cols,
    get_zodiac_sign,
    validate_time,
    validate_date,
    parse_content_constants,
    make_long_length
)
from repository.decorators import auto_delete_message
from repository.database.messages import MessagesRepository, MESSAGE_TYPES
from core.config import TIME_24_HOURS_FORMAT, SUPERADMIN_IDS, BEFORE_CONTENT, AFTER_CONTENT
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode


def log_messages(f):
    async def wrapper(*args: tuple, **kwargs: dict):
        update: Update = args[0]
        funcs_to_auto_delete = {
            "get_horoscope": {
                "type": MESSAGE_TYPES.HOROSCOPE,
                "deleting_date": None,
            },
            "send_message": {
                "type": MESSAGE_TYPES.HOROSCOPE,
                "deleting_date": datetime.datetime.now() + datetime.timedelta(days=1),
            },
        }

        if update.effective_user is None:
            return await f(*args, **kwargs)

        func_name = f.__name__
        from_user = update.effective_message.from_user if update.effective_message is not None else update.chat_join_request.from_user
        message = update.effective_message
        message_id = message.id if message else None
        text_html = message.text_html if message else None
        date = datetime.datetime.now()
        is_bot = from_user.is_bot
        from_chat_id = str(from_user.id)
        to_chat_id = str(update.effective_message.chat.id) if message else None

        values = {
            "html": text_html,
            "message_id": message_id,
            "from_chat_id": from_chat_id,
            "to_chat_id": to_chat_id,
            "date_created": date,
            "is_bot": is_bot,
            "event_name": func_name,
        }
        message_id = await MessagesRepository.create(values)

        if func_name not in funcs_to_auto_delete.keys():
            return await f(*args, **kwargs)

        func_config = funcs_to_auto_delete[func_name]

        deleting_values = {
            "message_id": message_id,
            "type": func_config["type"],
            "deleting_date": func_config["deleting_date"],
        }
        await MessagesRepository.to_delete(deleting_values)

        return await f(*args, **kwargs)

    return wrapper


class StartMenu:

    @staticmethod
    async def get_next_day_of_sending_horoscope(chat_id: str):
        personal_info = await PersonalInfoRepository.get_by_chat_id(chat_id)
        last_sent = await PostsRepository.get_last_sent(chat_id)
        next_date = ((datetime.datetime.now().date() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
                     + f" {personal_info['broadcast_time']}")

        if last_sent is not None:
            content = await PostsRepository.get_by_id(last_sent["post_id"])
            hours, minutes = personal_info["broadcast_time"].split(":")
            content_sending_date = content["sending_date"] + datetime.timedelta(hours=int(hours), minutes=int(minutes))

            if content_sending_date < datetime.datetime.now():
                next_date = ((datetime.datetime.now().date()).strftime("%d.%m.%Y")
                             + f" {personal_info['broadcast_time']}")

        return next_date

    @staticmethod
    @log_messages
    async def get_current_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        join_request = update.chat_join_request
        chat_id = str(update.message.chat_id if query is None else query.from_user.id) if join_request is None else str(join_request.from_user.id)
        personal_info = await PersonalInfoRepository.get_by_chat_id(chat_id)
        next_date = await StartMenu.get_next_day_of_sending_horoscope(chat_id)

        keyboard = [[InlineKeyboardButton(text="⭐️ Гороскоп на сьогодні", callback_data="get_horoscope")],
                    [InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings_menu")]]

        if query is None and join_request is None:
            await update.message.reply_text(
            )
        elif join_request is not None:
            await context.bot.send_message(
                text=reply_text,
            )
        elif query is not None:
            await query.edit_message_text(
                text=reply_tsext,
            )

        return ConversationHandler.END

    @staticmethod
    #@auto_delete_message
    @log_messages
    async def create_personal(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        user = await UsersRepository.get_by_chat_id(chat_id)

        if user is not None:
            await PersonalInfoRepository.delete_by_user(user_id=user["id"])

        if query is None or query.message.caption and update.message is not None:

            if update.message.text == " ":
                await context.bot.delete_message(chat_id=chat_id, message_id=update.message.id)

            await update.message.reply_text(
                quote=False,
                text=reply_text,
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove()
            )
        elif query is not None and query.message.caption and update.message is None:
            data = query.data.split(",")
            to_edit = True if len(data) == 1 else False

            if to_edit:
                await query.delete_message()
                await context.bot.send_message(
                    parse_mode=ParseMode.HTML,
                    chat_id=chat_id
                )
            elif not to_edit:
                await context.bot.send_message(
                    text=reply_text,
                    parse_mode=ParseMode.HTML,
                    chat_id=chat_id
                )

        elif query is not None:
            await query.answer()
            data = query.data.split(",")
            to_edit = True if len(data) == 1 else False

            if to_edit:
                await query.edit_message_text(text=reply_text, parse_mode=ParseMode.HTML)
            elif not to_edit:
                await context.bot.send_message(
                    text=reply_text,
                    parse_mode=ParseMode.HTML,
                    chat_id=chat_id
                )

        return "input_name"

    @staticmethod
    async def get_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        user = await UsersRepository.get_by_chat_id(chat_id)

        if user is None and update.message is not None:
            values = {
                "name": update.message.from_user.full_name,
                "nickname": update.message.from_user.username,
                "chat_id": chat_id,
                "role": ROLES["USER"]
            }

            if chat_id in SUPERADMIN_IDS:
                values["role"] = ROLES["ADMIN"]

            await UsersRepository.create(values)

        if user is not None and user["is_blocked"] is True:
            await UsersRepository.update(id=user["id"], values={"is_blocked": False})

        if user is not None and user["role"] == ROLES["ADMIN"] or chat_id in SUPERADMIN_IDS:
            return await AdminMenu.get_menu(update, context)

        personal_info = await PersonalInfoRepository.get_by_chat_id(chat_id)

        if personal_info is not None:
            return await StartMenu.get_current_user(update, context)

        if query is not None:
            await query.answer()
            await query.edit_message_text(
            )

        elif query is None:
                quote=False,
                text=reply_text,
                parse_mode=ParseMode.HTML
            )
        return await StartMenu.create_personal(update, context)

    @staticmethod
    @log_messages
    async def input_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        date = update.message.text
        nickname = update.message.from_user.username
        chat_id = str(update.message.chat_id)
        full_name = update.message.from_user.full_name
        validated_date = validate_date(date)

        if validated_date is None:
            await update.message.reply_text(
                quote=False,
                parse_mode=ParseMode.HTML
            )
            return "input_name"

        sign, sign_id = get_zodiac_sign(birthday_date=date, SIGNS=SIGNS)

        context.bot_data[f"{chat_id}:horoscope"] = {
        }
        return "input_birthday_time"

    @staticmethod
    @log_messages
    async def input_birthday_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        chat_id = str(update.message.chat_id)
        user_data = context.bot_data[f"{chat_id}:horoscope"]
        user_data["info"]["name"] = text
        return "choose_gender"

    @staticmethod
    @log_messages
    async def choose_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        chat_id = str(update.message.chat_id)
        user_data = context.bot_data[f"{chat_id}:horoscope"]
        text = validate_time(text)

        if text is None:
            return "choose_gender"

        user_data["info"]["time_birthday"] = text
        keyboard = [[InlineKeyboardButton(text="Жінка", callback_data="recive_broadcast,Жінка"),
                     InlineKeyboardButton(text="Чоловік", callback_data="recive_broadcast,Чоловік")]]
        await update.message.reply_text(
            text="<b>Стать? ㅤ ㅤ</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    @staticmethod
    #@auto_delete_message
    @log_messages
    async def receive_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data.split(",")
        gender = data[1]
        chat_id = str(query.from_user.id)
        user_data = context.bot_data[f"{chat_id}:horoscope"]
        user_data["info"]["gender"] = gender

        keyboard = [InlineKeyboardButton(text=t, callback_data=f"save_user_data,{t}") for t in TIME_24_HOURS_FORMAT]
        keyboard = keyboard_cols(keyboard, 4)
        keyboard = keyboard

        await query.edit_message_text(text="<b>У якій годині тобі зручно отримувати щоденний гороскоп?</b>\n"
                                           f"<i>Час на сервері: {datetime.datetime.now().strftime('%H:%M')}</i>",
                                      parse_mode=ParseMode.HTML,
                                      reply_markup=InlineKeyboardMarkup(keyboard))

    @staticmethod
    #@auto_delete_message
    @log_messages
    async def save_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data.split(",")
        broadcast_time = data[1] if data[1] != 'None' else None
        chat_id = str(query.from_user.id)
        user_data = context.bot_data[f"{chat_id}:horoscope"]
        user_data["info"]["broadcast_time"] = broadcast_time
        user = await UsersRepository.get_by_chat_id(chat_id)

        if user is None:
            user_id = await UsersRepository.create(user_data["user"])

        user_data["info"]["user_id"] = user_id if user is None else user["id"]
        personal_info_id = await PersonalInfoRepository.create(user_data["info"])

        if query is not None:
            await query.edit_message_text(
                text="<b>Налаштування завершено!</b>\nМи вже готуємо твій персональний гороскоп!",
                parse_mode=ParseMode.HTML
        )
        else:
            await update.message.reply_text(
                quote=False,
                text="<b>Налаштування завершено!</b>\nМи вже готуємо твій персональний гороскоп!",
                parse_mode=ParseMode.HTML
            )

        await StartMenu.get_horoscope(update, context)
        del context.bot_data[f"{chat_id}:horoscope"]

    @staticmethod
    async def send_horoscope_loader(update: Update, context: ContextTypes.DEFAULT_TYPE):
        async def _collect_message(_mess_chat: Update.message, _mess_id: int):
            values = {
                "html": content["html"],
                "message_id": _mess_chat.id,
                "from_chat_id": str(_mess_chat.from_user.id),
                "to_chat_id": str(_mess_chat.chat.id),
                "date_created": datetime.datetime.now(),
                "is_bot": _mess_chat.from_user.is_bot,
                "event_name": "get_horoscope",
            }
            message_id = await MessagesRepository.create(values)
            deleting_values = {
                "message_id": message_id,
                "type": MESSAGE_TYPES.HOROSCOPE,
                "deleting_date": None,
            }
            await MessagesRepository.to_delete(deleting_values)

        async def _delete_messages(except_id: int = None):
            messages = await MessagesRepository.get_by_type(chat_id=chat_id, type=MESSAGE_TYPES.HOROSCOPE, except_id=except_id)
            for item in messages:
                _mes = await MessagesRepository.get_by_id(item["message_id"])
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=_mes["message_id"])
                    await MessagesRepository.make_deleted(message_id=_mes["message_id"])
                except:
                    pass

        query = update.callback_query
        await query.answer()
        chat_id = str(query.from_user.id)
        user_data = await PersonalInfoRepository.get_by_chat_id(chat_id)
        date_today = (datetime.datetime.now()).date()
        message = await query.from_user.send_message(
        )

        await context.bot.edit_message_text(chat_id=chat_id, message_id=message.id, text="Обробка даних...")
        await asyncio.sleep(1)
        await context.bot.edit_message_text(chat_id=chat_id, message_id=message.id, text="Завантаження...")
        await asyncio.sleep(2)

        content = await PostsRepository.get_by_sign(sign_id=user_data["sign_id"], date=date_today)

        if content is None:
            await context.bot.edit_message_text(
s                chat_id=chat_id,
                message_id=message.id
            )
            return ConversationHandler.END

        reply_text = parse_content_constants(
            bc=BEFORE_CONTENT,
            ac=AFTER_CONTENT,
            con=content["html"],
            name=user_data["name"],
            date=date_today.strftime("%d.%m.%Y"))
        await context.bot.delete_message(chat_id=chat_id, message_id=query.message.id)

        if content["image_path"]:
            await context.bot.delete_message(chat_id, message_id=message.id)
            _message = await context.bot.send_photo(
                chat_id=chat_id,
                caption=reply_text,
                photo=content["image_path"],
                parse_mode=ParseMode.HTML,
            )

        else:
            _message = await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message.id,
                text=reply_text,
                parse_mode=ParseMode.HTML
            )

        await PostsRepository.make_sent(user_id=user_data["user_id"], post_id=content["id"])
        await asyncio.create_task(_delete_messages())
        await context.bot.send_message(
            chat_id=chat_id,
            parse_mode=ParseMode.HTML
        )
        await _collect_message(_mess_chat=_message, _mess_id=_message.id)
        return ConversationHandler.END

    @staticmethod
    #@auto_delete_message
    async def get_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await asyncio.create_task(StartMenu.send_horoscope_loader(update, context))
        return ConversationHandler.END
