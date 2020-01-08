from django.shortcuts import render
from django.views import View
from Website.models import Donation, Institution

# Create your views here.


class LandingPage(View):
    def get(self, request):
        donations = Donation.objects.all()
        donated_bags = 0
        for donation in donations:
            donated_bags += donation.quantity
        return render(request, 'index.html', {'donated_bags': donated_bags, 'donations': donations.count()})


class AddDonation(View):
    def get(self, request):
        return render(request, 'form.html')


class Login(View):
    def get(self, request):
        return render(request, 'login.html')


class Register(View):
    def get(self, request):
        return render(request, 'register.html')
