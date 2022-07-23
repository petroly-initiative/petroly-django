"""
Here are messages templates, to be used later.

type:
    - `MD` indicate this message to be compiled with markdown.
    - `Text` indicate this message is plain text.
"""


# MD
help_msg_text = """Use **/start** to run this bot\.

use /list to view all tracked sections

use **/untrack** CRN to untrack the section with the specified CRN number
For example, /delete 101235 : deletes the section with CRN 101235 from your tracking list

use **/track** CRN to track a new course using the section CRN"""

# MD
welcome_after_verifying = """
Welcome %i \.
We connected your Telegram to your Petroly account\.
"""

# Text
account_not_know = """Sorry, we didn't recognize your Telegram account. 
To do so, follow the steps in our website to connect your Petroly account with your Telegram's one."""

# MD
changes_detected = """**{course_number}\\-{section_number}**  \\- *{crn}*
Available Seats: {available_seats_old} ➡️  {available_seats}
Waiting list: {waiting_list_count}\n\n"""

# MD
tracked_courses = """**{course_number}\\-{section_number}**  \\- *{crn}*
Available Seats: {available_seats}
Waiting list: {waiting_list_count}\n\n"""
