from enum import unique
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import pre_save
from adminDash.util import unique_slug_generator, unique_campaign_name_generator
from django import forms

class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=False, null=False, unique=True)
    mediangels = models.BooleanField(default=False)
    slug = models.SlugField(max_length = 250, null = True, blank = True)

def slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
pre_save.connect(slug_generator, sender=Donor)

def content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.campaign_url, ext)
    return filename

class Fundraiser(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign_name = models.CharField(max_length = 200, null=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=False, null=False)
    aadhar_number = models.CharField(max_length=12, null=False, default='000000000000')
    campaign_url = models.SlugField(max_length= 250, null=False, blank = True)
    patient_name = models.CharField(max_length = 250, null=False)
    relation_to_patient = models.CharField(max_length = 250, null = False)
    patient_rel_name = models.CharField(max_length=240, null=False)
    campaign_description = models.TextField(null=False)
    campaign_photo = models.ImageField(null=True, upload_to=content_file_name)
    amount_needed = models.FloatField(null=False)
    amount_raised = models.FloatField(null=False, default=0)
    video_url = models.URLField(max_length = 250, null=False, unique=True)
    completed = models.BooleanField(default = False, null = False)
    soft_delete = models.BooleanField(default=True, null=False)
    ending_title = models.CharField(max_length=250, null=True, blank=True)
    ending_description = models.TextField(null=True, blank=True)

def url_generator(sender, instance, *args, **kwargs):
    if not instance.campaign_url:
        instance.campaign_url = unique_campaign_name_generator(instance)
pre_save.connect(url_generator, sender=Fundraiser)



class Photos(models.Model):
    fundraiser = models.ForeignKey(Fundraiser, on_delete=models.CASCADE)
    photo = models.ImageField(null=False)
    pic_or_doc = models.BooleanField(null=False, default=False)