from django import forms
from .models import Review, ReviewImage


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        widgets = {
            "rating": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


# Кастомный виджет для multiple upload
class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class ReviewImageForm(forms.ModelForm):
    class Meta:
        model = ReviewImage
        fields = ["image"]
        widgets = {
            "image": MultiFileInput(attrs={"class": "form-control", "multiple": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False

