from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("success/<int:order_id>/", views.order_success, name="order_success"),

    path("history/", views.order_history, name="order_history"),
    path("history/<int:order_id>/", views.order_detail, name="order_detail"),
    path("history/<int:order_id>/change-status/", views.change_order_status_user, name="order_change_status_user"),
    path("history/<int:order_id>/receipt/", views.download_receipt, name="download_receipt"),
    path("history/<int:order_id>/receipt/<str:receipt_type>/", views.download_receipt, name="download_receipt_type"),
    path("history/<int:order_id>/receipt/<str:receipt_type>/<int:pharmacy_id>/", views.download_receipt, name="download_receipt_pharmacy"),

    path("cart/add/<int:pharmacy_medicine_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:item_id>/", views.update_cart_item, name="update_cart_item"),

    path("favorites/", views.favorites_view, name="favorites"),
    path("favorites/toggle/<int:medicine_id>/", views.toggle_favorite, name="toggle_favorite"),
]
