# ! needs to converted it into a conversational handler instead
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram import Update


async def track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ! we should give the course details for a more comfortable UX

    if context.args:  # type: ignore
        await update.message.reply_text(
            text=f"Section with CRN **{context.args[0]}** is successfully tracked\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        await update.message.reply_text(
            text="Cannot untrack a course without specifying the CRN. Please try again and add the correct CRN"
        )


# ! needs to converted it into a conversational handler instead
async def untrack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """a method to remove a certain course from tracking list via its CRN"""
    if context.args:
        #! we need to handle non-existent CRNs as well
        await update.message.reply_text(
            text=f"Section with CRN **{context.args[0]}** is successfully untracked\!",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        await update.message.reply_text(
            text="Cannot untrack a course without specifying the CRN. Please try again and add the correct CRN"
        )
