from django.shortcuts import render
from .models import Medicine


def home(request):
    # получение последних 6 лекарств
    latest_medicines = Medicine.objects.order_by('-id')[:6]

    context = {
        "latest_medicines": latest_medicines
    }
    return render(request, "medicines/home.html", context)


def medicine_list(request):
    return render(request, "medicines/list.html")


def medicine_detail(request, slug):
    return render(request, "medicines/detail.html", {"slug": slug})
