# Generated by Django 3.1.3 on 2021-09-02 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashBoard', '0006_fundraiser_photos'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundraiser',
            name='aadhar_number',
            field=models.CharField(default='000000000000', max_length=12),
        ),
    ]
