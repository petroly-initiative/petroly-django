from django.core.management.base import BaseCommand
from telegram_bot.utils.bot_controller import BotController


class Command(BaseCommand):
    """a command that fires the bot polling"""

    help = "Runs the telegram bot process"

    def handle(self, *args, **options):
        self.stdout.write("Telegram Bot running...")
        BotController()
        self.stdout.write("Bot Process terminated")
