# Generated by Django 3.1.3 on 2021-09-02 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashBoard', '0014_fundraiser_medical_treatment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundraiser',
            name='campaign_url',
            field=models.SlugField(blank=True, max_length=250, null=True),
        ),
    ]