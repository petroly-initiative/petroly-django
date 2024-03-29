# Generated by Django 4.1.3 on 2022-11-12 08:18

import data
from django.db import migrations
import django_choices_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ("notifier", "0013_alter_trackinglist_channels"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="department",
            field=django_choices_field.fields.TextChoicesField(
                choices=[
                    ("AE", "Aerospace Engineering"),
                    ("ARE", "Architectural Engineering"),
                    ("ARC", "Architecture"),
                    ("BIOE", "Bioengineering"),
                    ("CE", "Civil & Environmental Engg"),
                    ("CEM", "Construction Engg & Management"),
                    ("CHE", "Chemical Engineering"),
                    ("CHEM", "Chemistry"),
                    ("CIE", "Control & Instrumentation Engineering"),
                    ("COE", "Computer Engineering"),
                    ("CPG", "CPG"),
                    ("CRP", "City & Regional Planning"),
                    ("EE", "Electrical Engineering"),
                    ("FIN", "Finance"),
                    ("GS", "Global Studies"),
                    ("IAS", "Islamic & Arabic Studies"),
                    ("ICS", "Information & Computer Science"),
                    ("LS", "Life Sciences"),
                    ("MATH", "Mathematics & Statistics"),
                    ("MBA", "Business Administration"),
                    ("ME", "Mechanical Engineering"),
                    ("MSE", "Material Sciences and Engineering"),
                    ("MGT", "Management & Marketing"),
                    ("PE", "Physical Education"),
                    ("PETE", "Petroleum Engineering"),
                    ("PHYS", "Physics"),
                    ("ISE", "Industrial and Systems Engineering"),
                    ("SWE", "Software Engineering"),
                    ("BUS", "Business"),
                    ("ENGL", "English"),
                    ("ACCT", "Accounting"),
                ],
                choices_enum=data.SubjectEnum,
                max_length=4,
                verbose_name="department",
            ),
        ),
    ]
