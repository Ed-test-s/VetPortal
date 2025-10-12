from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Pharmacy, PharmacyMedicine


from django.forms import modelform_factory, inlineformset_factory
from medicines.models import Medicine
from django.contrib import messages
from utils import generate_unique_slug

from django import forms
from .forms import PharmacyMedicineForm


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





@login_required
def pharmacy_dashboard(request):
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != profile.ROLE_PHARMACY:
        messages.error(request, "У вас нет прав для доступа к панели аптеки.")
        return redirect("home")

    pharmacy = Pharmacy.objects.filter(owner=profile).first()
    if not pharmacy:
        messages.error(request, "У вас пока нет зарегистрированной аптеки.")
        return redirect("home")

    # Создаём formset с передачей текущей аптеки
    PharmacyMedicineFormSet = inlineformset_factory(
        Pharmacy,
        PharmacyMedicine,
        form=PharmacyMedicineForm,
        fields=("medicine", "price", "stock_qty", "in_stock"),
        extra=1,
        can_delete=True
    )

    if request.method == "POST":
        formset = PharmacyMedicineFormSet(request.POST, instance=pharmacy, form_kwargs={"pharmacy": pharmacy})
        if formset.is_valid():
            formset.save()
            messages.success(request, "Изменения сохранены.")
            return redirect("pharmacy_dashboard")
    else:
        formset = PharmacyMedicineFormSet(instance=pharmacy, form_kwargs={"pharmacy": pharmacy})

    return render(request, "pharmacies/dashboard.html", {
        "pharmacy": pharmacy,
        "formset": formset,
    })




@login_required
def add_medicine(request):
    """Добавление нового лекарства"""
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != profile.ROLE_PHARMACY:
        messages.error(request, "Доступ запрещён.")
        return redirect("home")

    class MedicineForm(forms.ModelForm):
        class Meta:
            model = Medicine
            fields = ["name", "category", "manufacturer", "description", "instruction", "is_prescription", "main_image"]

    if request.method == "POST":
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            medicine = form.save()
            messages.success(request, f"Лекарство '{medicine.name}' добавлено.")
            return redirect("pharmacies:pharmacy_dashboard")
        else:
            messages.error(request, "Ошибка при добавлении лекарства.")
    else:
        form = MedicineForm()

    return render(request, "pharmacies/add_medicine.html", {"form": form})
