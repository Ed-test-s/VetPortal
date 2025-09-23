from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Clinic


def clinic_list(request):
    return render(request, "clinics/list.html")


def clinic_detail(request, slug):
    return render(request, "clinics/detail.html", {"slug": slug})


User = get_user_model()

@login_required
def my_clinic(request):
    """
    Попытка найти клинику, привязанную к текущему пользователю.
    Поведение:
    - если найдена -> редирект на страницу detail (name='clinic_detail', slug=...)
    - если не найдена -> показываем простую страницу с подсказкой
    """
    owner_field_model = Clinic._meta.get_field("owner").remote_field.model

    owners = []
    # если owner FK ссылается на User
    if owner_field_model == User:
        owners = [request.user]
    else:
        # предполагаем, что owner ссылается на UserProfile
        profile = getattr(request.user, "profile", None)
        if profile:
            owners = [profile]

    clinic = Clinic.objects.filter(owner__in=owners).first() if owners else None

    if clinic:
        return redirect("clinic_detail", slug=clinic.slug)
    # если клиника не найдена — можно предлагать создать в админке / показывать информ. страницу
    return render(request, "clinics/my_clinic_not_found.html", status=200)
