"""
This module is to define the fetching, filtering, and processing the data
from the KFUPM API
"""

import os
import json
import logging
from typing import List, Dict, Tuple

import requests as rq
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q
from django.template import loader
from django.utils.timezone import now

from telegram_bot import messages
from telegram_bot import utils as bot_utils
from evaluation.models import Instructor
from evaluation.schema import crete_global_id
from evaluation.types import InstructorNode

from .models import TrackingList, Course, ChannelEnum, Cache

logger = logging.getLogger(__name__)
User = get_user_model()

API = "https://registrar.kfupm.edu.sa/api/course-offering"
proxies = {
    "http": os.environ.get("API_HTTP_PROXY"),
    "https": os.environ.get("API_HTTPS_PROXY"),
}


def fetch_data(term: str, department: str) -> List[Dict]:
    """This load data from our DB."""

    try:
        obj = Cache.objects.get(term=term, department=department)

    except Cache.DoesNotExist:
        request_data(term, department)
        obj = Cache.objects.get(term=term, department=department)

    return obj.get_data()


def request_data(term, department) -> None:
    """This method performs a GET request to the KFUPM API
    for the specific args.

    Args:
        term (str): e.g., 202210
        department (str): e.g., 'ICS'

    Returns:
        dict: the response JSON after converting into dict object,
    """

    logger.info("Requesting %s-%s", term, department)

    try:
        res = rq.get(
            API,
            params={"term_code": term, "department_code": department},
            proxies=proxies,
            timeout=20,
        )

    except rq.Timeout:
        logger.warning(
            "Timeout on %s-%s",
            term,
            department,
        )
        raise

    except rq.RequestException as exc:
        logger.error(
            "Failed fetching %s-%s from API - Exception: %s",
            term,
            department,
            exc,
        )
        raise

    data = json.loads(res.content)["data"]

    if data:
        obj, _ = Cache.objects.get_or_create(term=term, department=department)
        obj.data = data
        obj.stale = False
        obj.updated_on = now()
        obj.save()

    else:
        logger.info("No data was returned from API")


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
            course_number=course["course"].raw["course_number"],
            section_number=course["course"].raw["section_number"],
            available_seats=course["status"]["available_seats"],
            available_seats_old=course["status"]["available_seats_old"],
            waiting_list_count="🟢 Open"
            if course["status"]["waiting_list_count"] > 0
            else "🔴 Closed",
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
