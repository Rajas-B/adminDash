from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from pyotp import TOTP
from .tasks import sleepy
from .models import User, Donor
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def home(request):
    context = {'active': 'home'}
    return render(request, 'dashBoard/index.html', context = context)

def contact(request):
    return render(request, 'dashBoard/contact.html')

def courses(request):
    return render(request, 'dasBoard/courses.html')

def mediangels(request):
    if request.method == "POST":
        name = request.POST["new_name"]
        email = request.POST["new_email"]
        phone = request.POST["new_phone"]
        password = request.POST["new_password"]
        confirmation = request.POST["new_password_confirm"]
        if password != confirmation:
            return render(request, "dashBoard/mediangels.html", {
                "sign_up_message": "Passwords must match."
            })
        totp = TOTP('base32secret3232')
        otp = totp.now()
        
        request.session['new_user_medi'] = {'name': name, 'email': email, 'phone': phone, 'password': password, 'otp': otp}
        return HttpResponseRedirect(reverse('mediangel_consent'))
    return render(request, 'dashBoard/mediangels.html')

def start_fundraiser(request):
    return render(request, 'dashBoard/start.html')

def mediangel_signup(request):
    if request.method == "POST":
        name = request.POST["new_name"]
        email = request.POST["new_email"]
        phone = request.POST["new_phone"]
        password = request.POST["new_password"]
        confirmation = request.POST["new_password_confirmation"]
        if password != confirmation:
            return render(request, "dashBoard/mediangels.html", {
                "sign_up_message": "Passwords must match."
            })
        totp = TOTP('base32secret3232')
        otp = totp.now()
        
        request.session['new_user_medi'] = {'name': name, 'email': email, 'phone': phone, 'password': password, 'otp': otp}
        return HttpResponseRedirect(reverse('mediangel_consent'))
    return HttpResponseRedirect(reverse('home'))

def mediangel_consent(request):
    if 'new_user_medi' in request.session:
        new_user = request.session['new_user_medi']
        if request.method == 'POST':
            if request.POST["otp_confirm"] == new_user['otp']:
                try:
                    user = User.objects.create_user(new_user['name'], new_user['email'], new_user['password'])
                    user.save()
                    donor = Donor.objects.create(user = user, phone_number = new_user['phone'], mediangels = True)
                    donor.save()
                except IntegrityError:
                    return HttpResponseRedirect(reverse('mediangels'))
                login(request, user)
                del request.session['new_user_medi']
                return HttpResponseRedirect(reverse('home'))
            else:
                return render(request, "dashBoard/mediconsent.html", {
                            "otp_message": "OTP does not match."
                        })
        return render(request, "dashBoard/mediconsent.html", {'otp': new_user['otp']})
    return HttpResponseRedirect(reverse('home'))


# Footer views

def faq(request):
    return render(request, 'dashBoard/faq.html')

def privacy(request):
    return render(request, 'dashBoard/privacy.html')

def refund(request):
    return render(request, 'dashBoard/refund.html')

def terms(request):
    return render(request, 'dashBoard/terms.html')














# try:
#     user = User.objects.create_user(name, email, password)
#     user.save()
# except IntegrityError:
#     return render(request, "auctions/register.html", {
#         "message": "Username already taken."
#     })
# try:
#     donor = Donor
# login(request, user)
# return HttpResponse("Hello")