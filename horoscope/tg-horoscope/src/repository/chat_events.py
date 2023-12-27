import asyncio
import datetime


class ChatEventsRepository:

    @staticmethod
    async def send_message(to_send: dict):
        users = await UsersRepository.get_unblocked()
        bot = Bot(token=HOROSCOPE_BOT_TOKEN)
        await bot.initialize()

        for user in users:
            if user["is_blocked"] or user["role"] == ROLES["ADMIN"] or user["chat_id"] in SUPERADMIN_IDS:
                continue

            try:
                message = await send_message_from_bot(
                    chat_id=user["chat_id"],
                    values=to_send,
                    bot=bot,
                )
            except Exception as e:
                if BLOCKED_BY_USER in str(e):
                    await UsersRepository.update(id=user["id"], values={"is_blocked": True})
                else:
                    print(e)
                continue

            values = {
                "html": message.text_html,
                "message_id": message.message_id,
                "from_chat_id": str(message.from_user.id),
                "to_chat_id": str(message.chat.id),
                "date_created": datetime.datetime.now(),
                "is_bot": message.from_user.is_bot,
                "event_name": "send_message",
            }
            message_id = await MessagesRepository.create(values)
            deleting_values = {
                "message_id": message_id,
                "type": MESSAGE_TYPES.BROADCAST,
                "deleting_date": datetime.datetime.now() + datetime.timedelta(seconds=10),
            }
            await MessagesRepository.to_delete(deleting_values)
            await PostsRepository.make_sent(post_id=to_send["id"], user_id=user["id"])

        await bot.close()

    @staticmethod
    async def send_message_on_hour():
        hour_now = (datetime.datetime.now()).strftime("%H:00")
        date = (datetime.datetime.now()).date()
        personals = await PersonalInfoRepository.get_by_time(hour_now)

        if personals is None or len(personals) == 0:
            return None

        bot = Bot(token=HOROSCOPE_BOT_TOKEN)
        await bot.initialize()

        ind = 0
        for personal in personals:
            user = await UsersRepository.get_by_chat_id(chat_id=personal["chat_id"])
            if ind != 0 and ind % 20 == 0:
                await asyncio.sleep(1)

            if user is not None and user["is_blocked"] or user is None:
                continue

            content = await PostsRepository.get_by_sign(sign_id=personal["sign_id"], date=date)

            if content is None:
                print(f"add content to date, {date}, on sign_id {personal['sign_id']}")
                continue

            last_sent = await PostsRepository.get_last_sent(chat_id=personal["chat_id"])

            if last_sent is not None and last_sent.get("post_id") == content["id"]:
                continue
            elif last_sent is None or last_sent is not None and last_sent.get("post_id") != content["id"]:
                try:
                    reply_text = parse_content_constants(
                        con=content["html"],
                        bc=BEFORE_CONTENT,
                        ac=AFTER_CONTENT,
                        date=date.strftime("%d.%m.%Y"),
                        name=personal["name"]
                    )
                    message = await send_message_from_bot(
                        chat_id=personal["chat_id"],
                        values=content,
                        bot=bot,
                        send_text=reply_text
                    )
                    await bot.send_message(
                        chat_id=personal["chat_id"],
                        text=f"<b>Гороскоп на завтра</b> тобі надійде автоматично о <b>{personal['broadcast_time']}</b>",
                        parse_mode=ParseMode.HTML
                    )
                except Exception as e:

                    if BLOCKED_BY_USER in str(e):
                        user = await UsersRepository.get_by_chat_id(chat_id=personal["chat_id"])
                        await UsersRepository.update(id=user["id"], values={"is_blocked": True})
                    else:
                        print(e)
                    continue

                values = {
                    "html": content["html"],
                    "message_id": message.id,
                    "from_chat_id": str(message.from_user.id),
                    "to_chat_id": str(message.chat.id),
                    "date_created": datetime.datetime.now(),
                    "is_bot": message.from_user.is_bot,
                    "event_name": "send_message_on_hour",
                }
                message_id = await MessagesRepository.create(values)
                deleting_values = {
                    "message_id": message_id,
                    "type": MESSAGE_TYPES.HOROSCOPE,
                    "deleting_date": None,
                }
                await MessagesRepository.to_delete(deleting_values)
                await PostsRepository.make_sent(user_id=personal["user_id"], post_id=content["id"])
                ind += 1

        await bot.close()

    @staticmethod
    async def delete_messages():
        to_delete = await MessagesRepository.get_to_delete()
        bot = Bot(token=HOROSCOPE_BOT_TOKEN)
        await bot.initialize()

        for item in to_delete:
            await bot.delete_message(chat_id=item["to_chat_id"], message_id=item["message_id"])
            await MessagesRepository.make_deleted(message_id=item["id"])

        await bot.close()

    @staticmethod
    async def send_sorry(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            trc = (traceback.format_exception(None, value=context.error, tb=context.error.__traceback__, chain=True))
            text_to_support = " ".join([i for i in trc])
            sentry_sdk.capture_exception(context.error)
            query = update.callback_query
            chat_id = str(update.message.chat_id if query is None else query.from_user.id)
            user = await UsersRepository.get_by_chat_id(chat_id)

            if BLOCKED_BY_USER in str(context.error):
                await UsersRepository.update({"is_blocked": True}, id=user["id"])
                return
            if MESSAGE_NOT_FOUND in str(context.error):
                return
            if chat_id is None:
                return

            reply_text = "Щось пішло не так :("
            if user is not None and user["role"] == ROLES["ADMIN"] or chat_id in SUPERADMIN_IDS:
                await context.bot.send_message(chat_id=chat_id, text=text_to_support)
                return None

            await context.bot.send_message(chat_id=chat_id, text=reply_text)
            return None

        except Exception as e:
            print(e)
            raise e

    @staticmethod
    async def send_postcard():
        bot = Bot(token=HOROSCOPE_BOT_TOKEN)
        await bot.initialize()
        today = datetime.datetime.now().date()
        today = today.strftime("%d.%m")
        personals = await PersonalInfoRepository.get_by_birthday(today)
        postcard = await PostsRepository.get_postcard()

        for item in personals:
            user = await UsersRepository.get_by_chat_id(chat_id=item["chat_id"])
            if user["is_blocked"]:
                continue

            message = await send_message_from_bot(
                chat_id=user["chat_id"],
                values=postcard,
                bot=bot
            )

        await bot.close()

    @staticmethod
    async def send_reminder():
        bot = Bot(token=HOROSCOPE_BOT_TOKEN)
        await bot.initialize()
        personals = await PersonalInfoRepository.get_without_personal()
        reminder = await PostsRepository.get_reminder()

        if reminder is None:
            return

        settings = await SettingsRepository.get_last()
        button_text = settings["reminder_button_text"] if settings is not None and settings.get("reminder_button_text") is not None else "Validate"
        reminder_button = [[InlineKeyboardButton(text=button_text, callback_data="create_personal,False")]]
        reply_markup = InlineKeyboardMarkup(reminder_button)

        for item in personals:
            user = await UsersRepository.get_by_chat_id(chat_id=item["chat_id"])

            if (user["is_blocked"]
            or user["role"] == ROLES["ADMIN"]
            or (datetime.datetime.now() - user["created_at"]) < datetime.timedelta(days=1)):
                continue

            try:
                message = await send_message_from_bot(
                    chat_id=user["chat_id"],
                    values=reminder,
                    bot=bot,
                    button=reply_markup
                )
            except:
                continue

        await bot.close()

    @staticmethod
    async def check_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
        join_request = update.chat_join_request
        personal = await PersonalInfoRepository.get_by_chat_id(str(join_request.from_user.id))
        user = await UsersRepository.get_by_chat_id(str(join_request.from_user.id))

        if user is None:
            values = {
                "nickname": join_request.from_user.username,
                "name": join_request.from_user.full_name,
                "chat_id": str(join_request.from_user.id)
            }
            await UsersRepository.create(values)

        if personal:
            return

        messages = await MessagesRepository.get_by_type(chat_id=str(join_request.from_user.id), type=MESSAGE_TYPES.PRESENT_NOTIFY)
        for item in messages:
            message = await MessagesRepository.get_by_id(item["message_id"])
            try:
                await context.bot.delete_message(chat_id=message["to_chat_id"], message_id=message["message_id"])
                await MessagesRepository.make_deleted(message["id"])
            except Exception as e:
                print(e)
                continue

        validate_button = [[KeyboardButton(text="Отримати гороскоп")]]
        broadcast = await PostsRepository.get_join_notification()

        if broadcast is None:
            return

        image_path = broadcast["image_path"]

        if image_path is None:
            message = await join_request.from_user.send_message(
                text=broadcast["html"],
                reply_markup=ReplyKeyboardMarkup(validate_button, one_time_keyboard=True, resize_keyboard=True),
                parse_mode=ParseMode.HTML
            )
        else:
            message = await join_request.from_user.send_photo(
                caption=broadcast["html"],
                photo=image_path,
                reply_markup=ReplyKeyboardMarkup(validate_button, one_time_keyboard=True, resize_keyboard=True),
                parse_mode=ParseMode.HTML
            )

        values = {
            "message_id": message.id,
            "from_chat_id": str(message.from_user.id),
            "to_chat_id": str(message.chat_id),
            "is_bot": True,
            "event_name": "check_join_request",
            "date_created": datetime.datetime.now(),
        }
        message_id = await MessagesRepository.create(values)
        values = {
            "message_id": message_id,
            "type": MESSAGE_TYPES.PRESENT_NOTIFY,
        }
        await MessagesRepository.to_delete(values)

