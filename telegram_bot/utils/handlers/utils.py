"""
This module contains some utilities for handling telegram commands
"""

from typing import List


def populate_tracking(courses: List) -> str:
    """helper method to create a formatted message for each course in the tracking list"""
    # for each course we will create a message format
    result = ""
    for course in courses:
        result += f"""**{course["course_number"]}\\-{course["section_number"]}**  \\- *{course["crn"]}*
        Available Seats: {course["available_seats"]}
        Waiting list: {conditional_coloring(course["waiting_list_count"])}\n\n"""
    return result


def conditional_coloring(wait_list_count) -> str:
    """helper method to append the correct coloring according to
    the waiting list count"""

    if wait_list_count == 5:
        return "🔴 Closed"

    return "🟢 Open"
