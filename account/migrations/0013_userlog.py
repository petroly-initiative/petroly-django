# Generated by Django 4.1.7 on 2023-03-24 18:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0012_alter_profile_major"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ip", models.GenericIPAddressField(verbose_name="IP")),
                ("function", models.CharField(max_length=100, verbose_name="function")),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, verbose_name="created on"),
                ),
                (
                    "updated_on",
                    models.DateTimeField(auto_now=True, verbose_name="updated on"),
                ),
            ],
            options={
                "verbose_name": "user log",
                "verbose_name_plural": "user logs",
            },
        ),
    ]
