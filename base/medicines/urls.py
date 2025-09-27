from django.urls import path
from . import views

urlpatterns = [
    path("", views.medicine_list, name="medicine_list"),
    path("<slug:slug>/", views.medicine_detail, name="medicine_detail"),
    path("<slug:slug>/reviews/", views.medicine_reviews, name="medicine_reviews"),

    path("<slug:slug>/reviews/add/", views.add_review, name="add_review"),
    path("<slug:slug>/reviews/<int:review_id>/", views.review_detail, name="review_detail"),
]
