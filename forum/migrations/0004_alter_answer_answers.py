# Generated by Django 3.2.2 on 2021-06-12 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_question_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='answers',
            field=models.ManyToManyField(null=True, related_name='answersfor2m', to='forum.Answer'),
        ),
    ]
