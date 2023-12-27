from telegram.ext import (CommandHandler, Application, ConversationHandler,
                          CallbackQueryHandler, MessageHandler, filters)
from repository.start_menu import StartMenu
from repository.admin_menu import AdminMenu
from repository.partner_menu import PartnerMenu


start_menu_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", StartMenu.get_menu),
        CallbackQueryHandler(callback=StartMenu.get_menu, pattern="start_menu"),
    ],
    states={
    },
    allow_reentry=True,
    fallbacks=[],
)

admin_menu_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=AdminMenu.products, pattern="admin_products"),
        CallbackQueryHandler(callback=AdminMenu.list_products, pattern="admin_list_products"),
        CallbackQueryHandler(callback=AdminMenu.add_product, pattern="admin_add_product"),
        CallbackQueryHandler(callback=AdminMenu.current_product, pattern="admin_product"),
        CallbackQueryHandler(callback=AdminMenu.product_ad, pattern="admin_add_ad")
    ],
    states={
        "product_add_price": [MessageHandler(callback=AdminMenu.add_price, filters=filters.TEXT)],
        "product_add_url": [MessageHandler(callback=AdminMenu.add_url, filters=filters.TEXT)],
        "product_add_post": [MessageHandler(callback=AdminMenu.add_post, filters=filters.TEXT)],
        "product_save": [MessageHandler(callback=AdminMenu.product_save, filters=filters.TEXT)],
        "save_ad_post": [MessageHandler(callback=AdminMenu.save_ad_post, filters=filters.TEXT)]
    },
    allow_reentry=True,
    fallbacks=[],
)
partner_menu_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=PartnerMenu.list_products, pattern="partner_products"),
        CallbackQueryHandler(callback=PartnerMenu.current_product, pattern="partner_select_product"),
        CallbackQueryHandler(callback=PartnerMenu.show_product_ad_post, pattern="partner_product_ad"),
        CallbackQueryHandler(callback=PartnerMenu.current_post, pattern="partner_select_post"),
        CallbackQueryHandler(callback=PartnerMenu.get_unique_link, pattern="partner_unique_link"),
        CallbackQueryHandler(callback=PartnerMenu.orders_button, pattern="partner_orders")
    ],
    states={
    },
    allow_reentry=True,
    fallbacks=[],
)


def add_handlers(application: Application):
    application.add_handler(start_menu_handler)
    application.add_handler(admin_menu_handler)
    application.add_handler(partner_menu_handler)
