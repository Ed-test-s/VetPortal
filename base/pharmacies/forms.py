from django import forms
from django.forms import inlineformset_factory
from .models import Pharmacy, PharmacyMedicine
from medicines.models import Medicine
from utils import generate_unique_slug


class PharmacyForm(forms.ModelForm):
    """Форма для редактирования информации об аптеке"""
    
    class Meta:
        model = Pharmacy
        fields = ['name', 'address', 'phone', 'email', 'latitude', 'longitude', 
                 'work_days', 'open_at', 'closed_at', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'pharmacy-name'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'work_days': forms.CheckboxSelectMultiple(),
            'open_at': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closed_at': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем поле для отображения slug (не сохраняется в БД)
        self.fields['slug_preview'] = forms.CharField(
            label='URL аптеки (slug)',
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'id': 'slug-preview'
            })
        )
        
        # Если редактируем существующую аптеку, показываем текущий slug
        if self.instance and self.instance.pk:
            self.fields['slug_preview'].initial = self.instance.slug
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Генерируем новый slug на основе названия
            new_slug = generate_unique_slug(self.instance, 'slug', 'name')
            # Обновляем slug в форме для отображения
            self.fields['slug_preview'].initial = new_slug
        return name
    
    def save(self, commit=True):
        # Исключаем slug_preview из сохранения
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class PharmacyMedicineForm(forms.ModelForm):
    class Meta:
        model = PharmacyMedicine
        fields = ("medicine", "price", "stock_qty", "in_stock")

    def __init__(self, *args, **kwargs):
        pharmacy = kwargs.pop("pharmacy", None)  # ← получаем аптеку из view
        super().__init__(*args, **kwargs)

        # Показываем все лекарства для редактирования существующих записей
        self.fields["medicine"].queryset = Medicine.objects.all()


PharmacyMedicineFormSet = inlineformset_factory(
    Pharmacy,
    PharmacyMedicine,
    form=PharmacyMedicineForm,  # ← используем кастомную форму
    fields=("medicine", "price", "stock_qty", "in_stock"),
    extra=1,
    can_delete=True
)
