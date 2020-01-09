from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from Website.models import Donation, Institution, UserForm
from django.contrib.auth.models import User

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


class AddDonation(View):
    def get(self, request):
        return render(request, 'form.html')


class Login(View):
    def get(self, request):
        if request.session.get('email'):
            email = request.session['email']
        else:
            email = ''
        return render(request, 'login.html', {'email': email})


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
