import logging
import os
from telegram.ext import Application, CommandHandler, filters, MessageHandler
from .handlers.command import start, help, list, track, untrack
from .handlers.error import nonExistent


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
            .token(str(os.environ.get("TELEGRAM_BOT_TOKEN")))
            .build()
        )
        self.init_handlers()
        self.app.run_polling()
        # type: ignore

    def init_handlers(self) -> None:
        self.app.add_handler(CommandHandler("start", start))
        self.app.add_handler(CommandHandler("help", help))
        self.app.add_handler(CommandHandler("list", list))
        self.app.add_handler(CommandHandler("track", track))
        self.app.add_handler(CommandHandler("untrack", untrack))
        self.app.add_handler(MessageHandler(filters.COMMAND, nonExistent))
