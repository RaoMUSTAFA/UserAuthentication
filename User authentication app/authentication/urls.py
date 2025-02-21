from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path ('signup',views.signup, name="signup"),
    path ('signin',views.signup, name="signin"),
    path ('signout',views.signup, name="signout"),
    path ('activate/<uidb64>/<token>',views.activate, name="activate")
]