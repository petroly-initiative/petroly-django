# Generated by Django 4.0.6 on 2022-08-24 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifier', '0010_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='status',
            field=models.CharField(choices=[('up', 'Up'), ('down', 'Down')], max_length=10, verbose_name='status'),
        ),
    ]
