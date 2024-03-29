# Generated by Django 4.1.3 on 2022-11-11 14:47

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ("notifier", "0012_alter_cache_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trackinglist",
            name="channels",
            field=multiselectfield.db.fields.MultiSelectField(
                choices=[
                    ("sms", "sms"),
                    ("push", "push"),
                    ("email", "email"),
                    ("whatsapp", "whatsapp"),
                    ("telegram", "telegram"),
                ],
                default="email",
                max_length=100,
            ),
        ),
    ]
