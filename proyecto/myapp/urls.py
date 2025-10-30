from django.contrib import admin 
from django.urls import path, include
from django.views import View
from . import views


urlpatterns = [
    path("",views.home, name="home"),
]

