# Generated by Django 4.0.6 on 2022-08-24 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifier', '0009_remove_cache_age_remove_cache_swr'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50, unique=True, verbose_name='key')),
                ('status', models.CharField(max_length=10, verbose_name='status')),
            ],
            options={
                'verbose_name': 'status',
                'verbose_name_plural': 'status',
            },
        ),
    ]
