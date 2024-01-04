"""
This module is to define the GraphQL queries and mutations
of the `whatsguard` app.
"""

from dataclasses import asdict
import strawberry
import strawberry.django
from strawberry.types import Info
from strawberry_django.permissions import IsAuthenticated
from whatsguard.models import Chat, Contact, Message

from whatsguard.types import ChatType, ContactType, MessageType
from whatsguard.utils import is_spam_or_ad


@strawberry.type
class Mutation:
    @strawberry.mutation
    def check_message(
        self, info: Info, message: MessageType, chat: ChatType, contact: ContactType
    ) -> bool:
        try:
            result = is_spam_or_ad(message.body)
        except:
            return False

        try:
            chat_obj, _ = Chat.objects.get_or_create(**asdict(chat))
            contact_obj, _ = Contact.objects.get_or_create(**asdict(contact))

            Message.objects.create(
                **asdict(message), chat=chat_obj, contact=contact_obj
            )

        except:
            pass
        return result
