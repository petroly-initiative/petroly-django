from typing import List
from telegram import InlineKeyboardMarkup


def populateTracking(courses: List) -> str:
    """helper method to create a formated message for each course in the tracking list"""
    # for each course we will create a message format
    result = ""
    for course in courses:
        result += f"""**{course["course_number"]}\-{course["section_number"]}**  \- *{course["crn"]}*
        Available Seats: {course["available_seats"]}
        Waitlist: {conditionalColoring(course["waiting_list_count"])}\n\n""";
    return result;

def conditionalColoring(waitlist_count) -> str:
    """helper method to append the correct coloring according to the waitlist count"""
    if waitlist_count == 5:
        return "🔴 Closed"
    else:
        return "🟢 Open"
    