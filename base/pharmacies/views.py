from django.shortcuts import render


def pharmacy_list(request):
    return render(request, "pharmacies/list.html")


def pharmacy_detail(request, slug):
    return render(request, "pharmacies/detail.html", {"slug": slug})
