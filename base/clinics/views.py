from django.shortcuts import render


def clinic_list(request):
    return render(request, "clinics/list.html")


def clinic_detail(request, slug):
    return render(request, "clinics/detail.html", {"slug": slug})
