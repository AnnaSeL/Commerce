# Generated by Django 4.1.6 on 2024-12-08 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_alter_bid_listing'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='listings',
            field=models.ManyToManyField(blank=True, related_name='listings', to='auctions.listing'),
        ),
    ]
