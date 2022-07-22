"""
Main class definition for the Telegram Bot interface.
"""

import os
import logging

from telegram.ext import Application, CommandHandler, filters, MessageHandler

from .handlers.command import start, help_msg, tracked_courses, verify
from .handlers.conversation import track, untrack
from .handlers.error import non_existent


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
            .build()
        )
        self.init_handlers()
        self.app.run_polling()
        self.app.bot.send_message()
        # type: ignore

    def init_handlers(self) -> None:
        self.app.add_handler(CommandHandler("start", start))
        self.app.add_handler(CommandHandler("help", help_msg))
        self.app.add_handler(CommandHandler("list", tracked_courses))
        self.app.add_handler(CommandHandler("track", track))
        self.app.add_handler(CommandHandler("untrack", untrack))
        self.app.add_handler(CommandHandler("verify", verify))
        self.app.add_handler(MessageHandler(filters.COMMAND, non_existent))
