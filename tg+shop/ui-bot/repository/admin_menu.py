import asyncio
import datetime
import json
import os
import time
from core.config import BACK_BUTTON_TEXT
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat, Bot
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from repository.tools import keyboard_cols
from repository.database.products import ProductRepository
from repository.database.posts import PostsRepository


class AdminMenu:

    @staticmethod
    async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        reply_text = "Products Menu"
        keyboard = [
            [InlineKeyboardButton(text="Add", callback_data="admin_add_product")],
            [InlineKeyboardButton(text="List", callback_data="admin_list_products")]
        ]

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
            return ConversationHandler.END

        await query.edit_message_text(text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    @staticmethod
    async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        reply_text = "Text a Title"
        context.bot_data[f"{chat_id}:add-post"] = {}

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text)
            return "product_add_price"

        await query.edit_message_text(text=reply_text)
        return "product_add_price"

    @staticmethod
    async def add_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        text = update.message.text
        reply_text = "Text a price. Format: 200.99"
        userdata = context.bot_data[f"{chat_id}:add-post"]
        userdata["title"] = text

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text)
            return "product_add_url"

        await query.edit_message_text(text=reply_text)
        return "product_add_url"

    @staticmethod
    async def add_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        reply_text = "Text a url for the post"
        text = update.message.text
        userdata = context.bot_data[f"{chat_id}:add-post"]
        userdata["price"] = int(float(text) * 100)

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text)
            return "product_add_post"

        await query.edit_message_text(text=reply_text)
        return "product_add_post"

    @staticmethod
    async def add_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        reply_text = ("Add post")
        text = update.message.text
        userdata = context.bot_data[f"{chat_id}:add-post"]
        userdata["url"] = text

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text)
            return "product_save"

        await query.edit_message_text(text=reply_text)
        return "product_save"

    @staticmethod
    async def product_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        reply_text = ("Good job")
        html = update.message.text_html

        userdata = context.bot_data[f"{chat_id}:add-post"]
        product_id = await ProductRepository.create(userdata)
        post_data = {
            "html": html,
            "product_id": product_id,
            "is_ad": False,
        }
        post_id = await PostsRepository.create(post_data)
        del userdata

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text)
            await AdminMenu.products(update, context)
            return ConversationHandler.END

        await query.edit_message_text(text=reply_text)
        await AdminMenu.products(update, context)
        return ConversationHandler.END

    @staticmethod
    async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        reply_text = "Products Menu"
        products = await ProductRepository.get_all()
        back_button = [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="admin_products")]
        keyboard = [InlineKeyboardButton(text=item["title"], callback_data=f"admin_product,{item['id']}") for item in products]
        keyboard = keyboard_cols(keyboard, 2)
        keyboard.append(back_button)

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
            return ConversationHandler.END

        await query.edit_message_text(text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    @staticmethod
    async def current_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        data = query.data.split(",")
        product_id = int(data[1])
        product = await ProductRepository.get_by_id(product_id)
        reply_text = f"Your product is: {product['title']}"
        back_button = [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="admin_list_products")]
        keyboard = [
            [InlineKeyboardButton(text="Edit", callback_data=f"admin_edit_product,{product_id}"),
             InlineKeyboardButton(text="Add product ad", callback_data=f"admin_add_ad,{product_id}")],
            back_button
        ]

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
            return ConversationHandler.END

        await query.edit_message_text(text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    @staticmethod
    async def edit_product():
        pass

    @staticmethod
    async def product_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        data = query.data.split(",")
        product_id = int(data[1])
        context.bot_data[f"{chat_id}:create-ad-post"] = {"product_id": product_id}
        reply_text = f"Text a post as ad for product"

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text)
            return "save_ad_post"

        await query.edit_message_text(text=reply_text)
        return "save_ad_post"

    @staticmethod
    async def save_ad_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        html = update.message.text_html
        userdata = context.bot_data[f"{chat_id}:create-ad-post"]
        userdata["html"], userdata["is_ad"] = html, True
        await PostsRepository.create(userdata)
        del userdata
        await AdminMenu.list_products(update, context)
        return ConversationHandler.END
