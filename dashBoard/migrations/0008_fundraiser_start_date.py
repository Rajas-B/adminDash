# Generated by Django 3.1.3 on 2021-09-02 08:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dashBoard', '0007_fundraiser_aadhar_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundraiser',
            name='start_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]