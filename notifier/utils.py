"""
This module is to define the fetching, filtering, and processing the data
from the KFUPM API
"""


import json
from typing import List, Dict, Tuple
from pprint import pprint
from time import sleep
from asgiref.sync import async_to_sync

import requests as rq
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django_q.tasks import async_task
from telegram.ext import Application
from telegram.constants import ParseMode

from .models import TrackingList, Course, ChannelEnum

User = get_user_model()
API = "https://registrar.kfupm.edu.sa/api/course-offering"


def fetch_data(term: str, department: str) -> List[Dict]:
    """This method performs a GET request to the KFUPM API
    for the specific args.

    Args:
        term (str): e.g., 202210
        department (str): e.g., 'ICS'

    Returns:
        dict: the response JSON after converting into dict object,
    """

    data = cache.get((term, department))

    if data:
        return data
    print("cache miss")
    res = rq.get(
        API, params={"term_code": term, "department_code": department}
    )

    assert res.ok
    data = json.loads(res.content)["data"]

    cache.set((term, department), data)  # store data into cache

    return data


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
        if api_course["crn"] == course.crn:
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
    keys = ["available_seats", "waiting_list_count"]
    info = {key: course_info[key] for key in keys}
    increased = (
        info["available_seats"] > course.available_seats
        or info["waiting_list_count"] > course.waiting_list_count
    )
    decreased = (
        info["available_seats"] < course.available_seats
        or info["waiting_list_count"] < course.waiting_list_count
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


# Telegram app, this shouldn't result conflict
app = Application.builder().token(settings.TELEGRAM_TOKEN).build()


@async_to_sync
async def send_telegram(chat_id: int, msg: str):
    """To make this method as sync"""

    val = await app.bot.send_message(
        chat_id=chat_id,
        text=msg,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def send_notification(user_pk: int, msg: str) -> None:
    """Send a notification for every channel in `TrackingList.channels`"""

    user: User = User.objects.get(pk=user_pk)
    channels = user.tracking_list.channels

    if ChannelEnum.EMAIL in channels:
        send_mail(
            subject="Changes detected",
            message=msg,
            recipient_list=[user.email],
            fail_silently=False,
            from_email=None,
        )

    if ChannelEnum.TELEGRAM in channels:
        send_telegram(chat_id=user.telegram_profile.id, msg=msg)


def formatter_md(courses: List[Course]) -> str:
    """helper method to create a formatted message for each course in the tracking list"""
    # for each course we will create a message format

    result = ""
    for course in courses:
        course = get_course_info(course)

        result += f"""**{course["course_number"]}\\-{course["section_number"]}**  \\- *{course["crn"]}*
        Available Seats: {course["available_seats"]}
        Waiting list: {conditional_coloring(course["waiting_list_count"])}\n\n"""
    return result


def formatter_change_md(info: List[Dict[str, Course | User | Dict]]) -> str:
    """helper method to create a formatted message for each course in the tracking list"""
    # for each course we will create a message format

    result = ""
    for course in info:
        status = course["status"]
        course = get_course_info(course["course"])

        result += f"""**{course["course_number"]}\\-{course["section_number"]}**  \\- *{course["crn"]}*
        Available Seats: {status["available_seats_old"]} ➡️  {status["available_seats"]}
        Waiting list: {conditional_coloring(status["waiting_list_count"])}\n\n"""
    return result


def conditional_coloring(wait_list_count) -> str:
    """helper method to append the correct coloring according to
    the waiting list count"""

    if wait_list_count == 5:
        return "🔴 Closed"

    return "🟢 Open"


def formatter_text(info: dict) -> str:
    """Format the info of
    changed courses, in a nice readable shape.

    Args:
        info (str): The info obj to be formatted
    """
    # TODO add detected time stamp

    msg = "A change detected in each of the following "
    for c in info:
        msg += f"\n\nCRN {c['course'].crn}:"
        msg += f"\n \t available seats from {c['status']['available_seats_old']} to {c['status']['available_seats']}"
        msg += f"\n \t waiting list count from {c['status']['waiting_list_count_old']} to {c['status']['waiting_list_count']}"

    return msg


def check_all_and_notify() -> None:
    """Check all tracked courses
    and grouped the notification by user
    then send a notification details

    This method is infinite loop,
    it should be called from a async context.
    """

    while True:
        collection = collect_tracked_courses()
        changed_courses = []

        for _, value in collection.items():
            changed, status = check_changes(value["course"])

            if changed:
                value["status"] = status
                changed_courses.append(value)

        # group `changed_courses` by unique trackers
        courses_by_tracker = {}
        keys = ["course", "status"]
        for c in changed_courses:
            for tracker in c["trackers"]:
                try:
                    courses_by_tracker[tracker.pk].append(
                        {key: c[key] for key in keys}
                    )
                except KeyError:
                    courses_by_tracker[tracker.pk] = [
                        {key: c[key] for key in keys}
                    ]

        for tracker_pk, info in courses_by_tracker.items():
            # TODO create a `NotificationEvent` obj
            # TODO send the notification for each TrackingList's channel

            async_task(
                "notifier.utils.send_notification",
                tracker_pk,
                formatter_change_md(info),
            )

        pprint(courses_by_tracker)

        sleep(5)
