"""
This module handles the conversation sequence to track ot untrack
a course.
"""

# ! needs to converted it into a conversational handler instead
# pyright: reportIncompatibleMethodOverride=false

from enum import Enum
from typing import Dict, cast

from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from telegram import InlineKeyboardMarkup, Update

from telegram_bot.utils import (
    clear_tracking,
    construct_reply_callback_grid,
    get_courses,
    get_departments,
    get_sections,
    get_terms,
    get_tracked_crns,
    submit_section,
    untrack_section,
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
    SELECT = 6


async def track(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> CommandEnum:
    """starting point for the /track command"""
    # cleaning data from previous sessions
    context.bot.callback_data_cache.clear_callback_data()
    context.bot.callback_data_cache.clear_callback_queries()
    context.user_data.clear()
    # getting available terms and create reply buttons
    terms = await get_terms(update.effective_chat.id)
    term_rows = construct_reply_callback_grid(
        terms, len(terms), is_callback_different=True
    )
    # display reply with constructed buttons for dept selection step
    await update.message.reply_text(
        text="Please provide the term for the tracked course. Enter /cancel to exit",
        reply_markup=InlineKeyboardMarkup(term_rows),
    )

    return CommandEnum.DEPT  # type: ignore


async def track_dept(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> CommandEnum:
    """a handler for department selection step in /track command"""

    # waiting for the user response
    query = update.callback_query
    await query.answer()
    # getting the data from previous step
    selected_term = cast(str, query.data)
    # storing persistent data for next steps
    context.user_data["term"] = selected_term
    # getting all departments' data
    departments = await get_departments()
    department_rows = construct_reply_callback_grid(departments, 3)

    # displaying the reply and buttons for next step
    await query.edit_message_text(
        text=f"Term {selected_term} was selected\\!\n\n"
        + "Please Enter the department of the course\\. \n\nEnter /cancel to exit",
        reply_markup=InlineKeyboardMarkup(department_rows),
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return CommandEnum.COURSE


async def track_courses(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> CommandEnum | int:
    """a handler for course selection step in /track command"""

    # waiting for the user response
    query = update.callback_query
    await query.answer()
    selected_dept = cast(str, query.data)
    # storing persistent data for next steps
    context.user_data["department"] = selected_dept
    # getting courses under the selected department and term
    courses = get_courses(
        term=context.user_data.get("term", "TERM_NOT_FOUND"),
        dept=selected_dept,
    )
    if len(courses) == 0:
        await query.edit_message_text(
            text= f"Oops! seems like there are no offered courses for {selected_dept} department in term {context.user_data.get('term', 'TERM_NOT_FOUND')}"
        )
        return ConversationHandler.END
    row_length = len(courses) if len(courses) < 3 else 3
    course_rows = construct_reply_callback_grid(courses, row_length=row_length)
    # displaying the reply and buttons for next step
    await query.edit_message_text(
        text=f"""
        **{selected_dept}** department was selected for term **{context.user_data.get("term", "TERM_NOT_FOUND")}**\\!

        Select a course

        Enter /cancel to exit
        """,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(course_rows),
    )

    return CommandEnum.SECTION


async def track_sections(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> CommandEnum | int:
    """a handler for section selection step in /track command"""
    # waiting for the user response
    query = update.callback_query
    await query.answer()
    selected_course = cast(str, query.data)
    # storing persistent data for next steps
    context.user_data["course"] = selected_course
    ## passing the user id to prevent adding already tracked sections twice
    sections = await get_sections(
        course=selected_course,
        dept=context.user_data.get("department", "DEPT_NOT_FOUND"),
        term=context.user_data.get("term", "TERM_NOT_FOUND"),
        user_id=update.effective_user.id,
    )
   
    if len(sections) == 0:
        await query.edit_message_text(
            text= f"Oops! seems like there are no offered sections for {selected_course} course in term {context.user_data.get('term', 'TERM_NOT_FOUND')}"
        )
        return ConversationHandler.END

    section_rows = construct_reply_callback_grid(
        sections,row_length= 1, is_callback_different=True
    )

    

    ## ! handle overflow by requesting the CRN explicitly
    if len(sections) > 100:
        ## cache all crns in the current course instead of fetching again
        ## storing all DB-specific param temporarily to store the data correctly
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
        + f"Term {context.user_data.get('term', 'TERM_NOT_FOUND')}\n\nEnter /cancel to exit",
        reply_markup=InlineKeyboardMarkup(section_rows),
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return CommandEnum.CONFIRM


async def track_crn(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> CommandEnum | int:
    """a handler for CRN-based section input step in /track command"""

    ## processing user input
    crn = update.message.text.strip()
    ## check if the CRN exists
    current_crns = list(
        {section[0] for section in context.user_data.get("sections", "NULL")}
    )

    if not crn in current_crns:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="CRN does not exist or is already tracked, "
            "please enter a valid CRN that you haven't tracked before\n\nEnter /cancel to exit",
        )
        return CommandEnum.CRN
    ## getting the required data to store a section in our DB
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

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Section with CRN `{crn}` Tracked successfully, Wait for our notifications\\!",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=None,
    )

    return ConversationHandler.END


async def track_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> CommandEnum | int:
    """a handler for button-based section input step in /track command"""
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

    # else:
    await query.edit_message_text(
        text=f"Section with CRN `{selected_section['crn']}` "
        "Tracked successfully, Wait for our notifications\\!",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=None,
    )

    return ConversationHandler.END


# display a list of all tracked courses
async def untrack(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int | CommandEnum:
    """a method to remove a certain section from tracking list via its CRN"""

    crns = await get_tracked_crns(user_id=update.effective_chat.id)
    context.user_data.clear()
    ## if CRNs exceed 100, enter the CRN in text
    if len(crns) > 100:
        context.user_data["crns"] = crns
        await update.message.reply_text(
            text="Your CRNs have exceeded display limits, "
            "please enter the CRN you would like to untrack. Use /cancel to stop the command",
            
        )
        return CommandEnum.CRN

    ## if CRNs do not overflow create the button grid
    crn_rows = construct_reply_callback_grid(crns, row_length=2)
    await update.message.reply_text(
        text="Please select the CRN to untrack from your CRN list. Use /cancel to stop the command",
        reply_markup=InlineKeyboardMarkup(crn_rows),
    )
    return CommandEnum.SELECT


async def untrack_crn(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int | CommandEnum:
    """a handler for CRN-based input in /untrack command"""

    ## checking if the CRN exits in the user CRN list
    crn = update.message.text.strip()
    if crn not in context.user_data.get("crns", []):
        await update.message.reply_text(
            text="Entered CRN does not exist in your tracking list",
        )
        return CommandEnum.CRN

    await untrack_section(crn=crn, user_id=update.effective_chat.id)
    await update.message.reply_text(
        text=f"Section with CRN `{crn} was untracked successfully!",
    )
    return ConversationHandler.END


async def untrack_select(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """a handler for button-based input in /untrack command"""

    ## waiting for user response
    query = update.callback_query
    await query.answer()
    crn = cast(str, query.data)
    ## perform unfrocking from DB
    await untrack_section(crn=crn, user_id=update.effective_chat.id)
    await query.edit_message_text(
        text=f"Section with CRN `{crn}` was untracked successfully\!",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """a handler to cancel ongoing conversational commands"""

    await update.message.reply_text(
        text="All right, we won't change anything."
    )

    return ConversationHandler.END


async def clear(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> CommandEnum:
    """a starting point for a full clear of selected terms' operation"""

    terms = await get_terms(update.effective_chat.id)
    terms.append(("All terms", "ALL"))
    term_rows = construct_reply_callback_grid(
        terms, len(terms), is_callback_different=True
    )
    await update.message.reply_text(
        text="Please select a term to clear, "
        "or clear all tracked terms at once. Use /cancel to stop the command",
        reply_markup=InlineKeyboardMarkup(term_rows),
    )

    return CommandEnum.CONFIRM


async def clear_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """a handler for term selection in /clear command"""

    query = update.callback_query
    await query.answer()

    target_term = query.data

    await clear_tracking(target_term, update.effective_chat.id)

    await query.edit_message_text(
        text=f"Untracked {'All sections' if target_term == 'ALL' else target_term + ' sections'} successfully!",
        reply_markup=None,
    )

    return ConversationHandler.END
