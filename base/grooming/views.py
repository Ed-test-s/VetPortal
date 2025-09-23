from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import GroomingCenter


def grooming_list(request):
    return render(request, "grooming/list.html")


def grooming_detail(request, slug):
    return render(request, "grooming/detail.html", {"slug": slug})


User = get_user_model()

@login_required
def my_grooming(request):
    owner_field_model = GroomingCenter._meta.get_field("owner").remote_field.model

    owners = []
    if owner_field_model == User:
        owners = [request.user]
    else:
        profile = getattr(request.user, "profile", None)
        if profile:
            owners = [profile]

    center = GroomingCenter.objects.filter(owner__in=owners).first() if owners else None

    if center:
        return redirect("grooming_detail", slug=center.slug)
    return render(request, "grooming/my_grooming_not_found.html", status=200)
