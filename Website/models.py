from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=64)


class Institution(models.Model):

    INSTITUTION_TYPE_CHOICES = (
        (1, 'fundacja'),
        (2, 'organizacja pozarządowa'),
        (3, 'zbiórka lolakna'),
    )

    name = models.CharField(max_length=128)
    description = models.TextField(null=True)
    type = models.IntegerField(choices=INSTITUTION_TYPE_CHOICES, default=1)
    categories = models.ManyToManyField(Category)


class Donation(models.Model):
    quantity = models.IntegerField()
    categories = models.ManyToManyField(Category)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    address = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=6)
    pick_up_date = models.DateField()
    pick_up_time = models.TimeField()
    pick_up_comment = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, default=True)
