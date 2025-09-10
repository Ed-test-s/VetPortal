from django.shortcuts import render


def cart_view(request):
    return render(request, "orders/cart.html")


def checkout_view(request):
    return render(request, "orders/checkout.html")


def order_success(request):
    return render(request, "orders/success.html")
