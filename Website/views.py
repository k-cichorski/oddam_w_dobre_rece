import json

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from Website.models import Donation, Institution, UserForm, Category, DonationForm
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

    def post(self, request):
        new_donation_form = DonationForm(request.POST)
        if new_donation_form.is_valid():
            chosen_categories = request.POST.getlist('categories')
            categories = Category.objects.filter(id__in=chosen_categories)
            institution = Institution.objects.get(id=request.POST['institution'])
            new_donation = Donation.objects.create(quantity=request.POST['quantity'], institution=institution,
                                                   address=request.POST['address'],
                                                   phone_number=request.POST['phone_number'],
                                                   city=request.POST['city'], zip_code=request.POST['zip_code'],
                                                   pick_up_date=request.POST['pick_up_date'], pick_up_time=request.POST['pick_up_time'],
                                                   pick_up_comment=request.POST['pick_up_comment'], user=request.user)
            new_donation.categories.set(categories)

            return render(request, 'form-confirmation.html', {'message': 'Dziękujemy za przesłanie formularza. '
                                                                         'Na maila prześlemy wszelkie informacje o odbiorze.'})

        else:
            return render(request, 'form-confirmation.html', {'message': 'Coś poszło nie tak... Spróbuj jeszcze raz'})


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
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return render(request, 'register.html')

    def post(self, request):

        filled = {'first_name': request.POST['first_name'], 'last_name': request.POST['last_name'],
                  'email': request.POST['email']}
        request_password = request.POST['password']

        if request_password == request.POST['password2'] and validate_password(request_password):
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

        elif validate_password(request_password) is False:
            return render(request, 'register.html',
                          {'message': 'Hasło zbyt łatwe ( min. pięć znaków, w tym jedna cyfra i jedna wielka litera )!',
                           'filled': filled})
        else:
            return render(request, 'register.html', {'message': 'Powtórzone hasło nie pasuje do oryginalnego!',
                                                     'filled': filled})


class ChangePassword(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        return render(request, 'change-password.html')

    def post(self, request):
        user = User.objects.get(username=request.user.username)
        old_password = request.POST['old_password']
        if user.check_password(old_password) is False:
            message = 'Stare hasło jest niepoprawne!'

        else:
            new_password = request.POST['new_password']
            re_new_password = request.POST['re_new_password']

            if new_password == re_new_password and validate_password(new_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return render(request, 'change-password.html', {'success': 'Hasło zostało zmienione!'})

            elif new_password != re_new_password:
                message = 'Powtórzone hasło nie pasuje do oryginalnego!'

            else:
                message = 'Hasło zbyt łatwe ( min. pięć znaków, w tym jedna cyfra i jedna wielka litera )!'

        return render(request, 'change-password.html', {'message': message})


class UserProfile(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        user_donations = Donation.objects.filter(user=request.user).order_by('picked_up')
        return render(request, 'user-profile.html', {'donations': user_donations})


# ----------- AJAX views


class AjaxGetOrganizationsId(View):
    def post(self, request):
        received_data = json.loads(request.body)
        category_list = received_data['category_list']
        organizations = Institution.objects.filter(categories__in=category_list).values('id')
        organizations_id = [element for element in organizations]
        data = {'organizations_id': organizations_id}
        return JsonResponse(data)


# ------------ Functions

def validate_password(password):
    password_has_capital_char = False
    password_contains_num = False
    for char in password:
        if char in '1234567890':
            password_contains_num = True

        if char.isupper():
            password_has_capital_char = True

    if password_contains_num and password_has_capital_char and len(password) >= 5:
        return True
    else:
        return False
