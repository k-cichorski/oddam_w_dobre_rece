import json
import secrets

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from Website.models import Donation, Institution, UserForm, Category, DonationForm, EmailVerification
from Oddam_W_Dobre_Rece import settings
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

        donations = Donation.objects.filter(picked_up=True)
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
        user = authenticate(request, username=request.POST['email'].casefold(), password=request.POST['password'])
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

        registration_email = request.POST['email'].casefold()

        filled = {'first_name': request.POST['first_name'], 'last_name': request.POST['last_name'],
                  'email': registration_email}
        request_password = request.POST['password']

        if request_password == request.POST['password2'] and validate_password(request_password):
            new_user_form = UserForm(request.POST)
            request.session['email'] = registration_email

            if new_user_form.is_valid():
                try:
                    new_user = User.objects.create_user(username=registration_email,
                                                        email=registration_email,
                                                        password=request.POST['password'],
                                                        first_name=request.POST['first_name'],
                                                        last_name=request.POST['last_name'],
                                                        is_active=False)
                except IntegrityError:
                    return render(request, 'register.html',
                                  {'message': 'Użytkownik z takim adresem e-mail już istnieje!', 'filled': filled})

                new_token = secrets.token_urlsafe(32)
                EmailVerification.objects.create(user=new_user, token=new_token)
                subject = 'Link weryfikacyjny do serwisu Oddam W Dobre Ręce'
                message = f'''Aby dokończyć rejestrację konta, kliknij w poniższy link:
                http://127.0.0.1:8000/token/{new_token}'''
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [registration_email,]
                send_mail(subject, message, email_from, recipient_list)
                return render(request, 'login.html', {'message': 'Kliknij w link wysłany w wiadomości email,'
                                                                 ' aby potwierdzić rejestrację i umożliwić logowanie'})
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


def ActivateAccount(request, token):
    new_user = EmailVerification.objects.get(token=token).user
    new_user.is_active = True
    new_user.save()
    return render(request, 'login.html', {'message': 'Twoje konto zostało zweryfikwoane, możesz się zalogować'})


class ProfileSettings(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        return render(request, 'profile-settings.html')

    def post(self, request):
        user = User.objects.get(username=request.user.username)
        if 'new_info' in request.POST:
            if user.check_password(request.POST['password']) is False:
                info_message = 'Wpisz poprawne hasło!'
                return render(request, 'profile-settings.html', {'info_message': info_message})
            else:
                new_first_name = request.POST['new_first_name']
                new_last_name = request.POST['new_last_name']
                new_email = request.POST['new_email']

                if len(new_first_name) > 0:
                    user.first_name = new_first_name
                if len(new_last_name) > 0:
                    user.last_name = new_last_name
                if len(new_email) > 0:
                    if user.email.casefold() == new_email.casefold():
                        info_message = 'Ten adres e-mail jest już zajęty!'
                        return render(request, 'profile-settings.html', {'info_message': info_message})
                    else:
                        user.email = new_email
                        user.username = new_email
                try:
                    user.save()
                except IntegrityError:
                    info_message = 'Ten adres e-mail jest już zajęty!'
                    return render(request, 'profile-settings.html', {'info_message': info_message})
                else:
                    success_message = 'Dane zostały zmienione!'
                    return render(request, 'profile-settings.html', {'success_message': success_message})
        else:
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
                    return render(request, 'profile-settings.html', {'success': 'Hasło zostało zmienione!'})

                elif new_password != re_new_password:
                    message = 'Powtórzone hasło nie pasuje do oryginalnego!'

                else:
                    message = 'Hasło zbyt łatwe ( min. pięć znaków, w tym jedna cyfra i jedna wielka litera )!'

            return render(request, 'profile-settings.html', {'message': message})


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
        organizations = Institution.objects.all()
        for category in category_list:
            organizations = organizations.filter(categories__id=category).values('id')
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

