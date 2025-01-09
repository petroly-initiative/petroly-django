"""
This module is to define the fetching, filtering, and processing the data
from the KFUPM API
"""

import html
import json
import logging
import os
import sys
from typing import Dict, List, Tuple
from collections import defaultdict

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q
from django.template import loader
from django.utils.timezone import now
from django_q.tasks import async_task
import requests as rq
from telegram.constants import ParseMode

from data import DepartmentEnum, SubjectEnum
from evaluation.models import Instructor
from evaluation.schema import crete_global_id
from evaluation.types import InstructorNode
from notifier.models import Cache
from telegram_bot import messages
from telegram_bot import utils as bot_utils
from telegram_bot.models import TelegramProfile

from .models import (
    Banner,
    BannerEvent,
    Cache,
    ChannelEnum,
    Course,
    Status,
    StatusEnum,
    TrackingList,
)

User = get_user_model()
logger = logging.getLogger(__name__)
assert (ENC_KEY := os.environ.get("ENC_KEY")), "You must provide `ENC_KEY` env var."

# with open("notifier/banner_api.py", "r") as file:
#     file_bin = file.read().encode()
#     f = Fernet(ENC_KEY.encode())
#     enc_file = f.encrypt(file_bin)
#
# with open("notifier/banner_api.py.bin", "wb") as file:
#     file.write(enc_file)

# decrypt the python code into a module
with open("notifier/banner_api.py.bin", "rb") as file:
    f = Fernet(ENC_KEY.encode())
    code = f.decrypt(file.read()).decode()
    import types

    banner_api = types.ModuleType("banner_api")
    exec(code, banner_api.__dict__)


def register_for_user(user_pk, term: str, crns: List):
    try:
        banner = Banner.objects.get(user__pk=user_pk)
    except ObjectDoesNotExist:
        bot_utils.send_telegram_message(
            TelegramProfile.objects.get(user__pk=user_pk).id,
            r"We tried to register your courses but you did not clone your Banner session",
        )
        return False

    if not banner.cookies:
        bot_utils.send_telegram_message(
            banner.user.telegram_profile.id,
            r"We tried to register your courses but your Banner session has expired",
        )
        return

    res = banner_api.register(banner, term, crns)

    if isinstance(res, list):
        message = ""
        for model in res:
            if model["submitResultIndicator"]:
                message += f"{model['subject']}{model['courseNumber']} - {model['courseReferenceNumber']}:"

                for msg in model["messages"]:
                    message += f"\n{msg['message']}"
                message += "\n\n"
    elif isinstance(res, str):
        message = res
    else:
        message = str(res)

    if message is not None:
        bot_utils.send_telegram_message(
            banner.user.telegram_profile.id,
            "We tried to register your courses here is the result\n\n"
            f"<pre>{html.escape(message)}</pre>",
            ParseMode.HTML,
        )
    else:
        bot_utils.send_telegram_message(
            banner.user.telegram_profile.id, r"We could not register your courses\."
        )

    BannerEvent.objects.create(
        banner=banner, crns=crns, term=term, result=f"{res}\n\n\n{message}"
    )


def check_session(user_pk):
    """This uses user's Banner session to
    check for its health."""
    banner = Banner.objects.get(user__pk=user_pk)

    if banner.cookies:
        if banner_api.check_banner(banner):
            banner.active = True
            banner.save()

            return True

        banner.active = False
        banner.save()
        banner.scheduler.delete()

        bot_utils.send_telegram_message(
            banner.user.telegram_profile.id,
            "We lost your cookies, re-clone your Banner session",
            ParseMode.HTML,
        )


def fetch_data(term: str, department: str) -> List[Dict]:
    """This load data from our DB."""

    try:
        obj = Cache.objects.get(term=term, department=department)

    except Cache.DoesNotExist:
        request_data(term, department)
        obj = Cache.objects.get(term=term, department=department)

    return obj.get_data()  # type: ignore


def request_data(term, department) -> None:
    """This method performs a GET request to the KFUPM API
    for the specific args.

    Args:
        term (str): e.g., 202210
        department (str): e.g., 'ICS'

    Returns:
        dict: the response JSON after converting into dict object,
    """
    api_obj, _ = Status.objects.get_or_create(key="API")
    obj, _ = Cache.objects.get_or_create(term=term, department=department)
    if api_obj.status == StatusEnum.DOWN:
        obj.stale = False
        obj.save()
        return

    try:
        data = banner_api.fetch(term, department)

    except rq.Timeout:
        logger.warning(
            "Timeout on %s-%s",
            term,
            department,
        )
        obj.stale = False
        obj.save()
        return

    except rq.exceptions.ProxyError as exc:
        logger.warn("ProxyError: %s", exc)
        obj.stale = False
        obj.save()

        api_obj.status = StatusEnum.DOWN
        api_obj.save()
        return

    except rq.RequestException as exc:
        logger.error(
            "Failed fetching %s-%s from API - Exception: %s",
            term,
            department,
            exc,
        )
        obj.stale = False
        obj.save()
        return

    except json.decoder.JSONDecodeError:
        logger.warning("JSON Decoding failed")

        obj.stale = False
        obj.save()
        return

    except banner_api.APIDownException:
        obj.stale = False
        obj.save()

        api_obj.status = StatusEnum.DOWN
        api_obj.save()
        return

    except Exception as exc:
        logger.error(
            "Failed fetching %s-%s from API - Exception: %s",
            term,
            department,
            exc,
        )
        obj.stale = False
        obj.save()
        return

    if data:
        obj.data = data
        obj.stale = False
        obj.updated_on = now()
        obj.save()

    else:
        logger.info("No data returned")


def get_course_info(course: Course) -> dict:
    """To search for a course by CRN in
    the returned data from `fetch_data`.

    Args:
        course (Course): obj of `Course` model

    Returns:
        dict: that course's info
    """

    data = fetch_data(course.term, course.department)
    for api_course in data:
        if api_course["courseReferenceNumber"] == course.crn:
            return api_course

    return {}


def check_changes(course: Course) -> Tuple:
    """for given `Course` obj check if there is
    an increase in one of the fields
    - `waiting_list_count`
    - `available_seats`
    compared against the last saved status.

    Args:
        course (Course): obj of `Course` model

    Returns:
        Tuple: first element is true if there is a change,
        the second element is a dict of the fields latest info.
    """

    course_info = get_course_info(course)
    if not course_info:
        course_crn = course.crn
        course.delete()
        raise ValueError(
            f"Course: {course_crn} not found, it might have been removed from source, "
            "It's deleted."
        )

    # renaming keys for back compatibility
    info = {
        "available_seats": course_info["seatsAvailable"],
        "waiting_list_count": course_info["waitAvailable"],
    }
    increased = (
        info["available_seats"] > 0 and info["available_seats"] > course.available_seats
    ) or (
        info["waiting_list_count"] > 0
        and info["waiting_list_count"] > course.waiting_list_count
    )

    # add the old numbers to returned info
    info["available_seats_old"] = course.available_seats
    info["waiting_list_count_old"] = course.waiting_list_count

    # update the course obj with new numbers
    course.available_seats = info["available_seats"]
    course.waiting_list_count = info["waiting_list_count"]

    # this is important even if there is no change,
    # to auto update the `last_updated` field to now.
    course.save()

    return (increased, info)


def collect_tracked_courses() -> Dict[str, List[Course | set[User]]]:
    """
    Collect all tracked courses and group with each course
    its `User` objects (aka, trackers).

    Returns:
        set: A set of all `Course` objects
    """
    courses_dict = {}

    for tracking_list in TrackingList.objects.all():
        user = tracking_list.user
        for course in tracking_list.courses.all():
            try:
                courses_dict[course.crn]["trackers"].add(user)
            except KeyError:
                courses_dict[course.crn] = {
                    "course": course,
                    "trackers": {user},
                }

    return courses_dict


def send_notification(user_pk: int, info: str) -> None:
    """Send a notification for every channel in `TrackingList.channels`"""

    tracking_list = TrackingList.objects.get(user__pk=user_pk)
    user = tracking_list.user
    channels = tracking_list.channels
    # deserialize the dict back
    info_dict: List[Dict] = eval(info)

    # inject `Course` objects and `course_api` into `info_dict`
    for c_info in info_dict:
        c_info["course"] = Course.objects.get(pk=c_info["course_pk"])

    if ChannelEnum.TELEGRAM in channels:
        try:
            success = bot_utils.send_telegram_changes(
                chat_id=user.telegram_profile.id,
                msg=formatter_change_md(info_dict),
            )
            if not success:
                logger.info("Deleting TrackingList for user: %s - %s", user, success)
                user.tracking_list.delete()

        except Exception as exc:
            logger.error("Couldn't send to Telegram: %s - %s", user, exc)
            # fall to sending and email
            channels.append(ChannelEnum.EMAIL)

    if ChannelEnum.EMAIL in channels:
        try:
            res = send_mail(
                subject="Petroly Radar Detected Changes -  We couldn't send it by Telegram"
                "Please check your Petroly settings",
                message=info,
                html_message=loader.render_to_string(
                    "notifier/email_changes.html",
                    context={
                        "info": info_dict,
                        "domain": "https://api.petroly.co",
                    },
                ),
                recipient_list=[user.email],
                fail_silently=False,
                from_email=None,
            )
            logger.info("Changes email was sent: %s", res)
        except Exception as exc:
            logger.error("Couldn't send email: %s", exc)

    # After sending notifications, let's try to register (if enabled)
    # user mignt not have a Banner obj yet
    try:
        if not user.banner.active:
            return
    except ObjectDoesNotExist:
        return

    courses: List[Course] = []
    register_courses = tracking_list.register_courses.all()
    for c_info in info_dict:
        if (
            c_info["course"] in register_courses
            and c_info["course"] in tracking_list.courses.all()
        ):
            # search if another section's been added already
            for course in courses:
                if course.raw["subjectCourse"] == c_info["course"].raw["subjectCourse"]:
                    break
            courses.append(c_info["course"])

    grouped_by_term = defaultdict(list)
    for c in courses:
        grouped_by_term[c.term].append(c.crn)

    if Status.is_up("register"):
        for term, crns in grouped_by_term.items():
            async_task(
                "notifier.utils.register_for_user",
                user_pk,
                term,
                ",".join(crns),
                task_name=f"register-{user_pk}",
                group="register_crns",
            )


def formatter_md(courses: List[Course]) -> str:
    """helper method to create a formatted message for each course in the tracking list"""
    # for each course we will create a message format

    result = ""
    for course in courses:
        result += messages.TRACKED_COURSES.format(
            crn=course.crn,
            course_number=course.raw["subjectCourse"],
            section_number=course.raw["sequenceNumber"],
            available_seats=course.available_seats,
            waiting_list_count="🟢 Open"
            if course.waiting_list_count > 0
            else "🔴 Closed",
        )

    return result.replace("-", "\\-")


def formatter_change_md(info: List[Dict[str, Course | Dict]]) -> str:
    """helper method to create a formatted message for each course in the tracking list"""
    # for each course we will create a message format

    result = "Changes detected 🥳\nClick on the CRN number to copy it\n\n"
    for course in info:
        result += messages.CHANGES_DETECTED.format(
            crn=course["course"].crn,
            course_number=course["course"].raw["subjectCourse"],
            section_number=course["course"].raw["sequenceNumber"],
            available_seats=course["status"]["available_seats"],
            available_seats_old=course["status"]["available_seats_old"],
            waiting_list_count=course["status"]["waiting_list_count"],
            waiting_list_count_old=course["status"]["waiting_list_count_old"],
        )

    return result.replace("-", "\\-")


def instructor_info_from_name(name: str, department: str) -> Dict:
    """Find a matching instructor
    in our `Instructor` model.

    Args:
        name (str): the name as from API
        department (str): department short form

    Returns:
        Dict: Some info
    """

    names = name.split(" ")
    match department:
        case SubjectEnum.ACCT | SubjectEnum.MKT | SubjectEnum.BUS | SubjectEnum.ECON:
            department = DepartmentEnum.ACFN

        case SubjectEnum.MIS | SubjectEnum.OM:
            department = DepartmentEnum.ISOM

        case SubjectEnum.ENGL | SubjectEnum.CGS:
            department = DepartmentEnum.ELD

        case SubjectEnum.SWE:
            department = DepartmentEnum.ICS

        case SubjectEnum.STAT:
            department = DepartmentEnum.MATH

        case SubjectEnum.ISE:
            department = DepartmentEnum.SE

        case SubjectEnum.ISE:
            department = DepartmentEnum.SE

        case SubjectEnum.GEOL:
            department = DepartmentEnum.ERTH

        case SubjectEnum.GEOP:
            department = DepartmentEnum.CPG

    filters = Q(department=department)

    for name_ in names:
        if "dr" not in name_.lower() and "mr" not in name_.lower():
            # ignore `dr` and `mr` from using in filtering
            filters &= Q(name__icontains=name_)

    queryset = Instructor.objects.filter(filters)
    if len(queryset) == 1:
        return {
            "pk": crete_global_id(InstructorNode, queryset[0].pk),
            "profilePic": queryset[0].profile_pic.url,
            "rating": queryset[0].avg()["overall_float"],
        }

    return {}


def not_stale_all_cache():
    """While DEBUG is False, make all cache stale False,
    to re-queue new fetching request, once the server is started."""

    if not settings.DEBUG:
        Cache.objects.filter(stale=True).update(stale=False)


# tbh, it's a dirty solution
if "petroly.wsgi" in sys.argv:
    # run task only when the server is started
    async_task("notifier.utils.not_stale_all_cache", task_name="set_stale_False")


# def clean_old_tasks():
#     old_date = datetime.now() - timedelta(minutes=2)
#     old_tasks = OrmQ.objects.filter(lock__date__lt=old_date)
#     print(old_tasks)
#     return
#     for task in old_tasks:
#         name: str = task.name()
#         if name.startswith("request-data"):
#             term, subject = name.replace("request-data-", "").split("-")

#             Cache.objects.filter(term=term, department=subject).update(stale=False)


# try:
#     schedule(
#         "notifier.utils.clean_old_task",
#         name="clean_old_tasks",
#         schedule_type=Schedule.MINUTES,
#         minutes=1,
#         repeats=-1,
#     )
# except IntegrityError as e:
#     logger.warn("While adding `clean_old_task`: %s", e)
#     pass
# except Exception as e:
#     logger.error("Failed to as clean old tasks: %s", e)
#     raise
