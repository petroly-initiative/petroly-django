"""
Main class definition for the Telegram Bot interface.
"""

from ast import pattern
import os
import logging


from telegram.ext import (
    Application,
    CommandHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
    InvalidCallbackData,
    MessageHandler,
)

from .handlers.command import start, help_msg, tracked_courses
from .handlers.conversation import (
    CommandEnum,
    cancel,
    track,
    track_confirm,
    track_courses,
    track_dept,
    track_sections,
    untrack
)
from .handlers.error import call_back_error, non_existent


# setting up the logger for the bot status
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
# spawning the bot process


class BotController:
    def __init__(self) -> None:

        self.app: Application = (
            Application.builder()
            .token(os.environ.get("TELEGRAM_BOT_TOKEN"))
            .arbitrary_callback_data(True)  # type: ignore
            .build()
        )
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.init_comm_handlers()
        self.init_conv_handlers()
        self.app.add_handler(MessageHandler(filters.COMMAND, non_existent))
        self.app.run_polling()
        print(self.app.handlers)

        logger.info("Telegram Bot started")

    def init_comm_handlers(self) -> None:
        self.app.add_handler(CommandHandler("start", start))
        self.app.add_handler(CommandHandler("help", help_msg))
        self.app.add_handler(CommandHandler("tracked", tracked_courses))
        self.app.add_handler(
            CallbackQueryHandler(call_back_error, pattern=InvalidCallbackData)
        )
        # self.app.add_handler(CommandHandler("track", track))
        # self.app.add_handler(CommandHandler("untrack", untrack))

        logger.info("Handlers initialized")

    def init_conv_handlers(self) -> None:
        """to handle all assigned conversation handlers"""
        track_handler = ConversationHandler(
            entry_points=[CommandHandler("track", track)],  # type: ignore
            states= {
                CommandEnum.DEPT: [CallbackQueryHandler(track_dept)],
                CommandEnum.COURSE: [CallbackQueryHandler(track_courses)],
                CommandEnum.SECTION: [CallbackQueryHandler(track_sections)],
                CommandEnum.CRN: [MessageHandler(filters.TEXT, track_crn )],
                CommandEnum.CONFIRM: [CallbackQueryHandler(track_confirm)],
                CommandEnum.CLOSE: [CallbackQueryHandler(track_close)]

            },  # type: ignore
            fallbacks=[CommandHandler("cancel", cancel)],  # type: ignore
        )
        self.app.add_handler(track_handler)
