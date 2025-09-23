from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Pharmacy


def pharmacy_list(request):
    return render(request, "pharmacies/list.html")


def pharmacy_detail(request, slug):
    return render(request, "pharmacies/detail.html", {"slug": slug})


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
