"""
This module is to define the GraphQL queries and mutations
of the `telegram_bot` app.
"""

from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.permissions import IsAuthenticated
from django_q.tasks import async_task

from .models import Token


@gql.type
class Query:
    """Main entry of all Query types of `notifier` app."""


@gql.type
class Mutation:
    """Main entry of all Mutation types of `notifier` app."""

    @gql.mutation
    def start_telegram_bot(self) -> None:
        """Thi enqueue a task for running the Telegram Bot.
        If there is a task for this method,
        no need to call this mutation.
        """

        async_task(
            "telegram_bot.bot_controller.BotController",
            task_name="telegram-bot",
            hook="hooks.print_obj"
        )

    @gql.mutation(directives=[IsAuthenticated()])
    def get_telegram_token(self, info: Info) -> str:
        """
        Create a obj from `Token` model,
        return the generated token.
        """
        user = info.context.request.user

        obj = Token.objects.create(user=user)

        return obj.token
        
def print_obj(task):
    print(task.result)