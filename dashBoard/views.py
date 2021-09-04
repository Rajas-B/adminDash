from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from pyotp import TOTP
from .tasks import sleepy
from .models import Photos, User, Donor, Fundraiser
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage

# Create your views here.

def home(request):
    if 'fundraiser_auth' in request.session:
        del request.session['fundraiser_auth']
    context = {'active': 'home'}
    return render(request, 'dashBoard/index.html', context = context)

def contact(request):
    return render(request, 'dashBoard/contact.html')

def courses(request):
    fundraiser = Fundraiser.objects.filter(soft_delete=False, completed=False)
    fundraiser = fundraiser.order_by("-start_date").all()
    fundraisers = []
    i = 0
    length = len(fundraiser)
    while(i<length//3):
        fundraisers.append(fundraiser[i*3:i*3+3])
        i+=1
    j = length%3
    if j > 0:
        fundraisers.append(fundraiser[length-j:])
    return render(request, 'dashBoard/courses.html', {
        'fundraisers': fundraisers
    })

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
    if request.method == "POST":
        patient_name = request.POST["patient_name"]
        phone = request.POST["phone"]
        name = request.POST["name"]
        if name == "":
            name = patient_name
        rel_to_patient = request.POST["rel_to_patient"]
        if rel_to_patient == "":
            rel_to_patient = "SELF"
        email = request.POST["email"]
        aadhar = request.POST["aadhar"]
        amount_needed = request.POST["amount_needed"]
        video_url = request.POST["video_url"]
        description = request.POST["description"]
        campaign_name = request.POST["campaign_name"]
        medical_treatment = request.POST["medical_treatment"]
        hospital_name = request.POST["hospital_name"]
        totp = TOTP('base32secret3232')
        otp = totp.now()
        fundraiser = {
            'patient_name': patient_name, 'phone': phone, 'name': name, 'rel_to_patient': rel_to_patient,
            'email': email, 'aadhar': aadhar, 'amount_needed': amount_needed, 'video_url': video_url, 
            'description': description, 'campaign_name': campaign_name, 'medical_treatment': medical_treatment,
            'hospital_name': hospital_name,'otp': otp,
        }
        request.session['fundraiser_auth'] = fundraiser
        return HttpResponseRedirect(reverse('consent'))

    return render(request, 'dashBoard/start.html')

def consent(request):
    if 'fundraiser_auth' in request.session:
        if request.method == 'POST':
            fundraiser_auth = request.session["fundraiser_auth"]
            otp = request.POST['otp']
            if otp == request.session['fundraiser_auth']['otp']:
                main_pic = request.FILES.get('main_pic')
                other_pics = request.FILES.getlist('other_pics')
                medical_report = request.FILES.getlist('medical_report')
                operation_bill = request.FILES.getlist('operation_bill')
                for i in range(len(other_pics)):
                    other_pics[i].name = other_pics[i].name.split('.')[0] + f'_{i}.' + other_pics[i].name.split('.')[-1]
                for i in range(len(medical_report)):
                    medical_report[i].name = medical_report[i].name.split('.')[0] + f'_{i}.' + medical_report[i].name.split('.')[-1]
                for i in range(len(operation_bill)):
                    operation_bill[i].name = operation_bill[i].name.split('.')[0] + f'_{i}.' + operation_bill[i].name.split('.')[-1]
                try:
                    fundraiser = Fundraiser.objects.create(campaign_name = fundraiser_auth["campaign_name"], phone_number = fundraiser_auth["phone"], email = fundraiser_auth["email"],aadhar_number = fundraiser_auth["aadhar"],patient_name = fundraiser_auth["patient_name"], relation_to_patient = fundraiser_auth["rel_to_patient"], patient_rel_name=fundraiser_auth["name"], campaign_description=fundraiser_auth["description"], campaign_photo = main_pic, medical_treatment=fundraiser_auth["medical_treatment"],amount_needed=fundraiser_auth["amount_needed"], video_url=fundraiser_auth["video_url"])
                    fundraiser.save()
                    for image in other_pics:
                        pics = Photos.objects.create(fundraiser = fundraiser, photo = image, pic_or_doc=False)
                        pics.save()
                    for image in medical_report:
                        pics = Photos.objects.create(fundraiser=fundraiser, photo=image, pic_or_doc=True)
                        pics.save()
                    for image in operation_bill:
                        pics = Photos.objects.create(fundraiser=fundraiser, photo=image, pic_or_doc=True)
                        pics.save()
                    return HttpResponseRedirect(reverse('home'))
                except:
                    return render(request, 'dashBoard/consent.hmtl', {
                        'database_error': 'Oops! Something went wrong.'
                    })
            else:
                return render(request, 'dashBoard/consent.html', {
                    "otp_error": "OTP does not match"
                })
        return render(request, 'dashBoard/consent.html', {
            'otp': request.session['fundraiser_auth']['otp'], 'hospital_name': request.session["fundraiser_auth"]['hospital_name'],
            'patient_name': request.session["fundraiser_auth"]["patient_name"], 'aadhar': request.session["fundraiser_auth"]["aadhar"],
            'name': request.session["fundraiser_auth"]["name"], 'medical_treatment': request.session["fundraiser_auth"]["medical_treatment"],
            })
    return HttpResponseRedirect(reverse('home'))

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

def fundraiser_page(request, campaign):
    fundraiser = Fundraiser.objects.get(campaign_url = campaign)
    if fundraiser is None:
        return HttpResponseRedirect(reverse('home'))
    photos = Photos.objects.filter(fundraiser = fundraiser, pic_or_doc=False)
    return render(request, 'dashBoard/course-details.html', {
        'fundraiser': fundraiser, 'photos': photos, 'number': range(1, len(photos)+1)
    })

# Test views

def test(request):
    if 'image' in request.session:
        image = request.session['image']
        return render(request, 'dashBoard/test.html', context = {'image': image})
    return render(request, 'dashBoard/test.html', context = {'image': 'Lol'})
# Footer views

def faq(request):
    return render(request, 'dashBoard/faq.html')

def privacy(request):
    return render(request, 'dashBoard/privacy.html')

def refund(request):
    return render(request, 'dashBoard/refund.html')

def terms(request):
    return render(request, 'dashBoard/terms.html')












