# Generated by Django 3.2.10 on 2022-01-10 16:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communities', '0007_alter_community_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_communities', to=settings.AUTH_USER_MODEL, verbose_name='likes'),
        ),
        migrations.AlterField(
            model_name='community',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_communities', to=settings.AUTH_USER_MODEL, verbose_name='owner'),
        ),
        migrations.RemoveField(
            model_name='community',
            name='report',
        ),
        migrations.AddField(
            model_name='community',
            name='report',
            field=models.ManyToManyField(blank=True, related_name='reporteded_communities', to=settings.AUTH_USER_MODEL, verbose_name='likes'),
        ),
    ]