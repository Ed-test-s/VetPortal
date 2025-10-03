from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from medicines.models import Medicine
from pharmacies.models import PharmacyMedicine
from .models import CartItem, Favorite, Cart

from django.views.decorators.http import require_POST

from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem, OrderPickup
import random, string
from django.urls import reverse

import base64
from io import BytesIO

try:
    import qrcode
except Exception:
    qrcode = None


# --- КОРЗИНА ---
@login_required
@login_required
def add_to_cart(request, pharmacy_medicine_id):
    pm = get_object_or_404(PharmacyMedicine, id=pharmacy_medicine_id)

    # корзина пользователя
    cart, _ = getattr(request.user.profile, "cart", None), None
    if not cart:
        from .models import Cart
        cart = Cart.objects.create(user=request.user.profile)

    # пытаемся добавить в корзину
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        pharmacy_medicine=pm,
        defaults={"quantity": 1}
    )

    if not created:
        # проверяем, чтобы не превысить stock_qty
        if item.quantity + 1 > pm.stock_qty:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": "Недостаточно товара в аптеке"})
            return redirect("cart")
        item.quantity += 1
        item.save()
    else:
        # новый item → сразу проверим stock_qty
        if item.quantity > pm.stock_qty:
            item.quantity = pm.stock_qty
            item.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "ok", "in_cart": True})
    return redirect("cart")



@require_POST
@login_required
def update_cart_item(request, item_id):
    """
    AJAX: плюс/минус количество. Ожидает POST с параметром 'action' == 'plus' или 'minus'
    Возвращает json с новым количеством и суммой позиции.
    """
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.profile.cart)
    pm = item.pharmacy_medicine
    action = request.POST.get("action")

    if action == "plus":
        if item.quantity + 1 > pm.stock_qty:
            return JsonResponse({"status": "error", "message": "Недостаточно товара в аптеке"})
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



# ВСЁ ЧТО СВЯЗАНО С ПЕРЕХОДОМ К ОФОРМЛЕНИЮ ЗАКАЗА


def generate_pickup_code(length=6):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_qr_data_uri(text):
    """
    Возвращает data-uri PNG с QR (если qrcode установлен), иначе None.
    """
    if qrcode is None:
        return None
    img = qrcode.make(text)
    buf = BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"



@transaction.atomic
@login_required
def checkout_view(request):
    """
    GET: показывает форму оформления — если переданы ?selected_items=1&selected_items=2,
         показывает только эти item'ы; иначе — всю корзину.
    POST: подтверждение заказа — ожидает selected_items[] в POST (хотя если нет — возьмёт все).
    """
    # корзина для текущего пользователя (UserProfile -> cart)
    cart = getattr(request.user.profile, "cart", None)
    if cart is None or cart.items.count() == 0:
        messages.error(request, "Ваша корзина пуста.")
        return redirect("cart")

    if request.method == "GET":
        selected_ids = request.GET.getlist("selected_items")
        if selected_ids:
            items_qs = cart.items.filter(id__in=selected_ids).select_related(
                "pharmacy_medicine__medicine", "pharmacy_medicine__pharmacy"
            )
        else:
            items_qs = cart.items.select_related(
                "pharmacy_medicine__medicine", "pharmacy_medicine__pharmacy"
            ).all()

        items = list(items_qs)
        total = sum(i.total_price() for i in items)

        initial = {
            "full_name": request.user.get_full_name() or "",
            "phone": str(request.user.profile.phone) if getattr(request.user, "profile", None) and request.user.profile.phone else "",
            "email": request.user.email or "",
        }

        return render(request, "orders/checkout.html", {
            "cart": cart,
            "items": items,
            "total": total,
            "initial": initial,
            "selected_ids": selected_ids,
        })

    # POST -> создаём заказ
    if request.method == "POST":
        selected_ids = request.POST.getlist("selected_items")
        if selected_ids:
            items_qs = cart.items.filter(id__in=selected_ids).select_related(
                "pharmacy_medicine__medicine", "pharmacy_medicine__pharmacy"
            )
        else:
            items_qs = cart.items.select_related(
                "pharmacy_medicine__medicine", "pharmacy_medicine__pharmacy"
            ).all()

        if not items_qs.exists():
            messages.error(request, "Не выбрано ни одной позиции для оформления.")
            return redirect("cart")

        # получаем данные клиента
        delivery = request.POST.get("delivery") or Order.DELIVERY_PICKUP
        payment = request.POST.get("payment") or Order.PAYMENT_CASH
        full_name = (request.POST.get("full_name") or request.user.get_full_name() or request.user.username).strip()
        phone = (request.POST.get("phone") or (str(request.user.profile.phone) if getattr(request.user, "profile", None) else "")).strip()
        email = (request.POST.get("email") or request.user.email or "").strip()
        address = request.POST.get("address").strip() if delivery == Order.DELIVERY_COURIER else ""

        # транзакция на всё оформление
        with transaction.atomic():
            # проверка остатков
            for item in items_qs:
                pm = item.pharmacy_medicine
                if item.quantity > pm.stock_qty:
                    messages.error(request, f"Недостаточно '{pm.medicine.name}' в аптеке {pm.pharmacy.name}. Доступно: {pm.stock_qty}.")
                    return redirect("cart")

            # создаём заказ (user = UserProfile)
            order = Order.objects.create(
                user=request.user.profile,
                delivery_type=delivery,
                payment_method=payment,
                customer_name=full_name,
                customer_phone=phone,
                customer_email=email,
                address=address or "",
            )

            # переносим позиции и списываем со склада
            for item in items_qs:
                pm = item.pharmacy_medicine
                OrderItem.objects.create(
                    order=order,
                    pharmacy_medicine=pm,
                    quantity=item.quantity,
                )
                # уменьшить stock
                pm.stock_qty = max(pm.stock_qty - item.quantity, 0)
                pm.in_stock = pm.stock_qty > 0
                pm.save(update_fields=["stock_qty", "in_stock", "updated_at"])

            # пересчитать итог
            order.recalc_total(save=True)

            # создаём pickup-коды
            if order.delivery_type == Order.DELIVERY_PICKUP:
                pharmacies = set(item.pharmacy_medicine.pharmacy for item in cart.items.all())
                for pharmacy in pharmacies:
                    OrderPickup.objects.create(order=order, pharmacy=pharmacy)
            else:
                # courier — один код без привязки к конкретной аптеке
                OrderPickup.objects.create(order=order)

            # удаляем перенесённые позиции из корзины
            items_qs.delete()

        # редиректим на страницу успеха с id заказа
        return redirect("order_success", order_id=order.id)



@login_required
def order_success(request, order_id):
    """
    Показывает созданный заказ и соответствующие pickup-коды + QR.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user.profile)
    pickups = order.pickups.select_related("pharmacy").all()
    pickups_with_qr = []

    for p in pickups:
        if order.delivery_type == Order.DELIVERY_PICKUP and p.pharmacy:
            # ссылка на страницу аптеки
            qr_url = request.build_absolute_uri(
                reverse("pharmacy_detail", args=[p.pharmacy.slug])
            )
        else:
            # курьерская доставка → рикролл
            qr_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        pickups_with_qr.append({
            "pickup_code": p.code,
            "pharmacy": p.pharmacy,
            "qr": generate_qr_data_uri(qr_url) if qrcode else None,
        })

    # список позиций
    items = order.items.select_related("pharmacy_medicine__medicine", "pharmacy_medicine__pharmacy").all()

    return render(request, "orders/success.html", {
        "order": order,
        "pickups": pickups_with_qr,
        "items": items,
    })




@login_required
def order_history(request):
    orders = (
        Order.objects
        .filter(user=request.user.profile)
        .prefetch_related(
            "items__pharmacy_medicine__medicine",
            "items__pharmacy_medicine__pharmacy",
            "pickups__pharmacy",
        )
        .order_by("-created_at")
    )
    return render(request, "orders/order_history.html", {"orders": orders})




@login_required
def order_detail(request, order_id):
    """
    Страница подробного просмотра одного заказа.
    Доступна только владельцу заказа (user.profile).
    """
    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items__pharmacy_medicine__medicine",
            "items__pharmacy_medicine__pharmacy",
            "pickups__pharmacy",
        ),
        id=order_id,
        user=request.user.profile
    )

    return render(request, "orders/order_detail.html", {"order": order})

