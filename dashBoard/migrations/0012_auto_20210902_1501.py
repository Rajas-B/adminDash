# Generated by Django 3.1.3 on 2021-09-02 09:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashBoard', '0011_auto_20210902_1449'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photos',
            name='fundraiser',
        ),
        migrations.DeleteModel(
            name='Fundraiser',
        ),
        migrations.DeleteModel(
            name='Photos',
        ),
    ]
