from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat, Bot
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from repository.decorators import auto_delete_message
from repository.tools import make_long_length


class AdminMenu:

    @staticmethod
    #@auto_delete_message
    async def get_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        keyboard = [
            [InlineKeyboardButton(text="💌 ", callback_data="")],
            [InlineKeyboardButton(text="♋ ", callback_data="")],
            [InlineKeyboardButton(text="📊 ", callback_data="")],
            [InlineKeyboardButton(text="⚙️ ", callback_data="")]
        ]
        if query is None:
            await update.message.reply_text(
                quote=False,
                text=make_long_length(""),
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ConversationHandler.END

        await query.answer()
        await query.edit_message_text(
            text=make_long_length(""),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END
