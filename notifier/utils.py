"""
This module is to define the fetching, filtering, and processing the data
from the KFUPM API
"""


import json
from typing import List, Dict, Tuple
from pprint import pprint
from time import sleep

import requests as rq
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django_q.tasks import async_task

from .models import TrackingList, Course

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


def send_notification(user_pk: int, info: str) -> None:
    user = User.objects.get(pk=user_pk)
    send_mail(
        subject="Changes detected",
        message=str(info),
        recipient_list=[user.email],
        fail_silently=False,
        from_email=None,
    )


def formatter(info: dict) -> str:
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
        for c in changed_courses:
            for tracker in c["trackers"]:
                try:
                    courses_by_tracker[tracker.pk].append(c)
                except KeyError:
                    courses_by_tracker[tracker.pk] = [c]

        for pk, info in courses_by_tracker.items():
            # TODO create a `NotificationEvent` obj
            # TODO send the notification for each TrackingList's channel

            async_task(
                "notifier.utils.send_notification",
                pk,
                formatter(info),
            )

        pprint(courses_by_tracker)

        sleep(5)
