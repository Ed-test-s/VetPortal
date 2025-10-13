from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Pharmacy, PharmacyMedicine


from django.forms import modelform_factory, inlineformset_factory
from medicines.models import Medicine
from django.contrib import messages
from utils import generate_unique_slug

from django import forms
from .forms import PharmacyMedicineForm, PharmacyForm


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
        extra=0,  # Убираем пустую строку для добавления
        can_delete=True
    )

    if request.method == "POST":
        # Обрабатываем форму аптеки
        form = PharmacyForm(request.POST, instance=pharmacy)
        formset = PharmacyMedicineFormSet(request.POST, instance=pharmacy, form_kwargs={"pharmacy": pharmacy})
        
        if form.is_valid() and formset.is_valid():
            # Сохраняем изменения аптеки
            pharmacy_instance = form.save(commit=False)
            # Обновляем slug если изменилось название
            if pharmacy_instance.name and pharmacy_instance.name != pharmacy.name:
                pharmacy_instance.slug = generate_unique_slug(pharmacy_instance, 'slug', 'name')
            pharmacy_instance.save()
            
            # Сохраняем formset
            formset.save()
            messages.success(request, "Изменения сохранены.")
            return redirect("pharmacy_dashboard")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
            # Показываем детальные ошибки формы
            if not form.is_valid():
                messages.error(request, f"Ошибки в информации об аптеке:")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"  {field}: {error}")
            if not formset.is_valid():
                messages.error(request, f"Ошибки в разделе лекарств:")
                for i, form_errors in enumerate(formset.errors):
                    if form_errors:
                        messages.error(request, f"  Лекарство {i+1}:")
                        for field, errors in form_errors.items():
                            for error in errors:
                                messages.error(request, f"    {field}: {error}")
                # Показываем ошибки non_form_errors
                if formset.non_form_errors():
                    for error in formset.non_form_errors():
                        messages.error(request, f"  Общие ошибки: {error}")
    else:
        form = PharmacyForm(instance=pharmacy)
        formset = PharmacyMedicineFormSet(instance=pharmacy, form_kwargs={"pharmacy": pharmacy})

    return render(request, "pharmacies/dashboard.html", {
        "pharmacy": pharmacy,
        "form": form,
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
        # Поля для дополнительных изображений (до 5 штук)
        extra_image_1 = forms.ImageField(
            required=False,
            label="Дополнительное изображение 1",
            widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        )
        extra_image_2 = forms.ImageField(
            required=False,
            label="Дополнительное изображение 2",
            widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        )
        extra_image_3 = forms.ImageField(
            required=False,
            label="Дополнительное изображение 3",
            widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        )
        extra_image_4 = forms.ImageField(
            required=False,
            label="Дополнительное изображение 4",
            widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        )
        extra_image_5 = forms.ImageField(
            required=False,
            label="Дополнительное изображение 5",
            widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        )
        
        class Meta:
            model = Medicine
            fields = ["name", "category", "manufacturer", "description", "instruction", "is_prescription", "main_image"]
            widgets = {
                'name': forms.TextInput(attrs={'class': 'form-control'}),
                'category': forms.Select(attrs={'class': 'form-select'}),
                'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
                'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
                'instruction': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
                'is_prescription': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'main_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            }

    if request.method == "POST":
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            medicine = form.save()
            
            # Обрабатываем дополнительные изображения
            extra_images = [
                form.cleaned_data.get('extra_image_1'),
                form.cleaned_data.get('extra_image_2'),
                form.cleaned_data.get('extra_image_3'),
                form.cleaned_data.get('extra_image_4'),
                form.cleaned_data.get('extra_image_5'),
            ]
            
            for image in extra_images:
                if image:  # Проверяем, что файл не пустой
                    from medicines.models import PharmacyImage
                    PharmacyImage.objects.create(medicine=medicine, image=image)
            
            messages.success(request, f"Лекарство '{medicine.name}' добавлено.")
            return redirect("pharmacies:pharmacy_dashboard")
        else:
            messages.error(request, "Ошибка при добавлении лекарства.")
    else:
        form = MedicineForm()

    return render(request, "pharmacies/add_medicine.html", {"form": form})


@login_required
def add_medicine_to_pharmacy(request):
    """Добавление существующего лекарства в аптеку"""
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != profile.ROLE_PHARMACY:
        messages.error(request, "Доступ запрещён.")
        return redirect("home")

    pharmacy = Pharmacy.objects.filter(owner=profile).first()
    if not pharmacy:
        messages.error(request, "У вас пока нет зарегистрированной аптеки.")
        return redirect("home")

    class AddMedicineToPharmacyForm(forms.Form):
        medicine = forms.ModelChoiceField(
            queryset=Medicine.objects.all(),
            label="Лекарство",
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        price = forms.DecimalField(
            max_digits=10, 
            decimal_places=2,
            label="Цена",
            widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        )
        stock_qty = forms.IntegerField(
            min_value=0,
            label="Количество",
            widget=forms.NumberInput(attrs={'class': 'form-control'})
        )
        in_stock = forms.BooleanField(
            label="В наличии",
            required=False,
            initial=True,
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
        )
        
        def __init__(self, *args, **kwargs):
            pharmacy = kwargs.pop('pharmacy', None)
            super().__init__(*args, **kwargs)
            
            if pharmacy:
                # Исключаем лекарства, которые уже есть в этой аптеке
                existing_medicines = pharmacy.pharmacy_medicines.values_list('medicine_id', flat=True)
                self.fields['medicine'].queryset = Medicine.objects.exclude(id__in=existing_medicines)

    if request.method == "POST":
        form = AddMedicineToPharmacyForm(request.POST, pharmacy=pharmacy)
        if form.is_valid():
            medicine = form.cleaned_data['medicine']
            price = form.cleaned_data['price']
            stock_qty = form.cleaned_data['stock_qty']
            in_stock = form.cleaned_data['in_stock']
            
            # Проверяем, не добавлено ли уже это лекарство
            if PharmacyMedicine.objects.filter(pharmacy=pharmacy, medicine=medicine).exists():
                messages.error(request, f"Лекарство '{medicine.name}' уже есть в вашей аптеке.")
            else:
                PharmacyMedicine.objects.create(
                    pharmacy=pharmacy,
                    medicine=medicine,
                    price=price,
                    stock_qty=stock_qty,
                    in_stock=in_stock
                )
                messages.success(request, f"Лекарство '{medicine.name}' добавлено в аптеку.")
                return redirect("pharmacy_dashboard")
    else:
        form = AddMedicineToPharmacyForm(pharmacy=pharmacy)

    return render(request, "pharmacies/add_medicine_to_pharmacy.html", {"form": form})
