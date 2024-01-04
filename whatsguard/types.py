"""
This module defines the types pf this `whatsguard` app
to be used from `schema` module.
"""


import strawberry
import strawberry.django
from strawberry import auto
from strawberry.types import Info

from .models import Chat, Contact, Message


@strawberry.django.input(Message)
class MessageType:
    """A type for `Message` model."""

    author: auto
    from_id: auto
    body: auto
    device_type: auto


@strawberry.django.input(Chat)
class ChatType:
    """A type for `Chat` model."""

    name: auto
    is_group: auto


@strawberry.django.input(Contact)
class ContactType:
    """A type for `Contact` model."""

    number: auto
    pushname: auto


@strawberry.type
class CheckResult:
    is_spam: bool
    message_pk: int | None
