from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from medicines.models import Medicine
from pharmacies.models import PharmacyMedicine
from .models import CartItem, Favorite


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
# def favorites_view(request):
#     favorites = [fav.medicine for fav in Favorite.objects.filter(user=request.user.profile)]
#     return render(request, "orders/favorites.html", {"favorites": favorites})

def favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user.profile).select_related("medicine")
    medicines = []

    for fav in favorites:
        medicine = fav.medicine
        # добавляем флаг прямо в объект (динамическое свойство)
        medicine.is_favorite = True
        medicines.append(medicine)

    return render(request, "orders/favorites.html", {"favorites": medicines})



@login_required
def order_history(request):
    orders = request.user.profile.orders.select_related("pharmacy").prefetch_related("items__pharmacy_medicine__medicine")
    return render(request, "orders/order_history.html", {"orders": orders})




# --- КОРЗИНА ---

@login_required
def add_to_cart(request, pharmacy_medicine_id):
    pm = get_object_or_404(PharmacyMedicine, id=pharmacy_medicine_id)
    cart, _ = request.user.profile.cart, None
    if not hasattr(request.user.profile, "cart"):
        from .models import Cart
        cart = Cart.objects.create(user=request.user.profile)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        pharmacy_medicine=pm,
        defaults={"quantity": 1}
    )
    if not created:
        item.quantity += 1
        item.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "ok", "in_cart": True})
    return redirect("cart")


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.profile.cart)
    item.delete()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "ok", "in_cart": False})
    return redirect("cart")


@login_required
def cart_view(request):
    cart = getattr(request.user.profile, "cart", None)
    items = cart.items.select_related("pharmacy_medicine__medicine") if cart else []
    return render(request, "orders/cart.html", {"items": items})


# --- ИЗБРАННОЕ ---

@login_required
def toggle_favorite(request, medicine_id):
    medicine = Medicine.objects.get(id=medicine_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user.profile, medicine=medicine)
    if not created:
        favorite.delete()
        return JsonResponse({"status": "removed"})
    return JsonResponse({"status": "added"})

