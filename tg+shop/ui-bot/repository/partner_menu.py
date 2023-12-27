import asyncio
import datetime
import json
import os
import time
from core.config import BACK_BUTTON_TEXT
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat, Bot
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from repository.database.products import ProductRepository
from repository.database.posts import PostsRepository
from repository.database.users import UsersRepository
from repository.database.orders import OrdersRepository
from db.orders import STATUS
from repository.tools import keyboard_cols


class PartnerMenu:

    @staticmethod
    async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        reply_text = "Products Menu"
        products = await ProductRepository.get_all()

        back_button = [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="start_menu")]
        keyboard = [InlineKeyboardButton(text=item["title"], callback_data=f"partner_select_product,{item['id']}") for item in products]
        keyboard = keyboard_cols(keyboard, 2)
        keyboard = keyboard
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
        product_info = await PostsRepository.get_by_product(product_id=product_id, is_ad=False)
        reply_text = (f"Your product is: <b>{product['title']}</b>"
                      f"\n\n"
                      f"👁‍🗨Product info:\n"
                      f"{product_info['html']}")

        back_button = [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="partner_products")]
        keyboard = [
            [InlineKeyboardButton(text="Show Product AD posts", callback_data=f"partner_product_ad,{product['id']}"),
             InlineKeyboardButton(text="Get unique link", callback_data=f"partner_unique_link,{product['id']}")],
            back_button
        ]

        if query is None:
            await update.message.reply_text(
                quote=False,
                text=reply_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            return ConversationHandler.END

        await query.edit_message_text(
            text=reply_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

    @staticmethod
    async def show_product_ad_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        data = query.data.split(",")
        product_id = int(data[1])
        posts = await PostsRepository.get_by_product(product_id=product_id, is_ad=True)
        reply_text = f"Posts:" + "ㅤ "*15

        back_button = [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data=f"partner_select_product,{product_id}")]
        keyboard = [InlineKeyboardButton(text=item["html"][:20], callback_data=f"partner_select_post,{item['id']},{product_id}") for item in posts]
        keyboard = keyboard_cols(keyboard, 2)
        keyboard = keyboard
        keyboard.append(back_button)

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
            return ConversationHandler.END

        await query.edit_message_text(text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    @staticmethod
    async def current_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        data = query.data.split(",")
        post_id = int(data[1])
        product_id = int(data[2])
        user = await UsersRepository.get_by_chat_id(chat_id)
        product = await ProductRepository.get_by_id(product_id)
        post = await PostsRepository.get_by_id(post_id)
        reply_text = (f"{post['html']}\n\n"
                      f"{product['url']}/{user['ukey']}")

        back_button = [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data=f"partner_select_product,{product_id}")]
        keyboard = [back_button]

        if query is None:
            await update.message.reply_text(quote=False, text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
            return ConversationHandler.END

        await query.edit_message_text(text=reply_text,
                                      reply_markup=InlineKeyboardMarkup(keyboard),
                                      parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    @staticmethod
    async def get_unique_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        data = query.data.split(",")
        product_id = int(data[1])
        product = await ProductRepository.get_by_id(product_id)
        user = await UsersRepository.get_by_chat_id(chat_id)
        reply_text = (f"Product: <b>{product['title']}</b>"
                      f"\n"
                      f"Partner link on product: <code>{product['url']}/{user['ukey']}</code>"
                      f"\n"
                      f"partner link: <code>{user['ukey']}</code>")

        keyboard = [[InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data=f"partner_select_product,{product_id}")]]

        await query.edit_message_text(
            text=reply_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )

    @staticmethod
    async def orders_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        data = query.data.split(",")
        page = int(data[1]) if len(data) > 1 else 0
        chat_id = str(update.message.chat_id if query is None else query.from_user.id)
        user = await UsersRepository.get_by_chat_id(chat_id)
        orders = await OrdersRepository.get_by_user(user_id=user["id"], skip=page)
        keyboard = []
        back_button = [InlineKeyboardButton(text=BACK_BUTTON_TEXT, callback_data="start_menu")]
        keyboard.append(back_button)

        if len(orders) == 0:
            await query.edit_message_text(text="No orders have been found", reply_markup=InlineKeyboardMarkup(keyboard))
            return ConversationHandler.END

        await query.delete_message()

        unique_orders = set()

        for order in orders:
            unique_orders.add(order["product_id"])

        for uorder in unique_orders:
            product = await ProductRepository.get_by_id(uorder)
            delivered = await OrdersRepository.get_count(
                status=STATUS["DELIVERED"],
                user_id=user["id"],
                product_id=uorder)
            intransit = await OrdersRepository.get_count(
                status=STATUS["INTRASIT"],
                user_id=user["id"],
                product_id=uorder)
            cancelled = await OrdersRepository.get_count(
                status=STATUS["CANCELED"],
                user_id=user["id"],
                product_id=uorder)
            reply_text = (f"<pre>Product: {product['title']}\n"
                          f"✔️Delivered: {delivered}\n"
                          f"🚚In transit: {intransit}\n"
                          f"♦️Cancelled: {cancelled}</pre>")
            await context.bot.send_message(chat_id=chat_id, text=reply_text, parse_mode=ParseMode.HTML)

        button_confirm = [InlineKeyboardButton(text="Yes, show next", callback_data=f"partner_orders,{page+1}")]
        keyboard.append(button_confirm)
        keyboard[0], keyboard[1] = keyboard[1], keyboard[0]
        await context.bot.send_message(
            chat_id=chat_id,
            text="Show 5 next?" + " ㅤ"*10,
            reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END
