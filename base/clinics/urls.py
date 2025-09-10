from django.urls import path
from . import views

urlpatterns = [
    path("", views.clinic_list, name="clinic_list"),
    path("<slug:slug>/", views.clinic_detail, name="clinic_detail"),
]
