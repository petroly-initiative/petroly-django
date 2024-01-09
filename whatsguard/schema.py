"""
This module is to define the GraphQL queries and mutations
of the `whatsguard` app.
"""

from dataclasses import asdict
from pydantic_core.core_schema import none_schema

import strawberry
import strawberry.django
from strawberry.types import Info
from strawberry_django.permissions import IsAuthenticated

from whatsguard.models import Chat, Contact, Message
from whatsguard.types import ChatType, CheckResult, ContactType, MessageType
from whatsguard.utils import is_spam_or_ad


@strawberry.type
class Mutation:
    @strawberry.mutation
    def check_message(
        self, info: Info, message: MessageType, chat: ChatType, contact: ContactType
    ) -> CheckResult:
        try:
            result, reason = is_spam_or_ad(message.body)
        except Exception as e:
            print(e)
            return CheckResult(is_spam=False, message_pk=None, reason="")

        try:
            if result:
                chat_obj, _ = Chat.objects.get_or_create(**asdict(chat))
                contact_obj, _ = Contact.objects.get_or_create(**asdict(contact))

                msg_obj = Message.objects.create(
                    **asdict(message), chat=chat_obj, contact=contact_obj
                )
                return CheckResult(is_spam=result, message_pk=msg_obj.pk, reason=reason)

            return CheckResult(is_spam=result, message_pk=None, reason=reason)

        except Exception as e:
            print(e)
            return CheckResult(is_spam=False, message_pk=None, reason=reason)
