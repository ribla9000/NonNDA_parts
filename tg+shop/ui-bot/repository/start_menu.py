from core.config import BACK_BUTTON_TEXT, SUPERADMIN_IDS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat, Bot
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from repository.database.users import UsersRepository
from repository.tools import create_unique_key


class StartMenu:

    @staticmethod
    async def get_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        user = await UsersRepository.get_by_chat_id(chat_id)
        values = {
            "name": update.message.from_user.full_name if update.message is not None else query.from_user.full_name,
            "nickname": update.message.from_user.username if update.message is not None else query.from_user.username,
            "chat_id": chat_id,
            "ukey": create_unique_key(),
        }

        if user is None and chat_id not in SUPERADMIN_IDS:
            await UsersRepository.create(values)
            await StartMenu.get_menu(update, context)
            return ConversationHandler.END
        elif user is None and chat_id in SUPERADMIN_IDS:
            values["role"] = "admin"
            await UsersRepository.create(values)
            await StartMenu.get_menu(update, context)
            return ConversationHandler.END

        if user["role"] == "admin":
            await StartMenu._menu_admin(update, context)
            return ConversationHandler.END
        elif user["role"] == "partner":
            await StartMenu._menu_partner(update, context)
            return ConversationHandler.END
        return ConversationHandler.END

    @staticmethod
    async def _menu_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        reply_text = "You are in the partner menu"
        keyboard = [
            [InlineKeyboardButton(text="Products", callback_data="partner_products"),
             InlineKeyboardButton(text="Orders", callback_data="partner_orders")],
            # [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="start_menu")]
        ]

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
            return ConversationHandler.END

        await query.edit_message_text(text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    @staticmethod
    async def _menu_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        reply_text = "You are in admin menu"
        keyboard = [
            [InlineKeyboardButton(text="products", callback_data="admin_products")],
            [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="start_menu")]
        ]

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
            return ConversationHandler.END

        await query.edit_message_text(text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END
