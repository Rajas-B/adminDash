from django.contrib import admin
from .models import Donor, Fundraiser, Payments, Photos
# Register your models here.
admin.site.register(Donor)
admin.site.register(Fundraiser)
admin.site.register(Photos)
admin.site.register(Payments)