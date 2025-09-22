from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def cart_view(request):
    return render(request, "orders/cart.html")


@login_required
def checkout_view(request):
    return render(request, "orders/checkout.html")


@login_required
def order_success(request):
    return render(request, "orders/success.html")


@login_required
def favorites_view(request):
    return render(request, "orders/favorites.html")
