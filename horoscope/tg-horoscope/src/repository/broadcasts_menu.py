import datetime
import os
from core.config import BACK_BUTTON_TEXT, DATETIME_FORMAT, ARROW_LEFT, ARROW_RIGHT
from repository.tools import (
    keyboard_cols,
    convert_str_date,
    collect_message,
    add_unexpected_date,
    send_message_from_bot,
    make_long_length
)
from repository.schedule_logic import ScheduleRepository
from repository.chat_events import ChatEventsRepository
from repository.database.posts import PostsRepository, POST_TYPE
from repository.decorators import auto_delete_message
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode


class BroadcastsMenu:

    @staticmethod
    #@auto_delete_message
    async def store_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.message.chat_id)
        values = await collect_message(update, context)
        context.bot_data.update({f"{chat_id}:broadcast-create": {"values": values}})

    @staticmethod
    #@auto_delete_message
    async def get_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        keyboard = [
        ]
        if query is not None:
            chat_id = str(query.from_user.id)
            await query.answer()
            await query.edit_message_text(
                text=reply_text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(
                quote=False,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        return ConversationHandler.END

    @staticmethod
    async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        keyboard = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="broadcasts_menu")]]
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return "get_broadcast_content"

    @staticmethod
    async def get_broadcast_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await BroadcastsMenu.store_message(update, context)
        await update.message.reply_text(
            quote=False,
            parse_mode=ParseMode.HTML
        )
        return "save_broadcast"

    @staticmethod
    async def save_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        chat_id = update.message.chat_id
        user_data = context.bot_data[f"{chat_id}:broadcast-create"]

        text = add_unexpected_date(text)
        date_obj = datetime.datetime.strptime(text, '%H:%M %d.%m.%Y')
        formatted_date_str = date_obj.strftime(DATETIME_FORMAT)
        formatted_date = datetime.datetime.strptime(formatted_date_str, DATETIME_FORMAT)

        user_data["values"]["sending_date"] = formatted_date
        user_data["values"]["type"] = POST_TYPE.AD
        broadcast_id = await PostsRepository.create(user_data["values"])
        user_data["values"]["id"] = broadcast_id
        await update.message.reply_text(
            quote=False,
            text=f"Розсилка буде відправлена о {text}"
        )

        scheduler = ScheduleRepository.scheduler
        ScheduleRepository.add_task(
            scheduler=scheduler,
            callback=ChatEventsRepository.send_message,
            run_time=str(user_data["values"]["sending_date"]),
            to_send=user_data["values"]
        )

        del context.bot_data[f"{chat_id}:broadcast-create"]
        return ConversationHandler.END

    @staticmethod
    async def get_scheduled(update: Update, context: ContextTypes.DEFAULT_TYPE, is_over: bool = True):
        query = update.callback_query
        await query.answer()
        scheduled_broadcasts = await PostsRepository.get_scheduled_broadcast(is_over=is_over)
        back_button = [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="broadcasts_menu")]

        if len(scheduled_broadcasts) == 0:
            await query.edit_message_text(text="No scheduled broadcasts.", reply_markup=InlineKeyboardMarkup([back_button]))
            return ConversationHandler.END

        existing_dates = []
        keyboard = []

        for broadcast in scheduled_broadcasts:

            if broadcast["sending_date"].strftime("%d.%m.%Y %H:%M") not in existing_dates:
                existing_dates.append(broadcast["sending_date"].strftime("%d.%m.%Y %H:%M"))
                keyboard.append(InlineKeyboardButton(
                        text=broadcast["sending_date"].strftime("%d.%m.%Y %H:%M"),
                        callback_data=f"broadcasts_select_date,{broadcast['sending_date']}"
                    )
                )

        keyboard = keyboard_cols(keyboard, 2)
        keyboard = keyboard
        keyboard.append(back_button)

        if is_over:
            await query.edit_message_text(
                text=make_long_length("Заплановані дати."),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif not is_over:
            await query.edit_message_text(
                text=make_long_length("Попередні дати."),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return ConversationHandler.END

    @staticmethod
    async def get_sent(update: Update, context: ContextTypes.DEFAULT_TYPE, is_over: bool = False):
        return await BroadcastsMenu.get_scheduled(update, context, is_over)

    @staticmethod
    async def paging_select_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
        from repository.tools import paging
        query = update.callback_query
        data = query.data.split(",")
        page = int(data[2])
        return await paging(
            callback=BroadcastsMenu.select_date,
            update=update,
            context=context,
            _page=page,
        )

    @staticmethod
    async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE, _page: int = 1):
        query = update.callback_query
        await query.answer()
        data = query.data.split(",")
        page = _page if len(data) != 3 else int(data[2])
        broadcasts_date = convert_str_date(data[1])
        scheduled_date = await PostsRepository.get_by_date(date=broadcasts_date, skip=page-1)

        keyboard = [
            InlineKeyboardButton(
                text=b["html"][:11] + "...",
                callback_data=f"broadcast_current,{b['id']}")
            for b in scheduled_date
        ]
        back_button = [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="broadcasts_menu")]
        arrow_left = InlineKeyboardButton(text=ARROW_LEFT, callback_data=f"broadcasts_date_paging,{broadcasts_date},{page - 1}")
        arrow_right = InlineKeyboardButton(text=ARROW_RIGHT, callback_data=f"broadcasts_date_paging,{broadcasts_date},{page + 1}")
        arrow_buttons = []

        if page > 1:
            arrow_buttons.append(arrow_left)
        if len(scheduled_date) > 13:
            arrow_buttons.append(arrow_right)

        keyboard = keyboard_cols(keyboard, 2)
        keyboard = keyboard
        keyboard.append(arrow_buttons)
        keyboard.append(back_button)

        await query.edit_message_text(text=make_long_length("розсилки"),
                                      reply_markup=InlineKeyboardMarkup(keyboard))

        return ConversationHandler.END

    @staticmethod
    async def select_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query

    @staticmethod
    async def delete_previous_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(query.from_user.id)
        await query.answer()
        await context.bot.delete_message(chat_id=chat_id, message_id=query.message.id - 1)
        await BroadcastsMenu.get_menu(update, context)
        return ConversationHandler.END
