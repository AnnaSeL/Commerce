# Generated by Django 4.1.6 on 2024-12-08 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0019_auto_20241208_2259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='won',
        ),
    ]
