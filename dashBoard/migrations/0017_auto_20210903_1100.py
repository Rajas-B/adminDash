# Generated by Django 3.1.3 on 2021-09-03 05:30

import dashBoard.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashBoard', '0016_remove_fundraiser_campaign_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundraiser',
            name='campaign_photo',
            field=models.ImageField(default='default.JPG', upload_to=dashBoard.models.content_file_name),
        ),
        migrations.AddField(
            model_name='fundraiser',
            name='hospital_name',
            field=models.TextField(default='Test case', max_length=250),
        ),
    ]