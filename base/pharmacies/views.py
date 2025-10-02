from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Pharmacy, PharmacyMedicine


def pharmacy_list(request):
    pharmacies = Pharmacy.objects.filter(is_active=True).order_by("name")
    return render(request, "pharmacies/list.html", {"pharmacies": pharmacies})



def pharmacy_detail(request, slug):
    pharmacy = get_object_or_404(Pharmacy, slug=slug, is_active=True)
    medicines = PharmacyMedicine.objects.filter(pharmacy=pharmacy, in_stock=True).select_related("medicine")
    return render(request, "pharmacies/detail.html", {
        "pharmacy": pharmacy,
        "medicines": medicines,
    })



User = get_user_model()

@login_required
def my_pharmacy(request):
    owner_field_model = Pharmacy._meta.get_field("owner").remote_field.model

    owners = []
    if owner_field_model == User:
        owners = [request.user]
    else:
        profile = getattr(request.user, "profile", None)
        if profile:
            owners = [profile]

    pharmacy = Pharmacy.objects.filter(owner__in=owners).first() if owners else None

    if pharmacy:
        return redirect("pharmacy_detail", slug=pharmacy.slug)
    return render(request, "pharmacies/my_pharmacy_not_found.html", status=200)
