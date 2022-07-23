# Generated by Django 4.0.6 on 2022-07-22 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegramprofile',
            name='chat_id',
        ),
        migrations.AlterField(
            model_name='telegramprofile',
            name='username',
            field=models.CharField(blank=True, max_length=256, unique=True, verbose_name='telegram username'),
        ),
    ]