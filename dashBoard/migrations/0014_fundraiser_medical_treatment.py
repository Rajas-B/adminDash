# Generated by Django 3.1.3 on 2021-09-02 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashBoard', '0013_fundraiser_photos'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundraiser',
            name='medical_treatment',
            field=models.TextField(default='Test case', max_length=250),
        ),
    ]