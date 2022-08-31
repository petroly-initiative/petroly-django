
from django.shortcuts import render
from django.views.generic import FormView

from .forms import TelegramMessageForm


class SendMassTelegramView(FormView):
    """a view to send a mass message to all
    saved telegram accounts"""

    template_name = "telegram_bot/telegram_form.html"
    form_class = TelegramMessageForm

    def form_valid(self, form: TelegramMessageForm):
        form.send_message(self.request.POST["message"])

        return render(self.request, "telegram_bot/telegram_sent.html")
