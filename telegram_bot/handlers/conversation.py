"""
This module handles the conversation sequence to track ot untrack
a course.
"""

# ! needs to converted it into a conversational handler instead
# pyright: reportIncompatibleMethodOverride=false

from typing import Dict, cast
from enum import Enum

from telegram import (
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from telegram_bot.utils import (
    construct_reply_callback_grid,
    get_courses,
    get_departments,
    get_sections,
    get_terms,
    submit_section,
    fetch_terms,
)


class CommandEnum(Enum):
    """This helps to understand what the message
    wants to do from"""

    DEPT = 0
    COURSE = 1
    SECTION = 2
    CONFIRM = 3
    CRN = 4
    CLOSE = 5


async def track(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> CommandEnum:
    # cleaning data from previous sessions
    context.bot.callback_data_cache.clear_callback_data()
    context.bot.callback_data_cache.clear_callback_queries()
    context.user_data.clear()
    terms = await get_terms(update.effective_chat.id)
    term_rows = construct_reply_callback_grid(
        terms, len(terms), is_callback_different=True
    )
    terms = await fetch_terms()
    term_rows = construct_reply_callback_grid(
        terms, len(terms), is_callback_different=True
    )
    # print(term_rows)
    await update.message.reply_text(
        text="Please provide the term for the tracked course. Enter /cancel to exit",
        reply_markup=InlineKeyboardMarkup(term_rows),
    )

    return CommandEnum.DEPT  # type: ignore


async def track_dept(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    query = update.callback_query
    await query.answer()
    # getting the data from previous step
    selected_term = cast(str, query.data)
    context.user_data["term"] = selected_term
    departments = await get_departments()
    department_rows = construct_reply_callback_grid(departments, 3)

    await query.edit_message_text(
        text=f"Term {selected_term} was selected\\!\n\n"
        + "Please Enter the department of the course\\. ",
        reply_markup=InlineKeyboardMarkup(department_rows),
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return CommandEnum.COURSE


async def track_courses(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> CommandEnum:
    query = update.callback_query
    await query.answer()
    selected_dept = cast(str, query.data)
    context.user_data["department"] = selected_dept
    courses = get_courses(
        term=context.user_data.get("term", "TERM_NOT_FOUND"),
        dept=selected_dept,
    )
    row_length = len(courses) if len(courses) < 3 else 3
    course_rows = construct_reply_callback_grid(courses, row_length=row_length)

    await query.edit_message_text(
        text=f"""
        **{selected_dept}** department was selected for term **{context.user_data.get("term", "TERM_NOT_FOUND")}**\\!

        Select a course
        """,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(course_rows),
    )

    return CommandEnum.SECTION


async def track_sections(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    selected_course = cast(str, query.data)
    context.user_data["course"] = selected_course
    ## passing the user id to prevent adding already tracked sections twice
    sections = await get_sections(
        course=selected_course,
        dept=context.user_data.get("department", "DEPT_NOT_FOUND"),
        term=context.user_data.get("term", "TERM_NOT_FOUND"),
        user_id=update.effective_user.id,
    )
    section_rows = construct_reply_callback_grid(
        sections, 1, is_callback_different=True
    )

    ## ! handle by requesting the CRN explicitly
    if len(sections) > 100:
        ## cache all crns in the current course instead of fetching again
        context.user_data["sections"] = [
            (section[1]["crn"], section[1]["seats"], section[1]["waitlist"])
            for section in sections
        ]
        await query.edit_message_text(
            text="Too many sections to display, please type the course CRN",
            reply_markup=None,
        )
        return CommandEnum.CRN

    await query.edit_message_text(
        text=f"Select a section for {selected_course} \\- "
        + f"Term {context.user_data.get('term', 'TERM_NOT_FOUND')}",
        reply_markup=InlineKeyboardMarkup(section_rows),
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return CommandEnum.CONFIRM


async def track_crn(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> CommandEnum:

    crn = update.message.text.strip()
    ## check if the CRN exists
    current_crns = list(
        {section[0] for section in context.user_data.get("sections", "NULL")}
    )
    print(crn, current_crns)
    if not crn in current_crns:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="CRN does not exist or is already tracked, "
            + "please enter a valid CRN that you haven't tracked before",
        )
        return CommandEnum.CRN

    target_section = [
        section
        for section in context.user_data.get("sections", "NULL")
        if section[0] == crn
    ][0]

    await submit_section(
        crn=target_section[0],
        seats=target_section[1],
        waitlist_count=target_section[2],
        user_id=update.effective_chat.id,
        term=context.user_data.get("term", "TERM_NOT_FOUND"),
        dept=context.user_data.get("department", "DEPT_NOT_FOUND"),
    )
    options = construct_reply_callback_grid(
        [("Yes", "True"), ("No", "False")],
        row_length=2,
        is_callback_different=True,
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Section with CRN **`{target_section[0]}`** "
        + "Tracked successfully!. Would you like to track another course?",
        reply_markup=InlineKeyboardMarkup(options),
    )

    context.user_data["from_crn"] = True
    return CommandEnum.CLOSE


async def track_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    # register in the tracking list for the user
    query = update.callback_query
    await query.answer()

    selected_section = cast(Dict[str, str | int], query.data)
    # ask for another CRN in same settings and restart last step if the user wants
    await submit_section(
        crn=selected_section["crn"],
        seats=selected_section["seats"],
        waitlist_count=selected_section["waitlist"],
        user_id=update.effective_chat.id,
        term=context.user_data.get("term", "TERM_NOT_FOUND"),
        dept=context.user_data.get("department", "DEPT_NOT_FOUND"),
    )
    options = construct_reply_callback_grid(
        [("Yes", "True"), ("No", "False")],
        row_length=2,
        is_callback_different=True,
    )
    # else:
    await query.edit_message_text(
        text=f"Section with CRN `{selected_section['crn']}` "
        + "Tracked successfully!. Would you like to track another course?",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(options),
    )

    return CommandEnum.CLOSE


async def track_close(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> CommandEnum | int:
    query = update.callback_query
    await query.answer()

    if query.data:
        return (
            CommandEnum.CRN
            if context.user_data.get("from_crn", False)
            else CommandEnum.SECTION
        )

    await query.edit_message_text(
        text="Wait for the notifications, thank you for using the Petroly bot!",
        reply_markup=None,
    )
    return ConversationHandler.END


# display a list of all tracked courses
async def untrack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """a method to remove a certain course from tracking list via its CRN"""
    if context.args:
        #! we need to handle non-existent CRNs as well
        await update.message.reply_text(
            text=f"Section with CRN **{context.args[0]}** is successfully untracked\\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        await update.message.reply_text(
            text="Cannot untrack a course without specifying the CRN. "
            "Please try again and add the correct CRN",
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        text="All right, we won't change anything."
    )

    return ConversationHandler.END
