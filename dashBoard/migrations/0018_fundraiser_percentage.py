# Generated by Django 3.1.3 on 2021-09-04 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashBoard', '0017_auto_20210903_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundraiser',
            name='percentage',
            field=models.IntegerField(default=0),
        ),
    ]
