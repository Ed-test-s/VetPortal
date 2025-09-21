from django.urls import path
from . import views

urlpatterns = [
    path("", views.journal_home, name="journal_home"),  # список статей
    path("<slug:slug>/", views.article_detail, name="article_detail"),  # отдельная статья
]
