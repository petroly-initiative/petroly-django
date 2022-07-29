# ! needs to converted it into a conversational handler instead
# pyright: reportIncompatibleMethodOverride=false

from typing import Tuple, Dict, cast
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from telegram_bot.utils import construct_reply_callback_grid, get_courses, get_departments, get_sections, get_terms


DEPT, COURSE, SECTION, CONFIRM, CHECK = range(5);

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # cleaning data from previous sessions
    context.bot.callback_data_cache.clear_callback_data()
    context.bot.callback_data_cache.clear_callback_queries()
    terms = await get_terms()
    term_rows = construct_reply_callback_grid(terms, len(terms))
    print(term_rows)
    await update.message.reply_text(
            text="Please provide the term for the tracked course. Enter /cancel to exit",
            reply_markup= InlineKeyboardMarkup(term_rows)
        )

    return DEPT

async def track_dept(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    query = update.callback_query;
    await query.answer();
    # getting the data from previous step
    selected_term, _ = cast(Tuple[str, Dict[str, str]], query.data)

    terms = await get_terms();
    departments = await get_departments()
    department_rows = construct_reply_callback_grid(
    departments,3, prev_callback_data= {"term": selected_term});

    await query.edit_message_text(
        text=f"Term {selected_term} was selected!\n\nPlease Enter the department of the course. ",
        reply_markup=InlineKeyboardMarkup(department_rows)
    )

    return COURSE;

async def track_courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query;
    await query.answer();

    selected_dept, previous_selections = cast(Tuple[str, Dict[str, str]], query.data);
    previous_selections["department"] = selected_dept;
    
    courses = get_courses(term=previous_selections["term"], dept=selected_dept);
    course_rows = construct_reply_callback_grid(courses,3, prev_callback_data=previous_selections);
   
    await query.edit_message_text(
        text= f"""
        {selected_dept} department was selected for term {previous_selections["term"]}!

        Select a course
        """,
        reply_markup= InlineKeyboardMarkup(course_rows)
    )

    return SECTION

async def track_sections(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    query = update.callback_query;
    await query.answer();

    selected_course, previous_selections = cast(Tuple[str, Dict[str, str]], query.data);
    previous_selections["course"] = selected_course;
    ## passing the user id to prevent adding alerady tracked sections twice
    sections = await get_sections(
        course=selected_course,
        dept=previous_selections["department"],
        term=previous_selections["term"],
        user_id= update.effective_user.id
        )
    section_rows = construct_reply_callback_grid(sections, 1, prev_callback_data=previous_selections);

    await query.edit_message_text(
        text=f"Select a section for {selected_course} - Term {previous_selections['term']}",
        reply_markup=InlineKeyboardMarkup(section_rows))
    

    return CONFIRM;

async def track_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # register in the tracking list for the user

    # ask for another CRN in same settings and restart last step if the user wants

    # else: 
    await update.message.reply_text(
        text="DONE!"
    )

    return ConversationHandler.END;

# ! needs to converted it into a conversational handler instead
async def untrack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """a method to remove a certain course from tracking list via its CRN"""
    if context.args:
        #! we need to handle non-existent CRNs as well
        await update.message.reply_text(
            text=rf"Section with CRN **{context.args[0]}** is successfully untracked\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        await update.message.reply_text(
            text="Cannot untrack a course without specifying the CRN. Please try again and add the correct CRN",
            
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        text = "Process Cancelled."
    )

    return ConversationHandler.END;