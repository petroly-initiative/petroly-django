"""
Django Models for a Modeling WhatsApp Messaging

These models define the structure for a simple messaging application with Contact, Chat, and Message entities.

Contact Model:
Represents a contact with a phone number, pushname, and creation timestamp.

Attributes:
    number (str): The phone number of the contact, stored as a string.
    pushname (str): The pushname (display name) of the contact, stored as a string.
    created_on (datetime): The timestamp indicating when the contact was created.

Meta:
    verbose_name (str): A human-readable name for a single instance of the model (default: "contact").
    verbose_name_plural (str): A human-readable name for the model in plural form (default: "contacts").

Usage Example:
    contact = Contact.objects.create(number='123456789', pushname='John Doe')


Chat Model:
Represents a chat entity in the application.

Each Chat can be either a one-on-one conversation or a group chat.

Attributes:
    name (str): The name of the chat. For one-on-one conversations, this can be the name
                of the other participant. For group chats, it can be the group name.
    is_group (bool): A boolean field indicating whether the chat is a group chat (True)
                     or a one-on-one conversation (False).

Meta:
    verbose_name (str): A human-readable name for the model, used in the Django admin.
                        Defaults to _("chat").
    verbose_name_plural (str): A human-readable plural name for the model, used in the Django admin.
                              Defaults to _("chats").

Example:
    # Create a one-on-one conversation
    one_on_one_chat = Chat.objects.create(name="John Doe", is_group=False)

    # Create a group chat
    group_chat = Chat.objects.create(name="Project Team", is_group=True)


Message Model:
Represents a message within a chat conversation.

Attributes:
    author (str): The phone number of the message author.
    from_ (str): The sender's identification for the message.
    body (str): The content of the message.
    device_type (str): The type of device from which the message was sent.
    created_on (datetime): The timestamp when the message was created.
    chat (Chat): The chat to which the message belongs (ForeignKey).
    contact (Contact): The contact associated with the message (ForeignKey).

Meta:
    verbose_name (str): A human-readable name for the model (singular).
    verbose_name_plural (str): A human-readable name for the model (plural).
"""

from django.db import models
from django.utils.translation import gettext as _


class Contact(models.Model):
    """
    Represents a contact with a phone number, pushname, and creation timestamp.

    Attributes:
        number (str): The phone number of the contact, stored as a string.
        pushname (str): The pushname (display name) of the contact, stored as a string.
        created_on (datetime): The timestamp indicating when the contact was created.

    Usage Example:
        contact = Contact.objects.create(number='123456789', pushname='John Doe')
    """

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")

    number = models.CharField(_("number"), max_length=15)
    pushname = models.CharField(_("pushname"), max_length=300)
    ignore = models.BooleanField(_("ignore"), default=False)
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)


class Chat(models.Model):
    """
    Represents a chat entity in the application.

    Each Chat can be either a one-on-one conversation or a group chat.

    Attributes:
        name (str): The name of the chat. For one-on-one conversations, this can be the name
                    of the other participant. For group chats, it can be the group name.
        is_group (bool): A boolean field indicating whether the chat is a group chat (True)
                         or a one-on-one conversation (False).

    Example:
        # Create a one-on-one conversation
        one_on_one_chat = Chat.objects.create(name="John Doe", is_group=False)

        # Create a group chat
        group_chat = Chat.objects.create(name="Project Team", is_group=True)
    """

    class Meta:
        verbose_name = _("chat")
        verbose_name_plural = _("chats")

    name = models.CharField(_("name"), max_length=300)
    is_group = models.BooleanField(_("is group"))


class Message(models.Model):
    """
    Represents a message within a chat conversation.

    Attributes:
        author (str): The phone number of the message author.
        from_ (str): The sender's identification for the message.
        body (str): The content of the message.
        device_type (str): The type of device from which the message was sent.
        created_on (datetime): The timestamp when the message was created.
        chat (Chat): The chat to which the message belongs (ForeignKey).
        contact (Contact): The contact associated with the message (ForeignKey).
    """

    class Meta:
        verbose_name = _("message")
        verbose_name_plural = _("messages")

    author = models.CharField(_("phone"), max_length=50)
    from_id = models.CharField(_("from"), max_length=50)
    body = models.TextField(_("body"))
    device_type = models.CharField(_("device type"), max_length=15)
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name=_("chat"))
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, verbose_name=_("contact")
    )

    def __str__(self) -> str:
        return str(self.body)
