"""
This module is to define the fetching, filtering, and processing the data
from the KFUPM API
"""


import json
from typing import List, Dict, Tuple

import requests as rq
from django.contrib.auth import get_user_model
from faas_cache_dict import FaaSCacheDict
from .models import TrackingList, Course

User = get_user_model()
API = "https://registrar.kfupm.edu.sa/api/course-offering"

# Constants
CACHE_AGE = 60 * 60  # seconds

# create in-memory cache
cache = FaaSCacheDict(default_ttl=CACHE_AGE, max_size_bytes="10M")


def fetch_data(term: int, department: str) -> List[Dict]:
    """This method performs a GET request to the KFUPM API
    for the specific args.

    Args:
        term (int): e.g., 202210
        department (str): e.g., 'ICS'

    Returns:
        dict: the response JSON after converting into dict object,
    """

    try:
        return cache[(term, department)]
    except KeyError:
        # handle cache miss
        res = rq.get(
            API, params={"term_code": term, "department_code": department}
        )

        assert res.ok
        data = json.loads(res.content)["data"]

        cache[(term, department)] = data  # store data into cache
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
    # TODO this should be compared against old status
    # TODO add fields indicate by how many the increase is

    course_info = get_course_info(course)
    keys = ["available_seats", "waiting_list_count"]
    info = {key: course_info[key] for key in keys}

    if info["available_seats"] > 0 or info["waiting_list_count"] > 0:
        return (True, info)

    return (False, info)


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


def check_all_and_notify() -> None:
    """Check all tracked courses
    and grouped the notification by user
    then send a notification details
    """
    collection = collect_tracked_courses()
    changed_courses = []

    for _, value in collection.items():
        changed, status = check_changes(value["course"])

        if changed:
            value["status"] = status
            changed_courses.append(value)

    print(changed_courses)
    # TODO group `changed_courses` by tracker


check_all_and_notify()
