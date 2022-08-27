"""
    To populate telegram links into out `community` service.
    How to use:
    run in the terminal:
        `python populate_communities.py {dev|prod}`
"""

import os
import sys
import time


settings_type = sys.argv[1]
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "petroly.settings." + settings_type
)
# the above line is sufficient
# settings.configure()

print("DJANGO_SETTINGS_MODULE: ", os.environ.get("DJANGO_SETTINGS_MODULE"))


def send_email():
    msg = """We received huge demand on our services, and sending huge number of 
    emails are not possible.
    if still want us to notify you please activate your Telegram from our website.
    Open your tacking list from the lower right icon, then open settings
    """

    for obj in TrackingList.objects.filter(channels=[ChannelEnum.EMAIL]):
        user: User = obj.user

        print(f"sending to {user}")
        try:
            user.email_user("Turning off Email Channel", msg)

        except Exception as exc:
            print(exc)

        time.sleep(3)


if __name__ == "__main__":
    import django

    django.setup()

    from notifier.models import TrackingList, ChannelEnum
    from django.contrib.auth.models import User

    send_email()
