from django import forms
from django_q.tasks import async_task

from telegram_bot.models import TelegramProfile


class TelegramMessageForm(forms.Form):
    """A simple form to write and send mass
    Telegram messages"""

    message = forms.CharField(widget=forms.Textarea)
    usernames = forms.CharField(widget=forms.Textarea)

    def send_message(self):
        usernames = self.cleaned_data["usernames"]

        if usernames:
            usernames = usernames.split(",")
            profiles = TelegramProfile.objects.filter(user__username__in=usernames)
        else:
            profiles = TelegramProfile.objects.all()

        chat_ids = [obj.id for obj in profiles]
        print(chat_ids)

        async_task(
            "telegram_bot.utils.mass_send_telegram_message",
            chat_ids,
            self.cleaned_data["message"],
            task_name="sending-mass-telegram",
            group="telegram_message",
            timeout=60 * 60,  # 1 hour
        )
