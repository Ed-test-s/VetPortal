from django.urls import path
from . import views

urlpatterns = [
    path("", views.pharmacy_list, name="pharmacy_list"),
    path("<slug:slug>/", views.pharmacy_detail, name="pharmacy_detail"),
]
