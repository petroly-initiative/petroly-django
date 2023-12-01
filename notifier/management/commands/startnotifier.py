"""
A django custom command to start the Notifier checking.
"""

from datetime import timedelta
import logging
import signal
import time
import warnings

from django.core.cache import CacheKeyWarning
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django_q.tasks import async_task, schedule
import requests as rq

from account.models import Profile
from notifier import utils
from notifier.models import Status, StatusEnum
from notifier.utils import check_changes, collect_tracked_courses

warnings.simplefilter("ignore", CacheKeyWarning)
warnings.simplefilter("ignore", DeprecationWarning)

# setting up the logger
logger = logging.getLogger(__name__)


class GracefulKiller:
    """To catch SIGINT $ SIGTERM signals
    then exit gracefully."""

    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True


class Command(BaseCommand):
    """a command that get in infinite loop of checking"""

    help = "Start checking and notifying the courses"

    def handle(self, *args, **options):
        """Check all tracked courses
        and grouped the notification by user
        then send a notification details

        This method is infinite loop,
        it should be called from a async context.

        return: the structure is
        {
            'user1_pk': [
                    {
                        'course1': <Course1>,
                        'status': {
                            'available_seats': 0
                            'waiting_list_count': 0
                            'available_seats_old': 0
                            'waiting_list_count_old': 0
                        }
                    },
                ], ...
            'user2_pk': ...,
        }
        """

        logger.info("Starting the Notifier Checking")
        killer = GracefulKiller()

        while not killer.kill_now:
            api_status, status_created = Status.objects.get_or_create(key="API")
            if status_created:
                api_status.status = StatusEnum.UP
                api_status.save()

            if api_status.status == StatusEnum.DOWN:
                logger.warning("API is still Down")
                time.sleep(30)

                try:
                    if utils.banner_api.test_connection():
                        logger.info("API is Up again")
                        api_status.status = StatusEnum.UP
                        api_status.save()

                except rq.exceptions.ProxyError:
                    logger.warn("Proxy issue not resolved.")

                except Exception as exc:
                    logger.error(exc)

                finally:
                    continue

            try:
                t_start = time.perf_counter()

                collection = collect_tracked_courses()
                changed_courses = []

                logger.info(
                    "Retrieved tracked courses within %0.4f",
                    time.perf_counter() - t_start,
                )

                t_start = time.perf_counter()
                for _, value in collection.items():
                    changed, status = check_changes(value["course"])

                    if changed:
                        value["status"] = status
                        changed_courses.append(value)

                logger.info(
                    "Courses changes checked within %0.4f",
                    time.perf_counter() - t_start,
                )

                t_start = time.perf_counter()
                # group `changed_courses` by unique trackers
                courses_by_tracker = {}
                for c in changed_courses:
                    for tracker in c["trackers"]:
                        try:
                            courses_by_tracker[tracker.pk].append(
                                {
                                    "course_pk": c["course"].pk,
                                    "status": c["status"],
                                }
                            )
                        except KeyError:
                            courses_by_tracker[tracker.pk] = [
                                {
                                    "course_pk": c["course"].pk,
                                    "status": c["status"],
                                }
                            ]

                logger.info(
                    "grouped changes within %0.9f",
                    time.perf_counter() - t_start,
                )

                t_start = time.perf_counter()
                for tracker_pk, info in courses_by_tracker.items():
                    if Profile.objects.get(user__pk=tracker_pk).premium:
                        async_task(
                            "notifier.utils.send_notification",
                            tracker_pk,
                            str(info),
                            task_name=f"sending-notification-{tracker_pk}",
                            group="change_notification",
                        )
                    else:
                        schedule(
                            "notifier.utils.send_notification",
                            tracker_pk,
                            str(info),
                            next_run=now() + timedelta(minutes=1),
                        )

                logger.info(
                    "Created `sending-notification-` within %0.9f",
                    time.perf_counter() - t_start,
                )

            except Exception as exc:
                logger.warning(exc)

            time.sleep(10)

        logger.info("Stopping the Notifier Checking.")
