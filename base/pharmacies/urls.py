from django.urls import path
from . import views


urlpatterns = [
    # path("my/", views.my_pharmacy, name="my_pharmacy"),
    path("dashboard/", views.pharmacy_dashboard, name="pharmacy_dashboard"),

    path("", views.pharmacy_list, name="pharmacy_list"),

    path("<slug:slug>/", views.pharmacy_detail, name="pharmacy_detail"),

    path("dashboard/add-medicine/", views.add_medicine, name="add_medicine"),

]
