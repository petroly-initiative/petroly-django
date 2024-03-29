# Generated by Django 4.0.6 on 2022-08-20 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifier', '0003_rename_raw_info_course_raw'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='updated on')),
                ('stale', models.BooleanField(default=False, verbose_name='stale')),
                ('age', models.IntegerField(verbose_name='age')),
                ('swr', models.IntegerField(verbose_name='swr')),
                ('data', models.JSONField(verbose_name='data')),
                ('department', models.CharField(max_length=7, verbose_name='department')),
                ('term', models.CharField(max_length=7, verbose_name='term')),
            ],
            options={
                'verbose_name': 'cache item',
                'verbose_name_plural': 'cache items',
            },
        ),
    ]
