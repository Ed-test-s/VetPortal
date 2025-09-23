from django.urls import path
from . import views

urlpatterns = [
    path("", views.pharmacy_list, name="pharmacy_list"),
    path("my/", views.my_pharmacy, name="my_pharmacy"),
    path("<slug:slug>/", views.pharmacy_detail, name="pharmacy_detail"),
]
