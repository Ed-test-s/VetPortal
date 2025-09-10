from django.urls import path
from . import views

urlpatterns = [
    path("", views.grooming_list, name="grooming_list"),
    path("<slug:slug>/", views.grooming_detail, name="grooming_detail"),
]
