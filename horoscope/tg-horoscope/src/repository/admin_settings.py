import datetime
from core.config import BACK_BUTTON_TEXT
from repository.tools import collect_message, validate_time, send_message_from_bot, make_long_length
from repository.chat_events import ChatEventsRepository
from repository.database.posts import PostsRepository, POST_TYPE
from repository.database.personal_info import PersonalInfoRepository
from repository.database.settings import SettingsRepository
from repository.decorators import auto_delete_message
from repository.schedule_logic import ScheduleRepository
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode


class AdminSettings:

    @staticmethod
    #@auto_delete_message
    async def get_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        reply_text = make_long_length("")
        keyboard = [
            [InlineKeyboardButton(text="🎂", callback_data="")],
            [InlineKeyboardButton(text="👽 ", callback_data="")],
            [InlineKeyboardButton(text="📂 ", callback_data="")],
            [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="")]
        ]
        if query is None:
            await update.message.reply_text(
                quote=False,
                text=reply_text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ConversationHandler.END

        await query.answer()
        await query.edit_message_text(
            text=reply_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    @staticmethod
    #@auto_delete_message
    async def birthday_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        reply_text = make_long_length("")

        change_time_button = [
            InlineKeyboardButton(text="🕐 ", callback_data="")
        ]
        get_birthdays_today_button = [
            InlineKeyboardButton(text="🗓 Д", callback_data="")
        ]
        back_button = [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="")]
        keyboard = [
            [InlineKeyboardButton(text="✏️ ", callback_data="")],
            [InlineKeyboardButton(text="👁 ", callback_data="")],
            change_time_button, get_birthdays_today_button, back_button]

        if query is None:
            await update.message.reply_text(
                quote=False,
                text=reply_text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ConversationHandler.END

        await query.answer()
        await query.edit_message_text(
            text=reply_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    @staticmethod
    async def create_postcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        keyboard = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="birthday_menu")]]
        await query.edit_message_text(
            text="",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return "save_postcard"

    @staticmethod
    async def store_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.message.chat_id)
        values = await collect_message(update, context)
        values.pop("sending_date")
        values["type"] = POST_TYPE.POSTCARD
        context.bot_data.update({f"{chat_id}:postcard-create": {"values": values}})

    @staticmethod
    async def save_postcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.message.chat_id)
        values = await collect_message(update, context)
        values.pop("sending_date")
        values["type"] = POST_TYPE.POSTCARD
        await PostsRepository.create(values)
        await AdminSettings.get_menu(update, context)
        return ConversationHandler.END

    @staticmethod
    #@auto_delete_message
    async def get_postcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
        postcard = await PostsRepository.get_postcard()
        query = update.callback_query
        await query.answer()
        chat_id = str(query.from_user.id)
        back_button = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="")]]

        if postcard is None:
            back_button = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="birthday_menu")]]
            await query.edit_message_text(
                text=" ",
                reply_markup=InlineKeyboardMarkup(back_button)
            )
            return "save_postcard"

        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=query.message.id
        )
        await send_message_from_bot(chat_id=chat_id, values=postcard, bot=context.bot)
        await context.bot.send_message(
            chat_id=chat_id,
            text="",
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    @staticmethod
    async def get_birthday_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        today = datetime.datetime.now().date()
        today = today.strftime("%d.%m")
        birthdays = await PersonalInfoRepository.get_by_birthday(today)
        count = len(birthdays)
        reply_text = f""

        back_button = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="birthday_menu")]]

        await query.edit_message_text(
            text=reply_text,
            reply_markup=InlineKeyboardMarkup(back_button)
        )
        return ConversationHandler.END

    @staticmethod
    async def change_birthday_time_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query

        back_button = [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="birthday_menu")]
        keyboard = [back_button]

        settings = await SettingsRepository.get_last()
        time_now = settings.get("birthday_sending_time") if settings is not None else "10:00"
        reply_text = f"{time_now}, \nФормат: 12:12"

        await query.edit_message_text(
            text=reply_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return "input_new_birthday_time"

    @staticmethod
    async def input_new_birthday_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        text = validate_time(to_validate=text)
        if text is None:
            await update.message.reply_text(text=" час")
            await AdminSettings.change_birthday_time_broadcast(update, context)
            return ConversationHandler.END
        values = {"birthday_sending_time": str(text)}
        settings_id = await SettingsRepository.create(values)

        scheduler = ScheduleRepository.scheduler
        ScheduleRepository.delete_task(scheduler, "birthday_cron")
        ScheduleRepository.add_task(
            scheduler=scheduler,
            task_id="birthday_cron",
            callback=ChatEventsRepository.send_postcard,
            task_type="day",
            run_time=text,
        )

        await AdminSettings.get_menu(update, context)
        return ConversationHandler.END

    @staticmethod
    async def notification_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        reply_text = make_long_length("👽  при ")
        keyboard = [
            [InlineKeyboardButton(text="➕ ", callback_data="create_join_notification")],
            [InlineKeyboardButton(text="👁 ", callback_data="get_join_notification")],
            [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="settings_menu")]
        ]

        if query is None:
            await update.message.reply_text(
                quote=False,
                text=reply_text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ConversationHandler.END

        await query.answer()
        await query.edit_message_text(
            text=reply_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    @staticmethod
    async def create_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        back_button = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="settings_menu")]]

        if query is None:
            await update.message.reply_text(
                quote=False,
                text=reply_text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(back_button)
            )
            return "save_join_notification"

        await query.answer()
        await query.edit_message_text(
            text=reply_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(back_button)
        )
        return "save_join_notification"

    @staticmethod
    async def save_join_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
        values: dict = await collect_message(update, context)
        values["type"] = POST_TYPE.NOTIFICATION
        await PostsRepository.create(values)
        return await AdminSettings.get_menu(update, context)

    @staticmethod
    async def get_join_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(query.from_user.id)
        notification = await PostsRepository.get_join_notification()
        back_button = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="admin_settings_delete_previous")]]

        if notification is None:
            back_button = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="filling_reminder_menu")]]
            await query.answer()
            await query.edit_message_text(
                reply_markup=InlineKeyboardMarkup(back_button)
            )
            return "save_join_notification"

        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=query.message.id
        )
        message = await send_message_from_bot(chat_id=chat_id, values=notification, bot=context.bot)
        await context.bot.send_message(
            chat_id=chat_id,
            reply_markup=InlineKeyboardMarkup(back_button)

        )
        return ConversationHandler.END

    @staticmethod
    async def filling_reminder_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        reply_text = make_long_length("<")
        keyboard = [
        ]
        if query is None:
            await update.message.reply_text(
                quote=False,
                text=reply_text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ConversationHandler.END

        await query.answer()
        await query.edit_message_text(
            text=reply_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    @staticmethod
    async def create_filling_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        reply_text = make_long_length("<b>")
        keyboard = [
            [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="filling_reminder_menu")]
        ]
        if query is None:
            await update.message.reply_text(
                quote=False,
                text=reply_text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return "save_filling_reminder"

        await query.answer()
        await query.edit_message_text(
            text=reply_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return "save_filling_reminder"

    @staticmethod
    async def save_filling_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_values = await collect_message(update, context)
        message_values["type"] = POST_TYPE.REMINDER
        message_values.pop("sending_date")
        await PostsRepository.create(values=message_values)
        await AdminSettings.get_menu(update, context)
        return ConversationHandler.END

    @staticmethod
    async def input_new_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        settings = await SettingsRepository.get_last()
        time_now = settings.get("reminder_sending_time") if settings is not None and settings.get("reminder_sending_time") is not None else "10:00"
        server_time = datetime.datetime.now().strftime("%H:%M")
        keyboard = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="filling_reminder_menu")]]

        if query is None:
            await update.message.reply_text(
                quote=False,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return "save_new_reminder_time"

        await query.answer()
        await query.edit_message_text(
            text=reply_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return "save_new_reminder_time"

    @staticmethod
    async def save_new_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        text = validate_time(to_validate=text)

        if text is None:
            await AdminSettings.input_new_reminder_time(update, context)
            return ConversationHandler.END

        settings_values = await SettingsRepository.get_last()

        if settings_values is None:
            settings_values = {"reminder_sending_time": text}
        elif settings_values:
            settings_values["reminder_sending_time"] = text
            settings_values.pop("id")

        settings_id = await SettingsRepository.create(settings_values)

        scheduler = ScheduleRepository.scheduler
        ScheduleRepository.delete_task(scheduler, "reminder_cron")
        ScheduleRepository.add_task(
            scheduler=scheduler,
            task_id="reminder_cron",
            callback=ChatEventsRepository.send_reminder,
            task_type="day",
            run_time=text,
        )

        await AdminSettings.get_menu(update, context)
        return ConversationHandler.END

    @staticmethod
    async def get_reminder_filler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        chat_id = str(query.from_user.id)
        reminder = await PostsRepository.get_reminder()
        settings = await SettingsRepository.get_last()
        button_text = settings.get("reminder_button_text") if settings is not None and settings.get(
            "reminder_button_text") is not None else "Validate me"
        reminder_button = [[InlineKeyboardButton(text=button_text, callback_data="NNNNN")]]
        reminder_markup = InlineKeyboardMarkup(reminder_button)
        back_button = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="admin_settings_delete_previous")]]

        if reminder is None:
            back_button = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="filling_reminder_menu")]]
            await query.edit_message_text(
                reply_markup=InlineKeyboardMarkup(back_button)
            )
            return "save_postcard"

        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=query.message.id
        )
        await send_message_from_bot(
            chat_id=chat_id,
            values=reminder,
            bot=context.bot,
            button=reminder_markup
        )
        await context.bot.send_message(
            chat_id=chat_id,
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode=ParseMode.HTML,

        )
        return ConversationHandler.END

    @staticmethod
    async def reminder_change_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        settings = await SettingsRepository.get_last()
        text_now = settings.get("reminder_button_text") if settings is not None and settings.get(
            "reminder_button_text") is not None else "ТЕКСТ КНОПКИ"
        keyboard = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="filling_reminder_menu")]]

        if query is None:
            await update.message.reply_text(
                quote=False,
                text=reply_text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return "save_new_reminder_button_text"

        await query.answer()
        await query.edit_message_text(
            text=reply_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return "save_new_reminder_button_text"

    @staticmethod
    async def save_new_reminder_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        settings_values = await SettingsRepository.get_last()

        if settings_values is None:
            settings_values = {"reminder_button_text": text}
        elif settings_values:
            settings_values["reminder_button_text"] = str(text)
            settings_values.pop("id")

        settings_id = await SettingsRepository.create(settings_values)
        await AdminSettings.get_menu(update, context)
        return ConversationHandler.END

    @staticmethod
    async def delete_previous_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(query.from_user.id)
        await query.answer()
        await context.bot.delete_message(chat_id=chat_id, message_id=query.message.id - 1)
        await AdminSettings.get_menu(update, context)
        return ConversationHandler.END