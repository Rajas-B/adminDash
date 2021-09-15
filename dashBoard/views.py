from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from pyotp import TOTP
from .models import Photos, User, Donor, Fundraiser, Payments
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
import stripe
from dashBoard.vendor.twilio_otp import otp_auth  
from django.conf import settings
from urllib.parse import quote_plus

stripe.api_key = settings.STRIPE_PRIVATE_KEY

# Create your views here.

def home(request):
    if 'fundraiser_auth' in request.session:
        del request.session['fundraiser_auth']
    if 'new_user_medi' in request.session:
        del request.session['new_user_medi']
    if 'payment_in_progress' in request.session:
        del request.session['payment_in_progress']
    fundraisers = Fundraiser.objects.all()
    fundraisers = fundraisers.order_by("-start_date").all()
    if fundraisers.count() >= 3:
        fundraisers = fundraisers[:3]
    context = {'active': 'home', 'fundraisers': fundraisers}
    return render(request, 'dashBoard/index.html', context = context)

def contact(request):
    return render(request, 'dashBoard/contact.html')

def courses(request):
    fundraiser = Fundraiser.objects.filter(completed=False)
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
    if 'donor' in request.session:
        return HttpResponseRedirect(reverse('home'))
    if request.method == "POST":
        name = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=name, password=password)
        if user is not None:
            donor = Donor.objects.get(user=user)
            login(request, user)
            request.session["donor"] = donor.pk
            return HttpResponseRedirect(reverse("home"))
        else:
            return render(request, "dashBoard/mediangels.html", {
                "message": "Invalid email and/or password."
            })
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
        otp_auth(phone, otp)
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
                fundraiser = Fundraiser.objects.create(campaign_name = fundraiser_auth["campaign_name"], phone_number = fundraiser_auth["phone"], email = fundraiser_auth["email"],aadhar_number = fundraiser_auth["aadhar"],patient_name = fundraiser_auth["patient_name"], relation_to_patient = fundraiser_auth["rel_to_patient"], patient_rel_name=fundraiser_auth["name"], campaign_description=fundraiser_auth["description"], campaign_photo = main_pic, medical_treatment=fundraiser_auth["medical_treatment"],amount_needed=int(fundraiser_auth["amount_needed"]), video_url=fundraiser_auth["video_url"])
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

            else:
                return render(request, 'dashBoard/consent.html', {
                    "otp_error": "OTP does not match"
                })
        return render(request, 'dashBoard/consent.html', {
            'hospital_name': request.session["fundraiser_auth"]['hospital_name'],
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
        confirmation = request.POST["new_password_confirm"]
        if password != confirmation:
            return render(request, "dashBoard/mediangels.html", {
                "sign_up_message": "Passwords must match."
            })
        totp = TOTP('base32secret3232')
        otp = totp.now()
        otp_auth(phone, otp)
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
        return render(request, "dashBoard/mediconsent.html")
    return HttpResponseRedirect(reverse('home'))

def fundraiser_page(request, campaign):
    fundraiser = Fundraiser.objects.get(campaign_url = campaign)
    if fundraiser is None:
        return HttpResponseRedirect(reverse('home'))
    photos = Photos.objects.filter(fundraiser = fundraiser, pic_or_doc=False)
    payment = Payments.objects.filter(fundraiser=fundraiser)
    payment = payment.order_by("-amount").all()
    share_string = quote_plus(fundraiser.campaign_name)
    if payment.count() >= 3:
        top_donors = payment[:3]
    else:
        top_donors = payment
    context = {
        'fundraiser': fundraiser, 'photos': photos, 'number': range(1, len(photos)+1), 'donations': payment.count(),
        'top_donors': top_donors, 'share_string': share_string,
    }
    if 'donor' in request.session:
        donor = Donor.objects.get(pk=request.session["donor"])
        context['donor'] = True
        context['phone_number'] = donor.phone_number
    return render(request, 'dashBoard/course-details.html', context=context)

# Payment gateway
def create_checkout_session(request):
    if request.method == "POST":
        name = request.POST["name"]
        if name == "":
            name = "Well wisher"
        phone = request.POST["phone"]
        email = request.POST["email"]
        fundraiser_id = request.POST["fundraiser"]
        amount_value = request.POST["amount_paying"]
        if amount_value == "custom_amount":
            amount_value = request.POST["custom_value"]
        amount_value = int(amount_value)
        try:
            fundraiser = Fundraiser.objects.get(id=fundraiser_id)
            request.session['payment_in_progress'] = {'fundraiser': fundraiser_id, 'amount': amount_value, 'phone': phone, 
                                                    'email': email, 'name': name}
            checkout_session = stripe.checkout.Session.create(

                    line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                        'name': f'Donating to {fundraiser.campaign_name}',
                        },
                        'unit_amount': f'{amount_value*100}',
                    },
                    'quantity': 1,
                    }],

                    payment_method_types=[
                    'card',
                    ],

                    mode='payment',
                    success_url= 'http://127.0.0.1:8000' + '/success',
                    cancel_url= 'http://127.0.0.1:8000' + '/cancel',

                )
            return HttpResponseRedirect(checkout_session.url)
        except:
            return HttpResponseRedirect(f'fundraiser-page/{fundraiser.campaign_url}')
    return HttpResponseRedirect(reverse("home"))

def create_checkout_session_mediangel(request):
    if 'donor' in request.session:
        if request.method == "POST":
            fundraiser_id = request.POST["fundraiser"]
            amount_value = request.POST["amount_paying"]
            if amount_value == "custom_amount":
                amount_value = request.POST["custom_value"]
            amount_value = int(amount_value)
            try:
                fundraiser = Fundraiser.objects.get(id=fundraiser_id)
                request.session['payment_in_progress'] = {'fundraiser': fundraiser_id, 'amount': amount_value, 'donor': True}
                checkout_session = stripe.checkout.Session.create(

                    line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                        'name': f'Donating to {fundraiser.campaign_name}',
                        },
                        'unit_amount': f'{amount_value*100}',
                    },
                    'quantity': 1,
                    }],

                    payment_method_types=[
                    'card',
                    ],

                    mode='payment',
                    success_url= 'http://127.0.0.1:8000' + '/success',
                    cancel_url= 'http://127.0.0.1:8000' + '/cancel',

                )
                return HttpResponseRedirect(checkout_session.url)
            except:
                return HttpResponseRedirect(f'fundraiser-page/{fundraiser.campaign_url}')

def payment_success(request):
    if 'payment_in_progress' in request.session:
        payment_details = request.session["payment_in_progress"]
        if 'donor' in request.session:
            donor = Donor.objects.get(pk=request.session['donor'])
            amount = payment_details['amount']
            fundraiser = Fundraiser.objects.get(pk=payment_details['fundraiser'])
            payment = Payments.objects.create(donor=donor, fundraiser=fundraiser, name=donor.user.username, amount=amount,phone_number=donor.phone_number, email=donor.user.email)
            payment.save()
            fundraiser.amount_raised += amount
            if fundraiser.amount_raised >= fundraiser.amount_needed:
                fundraiser.completed = True
            fundraiser.save()
        else:
            name = payment_details['name']
            email = payment_details['email']
            amount = payment_details['amount']
            phone = payment_details['phone']
            fundraiser = Fundraiser.objects.get(pk=payment_details['fundraiser'])
            payment = Payments.objects.create(fundraiser=fundraiser, name=name, amount=amount, phone_number=phone, email=email)
            payment.save()
            fundraiser.amount_raised += amount
            if fundraiser.amount_raised >= fundraiser.amount_needed:
                fundraiser.completed = True
            fundraiser.save()
        del request.session['payment_in_progress']

        return render(request, 'dashBoard/success.html', {'amount': amount, 'fundraiser': fundraiser})
    return HttpResponseRedirect(reverse('home'))

def payment_cancelled(request):
    if 'payment_in_progress' in request.session:
        
        del request.session['payment_in_progress']
        return render(request, 'dashBoard/cancel.html')
    return HttpResponseRedirect(reverse('home'))


def mediangel_logout(request):
    if 'donor' in request.session:
        logout(request)
        return HttpResponseRedirect(reverse('home'))
    return HttpResponseRedirect(reverse('home'))
# Test views

def test(request):
    if 'image' in request.session:
        image = request.session['image']
        return render(request, 'dashBoard/test.html', context = {'image': image})
    return render(request, 'dashBoard/test.html', context = {'image': 'Lol'})

# Footer views
def about(request):
    return render(request, 'dashBoard/about.html')

def faq(request):
    return render(request, 'dashBoard/faq.html')

def privacy(request):
    return render(request, 'dashBoard/privacy.html')

def refund(request):
    return render(request, 'dashBoard/refund.html')

def terms(request):
    return render(request, 'dashBoard/terms.html')












