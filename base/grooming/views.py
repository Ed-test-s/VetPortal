from django.shortcuts import render


def grooming_list(request):
    return render(request, "grooming/list.html")


def grooming_detail(request, slug):
    return render(request, "grooming/detail.html", {"slug": slug})
