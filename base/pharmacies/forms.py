from django import forms
from django.forms import inlineformset_factory
from .models import Pharmacy, PharmacyMedicine
from medicines.models import Medicine


class PharmacyMedicineForm(forms.ModelForm):
    class Meta:
        model = PharmacyMedicine
        fields = ("medicine", "price", "stock_qty", "in_stock")

    def __init__(self, *args, **kwargs):
        pharmacy = kwargs.pop("pharmacy", None)  # ← получаем аптеку из view
        super().__init__(*args, **kwargs)

        # Если аптека передана — фильтруем список лекарств
        if pharmacy:
            used_medicines = pharmacy.pharmacy_medicines.values_list("medicine_id", flat=True)
            # Можно показывать только те, что уже есть:
            self.fields["medicine"].queryset = Medicine.objects.filter(id__in=used_medicines)
            # Или, если хочешь добавить новые — наоборот:
            # self.fields["medicine"].queryset = Medicine.objects.exclude(id__in=used_medicines)
        else:
            # fallback — все лекарства
            self.fields["medicine"].queryset = Medicine.objects.all()


PharmacyMedicineFormSet = inlineformset_factory(
    Pharmacy,
    PharmacyMedicine,
    form=PharmacyMedicineForm,  # ← используем кастомную форму
    fields=("medicine", "price", "stock_qty", "in_stock"),
    extra=1,
    can_delete=True
)
