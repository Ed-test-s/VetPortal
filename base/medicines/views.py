from django.shortcuts import render


def medicine_list(request):
    return render(request, "medicines/list.html")


def medicine_detail(request, slug):
    return render(request, "medicines/detail.html", {"slug": slug})
