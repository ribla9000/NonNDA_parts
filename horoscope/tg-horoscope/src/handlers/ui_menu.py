from telegram.ext import (
    CommandHandler, Application, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters, ChatJoinRequestHandler
)
from repository.start_menu import StartMenu
from repository.broadcasts_menu import BroadcastsMenu
from repository.admin_menu import AdminMenu
from repository.content_menu import ContentMenu
from repository.statistics_menu import StatisticsMenu
from repository.chat_events import ChatEventsRepository
from repository.settings_menu import SettingsMenu


start_menu_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", StartMenu.get_menu),
        MessageHandler(callback=StartMenu.create_personal, filters=filters.Regex("")),
        CallbackQueryHandler(callback=StartMenu.get_menu, pattern=""),
        CallbackQueryHandler(callback=StartMenu.receive_broadcast, pattern=""),
        CallbackQueryHandler(callback=StartMenu.save_user_data, pattern=""),
        CallbackQueryHandler(callback=StartMenu.get_horoscope, pattern=""),
        CallbackQueryHandler(callback=StartMenu.create_personal, pattern=""),
        CommandHandler(callback=SettingsMenu.User.get_menu, command="")
    ],
    states={
        "": [MessageHandler(callback=StartMenu.input_name, filters=filters.TEXT)],
        "": [MessageHandler(callback=StartMenu.input_birthday_time, filters=filters.TEXT)],
        "": [MessageHandler(callback=StartMenu.choose_gender, filters=filters.TEXT)],
    },
    allow_reentry=True,
    fallbacks=[],
)
broadcast_menu_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=BroadcastsMenu.get_menu, pattern=""),
        CallbackQueryHandler(callback=BroadcastsMenu.create, pattern=""),
        CallbackQueryHandler(callback=BroadcastsMenu.get_scheduled, pattern=""),
        CallbackQueryHandler(callback=BroadcastsMenu.select_date, pattern=""),
        CallbackQueryHandler(callback=BroadcastsMenu.select_broadcast, pattern=""),
        CallbackQueryHandler(callback=BroadcastsMenu.get_sent, pattern=""),
        CallbackQueryHandler(callback=BroadcastsMenu.delete_previous_message, pattern=""),
        CallbackQueryHandler(callback=BroadcastsMenu.paging_select_date, pattern="")
    ],
    states={
        "get_broadcast_content": [MessageHandler(callback=BroadcastsMenu.get_broadcast_content, filters=filters.ALL)],
        "save_broadcast": [MessageHandler(callback=BroadcastsMenu.save_broadcast, filters=filters.TEXT)]
    },
    allow_reentry=True,
    fallbacks=[],
)
admin_menu_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=AdminMenu.get_menu, pattern=""),
    ],
    states={},
    allow_reentry=True,
    fallbacks=[],
)
content_menu_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=ContentMenu.get_menu, pattern=""),
        CallbackQueryHandler(callback=ContentMenu.create, pattern=""),
        CallbackQueryHandler(callback=ContentMenu.get_scheduled, pattern=""),
        CallbackQueryHandler(callback=ContentMenu.get_date, pattern=""),
        CallbackQueryHandler(callback=ContentMenu.get_content, pattern=""),
        CallbackQueryHandler(callback=ContentMenu.create_single, pattern=""),
        CallbackQueryHandler(callback=ContentMenu.select_single, pattern=""),
        CallbackQueryHandler(callback=ContentMenu.change_single_date, pattern=""),
        CallbackQueryHandler(callback=ContentMenu.delete_previous_message, pattern=""),
        CallbackQueryHandler(callback=ContentMenu.paging_get_scheduled, pattern="")
    ],
    states={
        "": [MessageHandler(callback=ContentMenu.save_content, filters=filters.TEXT)],
        "": [MessageHandler(callback=ContentMenu.save_single, filters=filters.ALL)],
        "": [MessageHandler(callback=ContentMenu.input_new_date, filters=filters.TEXT)],
    },
    allow_reentry=True,
    fallbacks=[],
)
statistics_menu_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=StatisticsMenu.get_menu, pattern=""),
    ],
    states={},
    allow_reentry=True,
    fallbacks=[],
)
settings_menu_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=SettingsMenu.get_menu, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.birthday_menu, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.create_postcard, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.get_postcard, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.change_birthday_time_broadcast, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.get_birthday_members, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.notification_menu, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.create_notification, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.get_join_notification, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.delete_previous_message, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.filling_reminder_menu, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.create_filling_reminder, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.input_new_reminder_time, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.get_reminder_filler, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.Admin.reminder_change_button_text, pattern=""),

        CallbackQueryHandler(callback=SettingsMenu.User.change_receive_broadcasts, pattern=""),
        CallbackQueryHandler(callback=SettingsMenu.User.save_new_receive_broadcasts_time, pattern="")
    ],
    states={
        "": [MessageHandler(callback=SettingsMenu.Admin.save_postcard, filters=filters.ALL)],
        "": [MessageHandler(callback=SettingsMenu.Admin.input_new_birthday_time, filters=filters.TEXT)],
        "": [MessageHandler(callback=SettingsMenu.Admin.save_join_notification, filters=filters.ALL)],
        "": [MessageHandler(callback=SettingsMenu.Admin.save_filling_reminder, filters=filters.ALL)],
        "": [MessageHandler(callback=SettingsMenu.Admin.save_new_reminder_time, filters=filters.TEXT)],
        "": [MessageHandler(callback=SettingsMenu.Admin.save_new_reminder_button_text, filters=filters.TEXT)]
    },
    allow_reentry=True,
    fallbacks=[],
)

join_request_handler = ConversationHandler(
    entry_points=[ChatJoinRequestHandler(callback=ChatEventsRepository.check_join_request)],
    states={},
    allow_reentry=True,
    fallbacks=[],
)


def add_handlers(application: Application):
    application.add_handler(start_menu_handler)
    application.add_handler(broadcast_menu_handler)
    application.add_handler(admin_menu_handler)
    application.add_handler(content_menu_handler)
    application.add_handler(statistics_menu_handler)
    application.add_handler(settings_menu_handler)
    application.add_handler(join_request_handler)
    application.add_error_handler(callback=ChatEventsRepository.send_sorry)
