

from django.urls import path
from . import views

app_name = "telegram_bot"

urlpatterns = [
    path('send_mass_telegram/', views.SendMassTelegramView.as_view(), name='send_mass_telegram'),
]
