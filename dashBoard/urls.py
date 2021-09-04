from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("contact-us", views.contact, name="contact"),
    path("fundraisers", views.courses, name="courses"),
    path("mediangels", views.mediangels, name="mediangels"),
    path("mediconsent", views.mediangel_consent, name="mediangel_consent"),
    path("start-fundraiser", views.start_fundraiser, name="start-fundraiser"),
    path("fundraiser-consent", views.consent, name="consent"),
    path("fundraiser-page/<str:campaign>", views.fundraiser_page, name="fundraiser_page"),

    # footer urls
    path("faq", views.faq, name="faq"),
    path("privacy-policy", views.privacy, name="privacy-policy"),
    path("refund-policy", views.refund, name="refund-policy"),
    path("terms-of-service", views.terms, name="terms-of-service"),

    # test urls
    path("test", views.test, name="test"),
]
