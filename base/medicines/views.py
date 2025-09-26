from django.shortcuts import render, get_object_or_404
from .models import Medicine
from orders.models import Favorite
from pharmacies.models import PharmacyMedicine

def home(request):
    latest_medicines = Medicine.objects.order_by('-id')[:9]

    # пометим для каждого лекарства — в избранном ли оно у текущего пользователя
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        favorite_ids = Favorite.objects.filter(user=request.user.profile).values_list("medicine_id", flat=True)
        for med in latest_medicines:
            med.is_favorite = med.id in favorite_ids
    else:
        for med in latest_medicines:
            med.is_favorite = False

    context = {
        "latest_medicines": latest_medicines
    }
    return render(request, "medicines/home.html", context)


def medicine_list(request):
    return render(request, "medicines/list.html")


def medicine_detail(request, slug):
    """
    Страница конкретного лекарства:
      - объект Medicine
      - is_favorite (для текущего пользователя)
      - список PharmacyMedicine (аптеки, цены, наличие)
    """
    medicine = get_object_or_404(Medicine, slug=slug)

    # аптеки и цены
    pharmacies = (
        PharmacyMedicine.objects
        .filter(medicine=medicine)
        .select_related("pharmacy")
    )

    # флаг избранного
    is_favorite = False
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        is_favorite = Favorite.objects.filter(
            user=request.user.profile,
            medicine=medicine
        ).exists()

    context = {
        "medicine": medicine,
        "pharmacies": pharmacies,
        "is_favorite": is_favorite,
    }
    return render(request, "medicines/detail.html", context)


def medicine_reviews(request, slug):
    return render(request, "medicines/reviews.html", {"slug": slug})

