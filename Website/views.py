import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from Website.models import Donation, Institution, UserForm, Category
from django.contrib.auth.models import User
import json

# Create your views here.


class LandingPage(View):
    def get(self, request):
        charities = Institution.objects.filter(type=1)
        non_gov_org = Institution.objects.filter(type=2)
        local_charities = Institution.objects.filter(type=3)

        # paginator_charities = Paginator(charities, 5)
        # paginator_non_gov_org = Paginator(non_gov_org, 5)
        # paginator_local_charities = Paginator(local_charities, 5)

        donations = Donation.objects.all()
        donated_bags = 0
        for donation in donations:
            donated_bags += donation.quantity

        return render(request, 'index.html', {'donated_bags': donated_bags, 'donations': donations.count(),
                                              'charities': charities, 'non_gov_org': non_gov_org,
                                              'local_charities': local_charities})


class AddDonation(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        categories = Category.objects.all()
        institutions = Institution.objects.all()
        return render(request, 'form.html', {'categories': categories, 'institutions': institutions})


class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')

        if request.session.get('email'):
            email = request.session['email']
        else:
            email = ''
        if request.GET.get('next'):
            valuenext = request.GET.get('next')
        else:
            valuenext = ''
        return render(request, 'login.html', {'email': email, 'next': valuenext})

    def post(self, request):
        user = authenticate(request, username=request.POST['email'], password=request.POST['password'])
        valuenext = request.POST.get('next')

        if user is not None:
            login(request, user)
            if str(valuenext) != '':
                return redirect('donate')
            else:
                return redirect('home')
        else:
            email = request.POST['email']
            return render(request, 'login.html', {'message': 'Podany login i/lub hasło są nieprawidłowe!',
                                                  'email': email})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('home')


class Register(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):

        filled = {'first_name': request.POST['first_name'], 'last_name': request.POST['last_name'],
                  'email': request.POST['email']}
        request_password = request.POST['password']

        password_has_capital_char = False
        password_contains_num = False
        for char in request_password:
            if char in '1234567890':
                password_contains_num = True

            if char.isupper():
                password_has_capital_char = True

        if request_password == request.POST['password2'] and len(request_password) >= 5 and password_contains_num and \
                password_has_capital_char:
            new_user_form = UserForm(request.POST)
            request.session['email'] = request.POST['email']

            if new_user_form.is_valid():
                try:
                    User.objects.create_user(username=request.POST['email'], email=request.POST['email'],
                                             password=request.POST['password'], first_name=request.POST['first_name'],
                                             last_name=request.POST['last_name'])
                except IntegrityError:
                    return render(request, 'register.html',
                                  {'message': 'Użytkownik z takim adresem e-mail już istnieje!', 'filled': filled})
                return redirect('login')
            else:
                return render(request, 'register.html',
                              {'message': 'Podaj poprawny adres e-mail!', 'filled': filled})

        elif len(request_password) < 5 or not password_has_capital_char or not password_contains_num:
            return render(request, 'register.html',
                          {'message': 'Hasło zbyt łatwe ( min. pięć znaków, w tym jedna cyfra i jedna wielka litera )!',
                           'filled': filled})
        else:
            return render(request, 'register.html', {'message': 'Powtórzone hasło nie pasuje do oryginalnego!',
                                                     'filled': filled})

# ----------- AJAX views


class AjaxGetOrganizationsId(View):
    def post(self, request):
        received_data = json.loads(request.body)
        category_list = received_data['category_list']
        organizations = Institution.objects.filter(categories__in=category_list).values('id')
        organizations_id = [element for element in organizations]
        data = {'organizations_id': organizations_id}
        return JsonResponse(data)
