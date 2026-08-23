from __future__ import annotations

import logging

from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from . import constants
from .config import Settings, load_settings
from .handlers import menu, payments
from .handlers.anticheat import handle_channel_member_update
from .handlers.start import start_command
from .storage import Store

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("yeon")


async def _on_error(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Unhandled exception while processing update:", exc_info=context.error)
    if hasattr(update, "effective_message") and update.effective_message:
        try:
            await update.effective_message.reply_text(
                f'{constants.pe("card")} Something went wrong — please try again.',
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass


async def _post_init(application: Application) -> None:
    settings: Settings = application.bot_data["settings"]
    try:
        await application.bot.send_message(
            chat_id=settings.logger_group_id,
            text=f'{constants.pe("sparkle")} <b>{constants.BOT_NAME} is online</b>',
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        log.exception("Could not announce startup in logger group.")
    log.info("%s is online.", constants.BOT_NAME)


def build_application() -> Application:
    settings = load_settings()
    store = Store(settings.mongo_uri, settings.mongo_db_name)

    application = ApplicationBuilder().token(settings.bot_token).post_init(_post_init).build()
    application.bot_data["settings"] = settings
    application.bot_data["store"] = store

    application.add_handler(CommandHandler("start", start_command))

    connect_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu.connect_start, pattern="^menu_connect$")],
        states={
            menu.AWAITING_CHANNEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, menu.connect_receive)
            ],
        },
        fallbacks=[CallbackQueryHandler(menu.cancel_flow, pattern="^menu_cancel$")],
    )

    create_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu.create_start, pattern="^menu_create$")],
        states={
            menu.AWAITING_PRIZE: [MessageHandler(filters.ALL & ~filters.COMMAND, menu.create_receive)],
        },
        fallbacks=[CallbackQueryHandler(menu.cancel_flow, pattern="^menu_cancel$")],
    )

    vote_adjust_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(menu.addvotes_start, pattern="^menu_addvotes$"),
            CallbackQueryHandler(menu.removevotes_start, pattern="^menu_removevotes$"),
        ],
        states={
            menu.AWAITING_VOTE_ADJUST: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, menu.vote_adjust_receive)
            ],
        },
        fallbacks=[CallbackQueryHandler(menu.cancel_flow, pattern="^menu_cancel$")],
    )

    application.add_handler(connect_conv)
    application.add_handler(create_conv)
    application.add_handler(vote_adjust_conv)

    buy_cash_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(payments.buyvotes_cash_start, pattern="^buyvotes_cash$")],
        states={
            payments.ASK_QTY_CASH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, payments.receive_qty_cash)
            ],
            payments.ASK_SCREENSHOT: [MessageHandler(filters.PHOTO, payments.receive_screenshot)],
        },
        fallbacks=[CallbackQueryHandler(menu.cancel_flow, pattern="^menu_cancel$")],
    )

    buy_stars_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(payments.buyvotes_stars_start, pattern="^buyvotes_stars$")],
        states={
            payments.ASK_QTY_STARS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, payments.receive_qty_stars)
            ],
        },
        fallbacks=[CallbackQueryHandler(menu.cancel_flow, pattern="^menu_cancel$")],
    )

    application.add_handler(buy_cash_conv)
    application.add_handler(buy_stars_conv)

    application.add_handler(CallbackQueryHandler(menu.go_home, pattern="^menu_home$"))
    application.add_handler(CallbackQueryHandler(menu.show_manage, pattern="^menu_manage$"))
    application.add_handler(CallbackQueryHandler(menu.show_leaderboard, pattern="^menu_leaderboard$"))
    application.add_handler(CallbackQueryHandler(menu.end_confirm, pattern="^menu_end_confirm$"))
    application.add_handler(CallbackQueryHandler(menu.end_yes, pattern="^menu_end_yes$"))
    application.add_handler(CallbackQueryHandler(menu.vote_callback, pattern="^vote_"))
    application.add_handler(CallbackQueryHandler(payments.purchase_accept, pattern="^purchase_accept_"))
    application.add_handler(CallbackQueryHandler(payments.purchase_reject, pattern="^purchase_reject_"))

    # Anti-cheat: revoke votes when a voter leaves the connected channel
    application.add_handler(ChatMemberHandler(handle_channel_member_update, ChatMemberHandler.CHAT_MEMBER))

    # Telegram Stars payments
    application.add_handler(PreCheckoutQueryHandler(payments.precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, payments.successful_payment_callback))

    # NOTE: the old "share your link to confirm a cash purchase" fallback
    # handler has been removed. purchase_accept() now credits votes
    # immediately using the stored participant_id — no link confirmation
    # step is needed anymore, and payments.link_confirmation_handler no
    # longer exists, so registering it here would crash on startup.

    application.add_error_handler(_on_error)

    return application


def main() -> None:
    application = build_application()
    application.run_polling(
        allowed_updates=["message", "callback_query", "chat_member", "pre_checkout_query"]
    )


if __name__ == "__main__":
    main()