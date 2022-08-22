"""
Here are some implement some useful logging configuration.
"""

import logging

import requests
from django.conf import settings

CUSTOM_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
        "verbose": {
            "format": "{levelname} {module} {process:d} - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "send_discord": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "petroly.log.DiscordNotificationHandler",
        },
    },
    "loggers": {
        "notifier": {
            "handlers": ["console", "send_discord"],
            "level": "INFO",
            "propagate": False,
        },
        "telegram_bot": {
            "handlers": ["console", "send_discord"],
            "level": "INFO",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
        },
    },
}


MESSAGE = """
An Exception occurred

Level: `{}`
Module: `{}`
Line: `{}`
Message
```{}```
"""


class DiscordNotificationHandler(logging.Handler):
    """
    This a logging handler to send a Discord notification.
    """

    def __init__(self):
        super().__init__()

    def emit(self, record: logging.LogRecord):
        content = MESSAGE.format(
            record.levelname, record.module, record.lineno, record.message
        )

        requests.post(settings.DISCORD_WEBHOOK_URL, json={"content": content})
