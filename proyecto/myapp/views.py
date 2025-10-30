from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseForbidden


# Create your views here.

def home(request):
    return HttpResponse("HOME VIEW")