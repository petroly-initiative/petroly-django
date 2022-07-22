"""
This module handles main entry commands for our Telegram Bot.

methods:
    - `start`
    - `help`
    - `list`
"""
import re

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonCommands,
    Update,
)

from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..handlers.utils import populate_tracking
from ..models import TelegramProfile
from ..utils import user_from_telegram
from .messages import help_msg_text

courses = []


def escape_md(txt) -> str:
    match_md = r"((([_*]).+?\3[^_*]*)*)([_*])"

    return re.sub(match_md, "\g<1>\\\\\g<4>", txt)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """the command to start the bot session"""
    # ! if we run this script first, we need to ignore already sent commands
    # to not raise Django error, as it process may not have started yet
    # ! the users need to provide their telegram usernames, so that we can
    # match their names when contacting the bot

    user_id = update.effective_user.id

    if user_id:
        try:
            # try to identify the user form its telegram id
            await user_from_telegram(user_id)

            await update.message.reply_text(
                text=f"Hi {escape_md(update.effective_user.username)}, I am *Petroly* Bot",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            # instantiating the menu button
            await context.bot.set_chat_menu_button(update.effective_chat.id, MenuButtonCommands())  # type: ignore
            await context.bot.set_my_commands(
                commands=[
                    ("/start", "Starts/restarts the bot process"),
                    ("/help", "extensive assistance on all commands"),
                    (
                        "/list",
                        "lists all currently tracked courses on the petroly notifier service",
                    ),
                    (
                        "/track",
                        "adds new section to your tracking list (/track CRN)",
                    ),
                    (
                        "/untrack",
                        "deletes the section from your tracking list (/untrack CRN)",
                    ),
                ]
            )

        except TelegramProfile.DoesNotExist:
            await update.message.reply_text(
                text="Sorry, You are not signed in the Petroly Notifier Service for Telegram bots, to do so, visit our website",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Visit petroly.co",
                                url="https://petroly.co",
                            )
                        ]
                    ]
                ),
            )


# displaying all possible commands by the user
async def help_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """command for helping users with extra instructions on each command"""
    await update.message.reply_text(
        text=help_msg_text,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def tracked_courses(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """a handler to display all currently tracked courses by the user"""

    user_id = update.effective_user.id

    if user_id:
        try:
            user = await user_from_telegram(user_id)
        except TelegramProfile.DoesNotExist:
            await update.message.reply_text(
                text="You don't have a TelegramProfile."
            )
            return

    else:
        await update.message.reply_text(text="We could not find your ID.")

    await update.message.reply_text(
        text=f"Here is the list of your currently tracked sections: \n\n {str(user.tracking_list.courses.all())}",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
