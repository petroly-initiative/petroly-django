from django.contrib import admin

from whatsguard.models import Chat, Contact, Message

admin.site.register([Chat, Contact, Message])
