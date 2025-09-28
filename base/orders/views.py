from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from medicines.models import Medicine
from pharmacies.models import PharmacyMedicine
from .models import CartItem, Favorite, Cart

from django.views.decorators.http import require_POST


@login_required
def checkout_view(request):
    return render(request, "orders/checkout.html")


@login_required
def order_success(request):
    return render(request, "orders/success.html")


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



@require_POST
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.profile.cart)
    item.delete()
    return JsonResponse({"status": "ok", "in_cart": False})



@login_required
def cart_view(request):
    # получаем корзину или создаём на лету (если по каким-то причинам нет)
    cart = getattr(request.user.profile, "cart", None)
    if cart is None:
        cart = Cart.objects.create(user=request.user.profile)

    # все элементы корзины (мы используем их и отдельно сгруппированные по аптекам)
    items = cart.items.select_related("pharmacy_medicine__medicine", "pharmacy_medicine__pharmacy").all()

    # сгруппировать по аптекам — передаём .items() чтобы безопасно итерировать в шаблоне
    groups = cart.grouped_by_pharmacy()
    groups_items = list(groups.items())  # [(pharmacy, [items]), ...]

    return render(request, "orders/cart.html", {
        "cart": cart,
        "items": items,
        "groups": groups_items,
    })



@require_POST
@login_required
def update_cart_item(request, item_id):
    """
    AJAX: плюс/минус количество. Ожидает POST с параметром 'action' == 'plus' или 'minus'
    Возвращает json с новым количеством и суммой позиции.
    """
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.profile.cart)
    action = request.POST.get("action")

    if action == "plus":
        item.quantity += 1
        item.save()
    elif action == "minus":
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            # нельзя уменьшить ниже 1 — можно удалить, если нужно
            pass

    return JsonResponse({
        "status": "ok",
        "item_id": item.id,
        "quantity": item.quantity,
        "total": float(item.total_price()),
    })


# --- ИЗБРАННОЕ ---
@login_required
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
def toggle_favorite(request, medicine_id):
    medicine = Medicine.objects.get(id=medicine_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user.profile, medicine=medicine)
    if not created:
        favorite.delete()
        return JsonResponse({"status": "removed"})
    return JsonResponse({"status": "added"})




