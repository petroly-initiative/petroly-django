"""
Bot handlers of unrecognized command is asked.
"""

from telegram.ext import ContextTypes
from telegram import Update


async def non_existent(
    update: Update, _: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.message.reply_text(
        text="Oops! This command does not exist, check the menu for available commands"
    )
