# Generated by Django 4.0.6 on 2022-07-22 07:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import telegram_bot.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('revoked', models.BooleanField(default=False, verbose_name='revoked')),
                ('token', models.CharField(default=telegram_bot.models.generate_token_str, help_text='random generated', max_length=5, verbose_name='token')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'token',
                'verbose_name_plural': 'tokens',
                'ordering': ['-created_on', 'user'],
            },
        ),
        migrations.CreateModel(
            name='TelegramProfile',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='telegram user ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('chat_id', models.IntegerField(unique=True, verbose_name='chat ID')),
                ('username', models.CharField(max_length=256, unique=True, verbose_name='telegram username')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
    ]
