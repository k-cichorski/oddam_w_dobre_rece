"""Oddam_W_Dobre_Rece URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from Website.views import LandingPage, AddDonation, Login, Logout, Register, AjaxGetOrganizationsId

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPage.as_view(), name='home'),
    re_path(r'^donate/$(?i)', AddDonation.as_view(), name='donate'),
    re_path(r'^login/$(?i)', Login.as_view(), name='login'),
    re_path(r'^logout/$(?i)', Logout.as_view(), name='logout'),
    re_path(r'^register/$(?i)', Register.as_view(), name='register'),
    path('ajax/organizations/id/', AjaxGetOrganizationsId.as_view()),
]