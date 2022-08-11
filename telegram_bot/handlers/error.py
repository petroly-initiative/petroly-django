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

async def call_back_error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Informs the user that the button is no longer available."""
    await update.callback_query.answer()
    await update.effective_message.edit_text(
        "Sorry, this message no longer accepts replies.\n Please run the command again"
    )