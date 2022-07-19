from telegram.ext import ( Application, CommandHandler
)


from notifier.bot.botController import BotController

from django.apps import AppConfig



class NotifierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifier'

        
  
        
