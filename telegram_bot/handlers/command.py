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
from django.contrib.auth import get_user_model

from ..models import TelegramProfile
from ..utils import (
    user_from_telegram,
    tracked_courses_,
)
from .. import messages

User = get_user_model()


def escape_md(txt) -> str:
    """To escape special characters:
    `_`,  and `*`"""
    match_md = r"((([_*-\.]).+?\3[^_*-\.]*)*)([_*-\.])"

    return re.sub(match_md, r"\g<1>\\\g<4>", txt)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """the command to start the bot session"""
    # ! if we run this script first, we need to ignore already sent commands
    # to not raise Django error, as it process may not have started yet
    # ! the users need to provide their telegram usernames, so that we can
    # match their names when contacting the bot

    user_id = update.effective_user.id

    if user_id:
        try:
            await update.message.reply_text(
                text=f"Hi {escape_md(update.effective_user.username)}, I am *Petroly* Bot",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

            # try to identify the user form its telegram id
            await user_from_telegram(user_id=user_id, update=update)

            # instantiating the menu button
            await context.bot.set_chat_menu_button(update.effective_chat.id, MenuButtonCommands())  # type: ignore
            await context.bot.set_my_commands(
                commands=[
                    ("/start", "Starts/restarts the bot process"),
                    ("/help", "extensive assistance on all commands"),
                    (
                        "/tracked",
                        "lists all currently tracked courses on the petroly notifier service",
                    ),
                    (
                        "/track",
                        "adds a new section to your tracking list ",
                    ),
                    (
                        "/untrack",
                        "deletes a section from your tracking list ",
                    ),
                    (
                        "/clear",
                        "deletes all tracked courses from your tracking list",
                    )
                ]
            )

        except TelegramProfile.DoesNotExist:
            # TODO provide some kind of sign in with Telegram widget
            await update.message.reply_text(
                text=messages.ACCOUNT_NOT_KNOWN,
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
        text=messages.HELP_MSG,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def tracked_courses(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """a handler to display all currently tracked courses by the user"""

    user_id = update.effective_user.id
    user: User = await user_from_telegram(user_id=user_id, update=update)

    await update.message.reply_text(
        text="""Here is the list of your currently tracked sections: 

        **click on the CRN to copy it to your clipboard**

        """
        + f"{await tracked_courses_(user)}",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
