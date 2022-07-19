from telegram.ext import ( ContextTypes)
from telegram import Update



async def nonExistent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(text = "This command does not exist, please refer to the menu for available commands that you can use for the notifier bot");