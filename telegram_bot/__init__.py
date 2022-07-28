from telegram.ext import Application
from django.conf import settings

# Telegram app, this shouldn't result conflict
# This can be imputed from anywhere within Django
# To send quick message to a user
telegram_app = Application.builder().token(settings.TELEGRAM_TOKEN).build()
