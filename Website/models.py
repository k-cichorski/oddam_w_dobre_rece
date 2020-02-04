from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm

# Create your models here.


class Category(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = 'Kategoria'
        verbose_name_plural = 'Kategorie'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ['name']


class Institution(models.Model):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Instytucja'
        verbose_name_plural = 'Instytucje'

    INSTITUTION_TYPE_CHOICES = (
        (1, 'fundacja'),
        (2, 'organizacja pozarządowa'),
        (3, 'zbiórka lolakna'),
    )

    name = models.CharField(max_length=128, verbose_name='Nazwa')
    description = models.TextField(null=True, verbose_name='Opis')
    type = models.IntegerField(choices=INSTITUTION_TYPE_CHOICES, default=1, verbose_name='Rodzaj instytucji')
    categories = models.ManyToManyField(Category, verbose_name='Kategorie')


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'type', 'categories']


class Donation(models.Model):
    def __str__(self):
        return self.user.username + ' ' + str(self.pick_up_date)

    class Meta:
        verbose_name = 'Dotacja'
        verbose_name_plural = 'Dotacje'

    quantity = models.IntegerField()
    categories = models.ManyToManyField(Category)
    institution = models.ForeignKey(Institution, on_delete=models.DO_NOTHING)
    address = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=6)
    pick_up_date = models.DateField()
    pick_up_time = models.TimeField()
    pick_up_comment = models.TextField(null=True)
    picked_up = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.TextField()


class PasswordRetrieval(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.TextField()


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    fields = ['quantity', 'categories', 'institution', 'address', 'phone_number', 'city', 'zip_code', 'pick_up_date',
              'pick_up_time', 'pick_up_comment', 'picked_up', 'user']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']


class DonationForm(ModelForm):
    class Meta:
        model = Donation
        exclude = ['user', 'institution', 'categories']
