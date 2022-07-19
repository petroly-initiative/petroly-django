from django.core.management.base import BaseCommand;
from ...bot.botController import BotController;

class Command(BaseCommand):
    help = "Runs the telegram bot process"

    def handle(self, *args, **options):
        self.stdout.write("Telegram Bot running...")
        controller = BotController();
        self.stdout.write("Bot Process terminated");
        
