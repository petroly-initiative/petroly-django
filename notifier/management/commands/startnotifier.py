"""
A django custom command to start the Notifier checking.
"""

from django.core.management.base import BaseCommand

from notifier.utils import check_all_and_notify


class Command(BaseCommand):
    """a command that get in infinite loop of checking"""

    help = "Start checking and notifying the courses"

    def handle(self, *args, **options):
        self.stdout.write(">>>> Notifier running")
        check_all_and_notify()
        self.stdout.write(">>>> Notifier stopped")
