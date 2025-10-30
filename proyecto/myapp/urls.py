from django.contrib import admin 
from django.urls import path, include
from django.views import View
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("upload/", views.upload_documents, name="upload"),
    path("quiz/", views.quiz, name="quiz"),
    path("api/ask/", views.ask_question, name="ask_question"),
]

