# Generated by Django 4.1.6 on 2024-12-04 20:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_rename_price_listing_bid_alter_listing_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='bid',
            new_name='price',
        ),
    ]
