"""
This module is to define the fetching, filtering, and processing the data
from the KFUPM API
"""


import json
import logging
from typing import List, Dict, Tuple

import requests as rq
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Q
from django.template import loader

from telegram_bot import messages
from telegram_bot import utils as bot_utils
from evaluation.models import Instructor
from evaluation.schema import crete_global_id
from evaluation.types import InstructorNode

from .models import TrackingList, Course, ChannelEnum

User = get_user_model()
API = "https://registrar.kfupm.edu.sa/api/course-offering"

logger = logging.getLogger("django")


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
    logger.info("cache miss for %s-%s", term, department)

    try:
        res = rq.get(
            API, params={"term_code": term, "department_code": department}
        )
    except rq.RequestException as exc:
        logger.error("Failed fetching %s-%s form API - status: %s", term, department, exc)
        return []

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


def send_notification(user_pk: int, info: str) -> None:
    """Send a notification for every channel in `TrackingList.channels`"""

    user: User = User.objects.get(pk=user_pk)
    channels = user.tracking_list.channels
    # deserialize the dict back
    info_dict: List[Dict] = eval(info)

    # inject `Course` objects and `course_api` into `info_dict`
    for c in info_dict:
        c["course"] = Course.objects.get(pk=c["course_pk"])

    if ChannelEnum.EMAIL in channels:
        send_mail(
            subject="Petroly Radar Detected Changes",
            message=info,
            html_message=loader.render_to_string(
                "notifier/email_changes.html", context={"info": info_dict}
            ),
            recipient_list=[user.email],
            fail_silently=False,
            from_email=None,
        )

    if ChannelEnum.TELEGRAM in channels:
        bot_utils.send_telegram_changes(
            chat_id=user.telegram_profile.id,
            msg=formatter_change_md(info_dict),
        )


def formatter_md(courses: List[Course]) -> str:
    """helper method to create a formatted message for each course in the tracking list"""
    # for each course we will create a message format

    result = ""
    for course in courses:
        result += messages.TRACKED_COURSES.format(
            crn=course.crn,
            course_number=course.raw["course_number"],
            section_number=course.raw["section_number"],
            available_seats=course.available_seats,
            waiting_list_count="🔴 Closed"
            if course.waiting_list_count > 0
            else "🟢 Open",
        )

    return result.replace("-", "\\-")


def formatter_change_md(info: List[Dict[str, Course | Dict]]) -> str:
    """helper method to create a formatted message for each course in the tracking list"""
    # for each course we will create a message format

    result = "Changes detected 🥳\nClick on the CRN number to copy it\n\n"
    for course in info:
        result += messages.CHANGES_DETECTED.format(
            crn=course["course"].crn,
            course_number=course["course"].raw["course_number"],
            section_number=course["course"].raw["section_number"],
            available_seats=course["status"]["available_seats"],
            available_seats_old=course["status"]["available_seats_old"],
            waiting_list_count="🔴 Closed"
            if course["status"]["waiting_list_count"] > 0
            else "🟢 Open",
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
    filters = Q(department=department)

    for name_ in names:
        if "dr" not in name_.lower() and "mr" not in name_.lower():
            # ignore `dr` and `mr` from using in filtering
            filters &= Q(name__icontains=name_)

    queryset = Instructor.objects.filter(filters)
    if len(queryset) == 1:
        return {
            "id": crete_global_id(InstructorNode, queryset[0].pk),
            "profilePic": queryset[0].profile_pic.url,
            "rating": queryset[0].avg()["overall_float"],
        }

    return {}
