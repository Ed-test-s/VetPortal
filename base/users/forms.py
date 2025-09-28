from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UserProfile
import re
from django.core.exceptions import ValidationError

from django.contrib.auth.forms import PasswordChangeForm



# === Авторизация (по email / телефону / логину) ===
class EmailOrPhoneAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Email или телефон или логин",
        widget=forms.TextInput(attrs={
            "autofocus": True,
            "class": "form-control",
            "placeholder": "Введите email, телефон или логин"
        })
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Введите пароль"
        }),
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            # Проверка email
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                # Проверка телефона
                try:
                    user_obj = User.objects.get(profile__phone=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    pass  # логинимся по username напрямую

            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError("Неверные данные для входа")

        return self.cleaned_data


# === Регистрация пользователя ===
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Придумайте логин"
        })
    )
    email = forms.EmailField(
        required=True,
        label="Почта",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Введите почту"
        })
    )
    first_name = forms.CharField(
        required=True,
        label="Имя",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите имя"
        })
    )
    last_name = forms.CharField(
        required=True,
        label="Фамилия",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите фамилию"
        })
    )
    phone = forms.CharField(
        required=True,
        label="Телефон",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите номер телефона"
        })
    )
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Введите пароль"
        }),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Повторите пароль"
        }),
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "phone", "password1", "password2")

    # === ВАЛИДАЦИЯ ===
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        pattern = r"^(\+375|80)(25|29|33|44)\d{7}$"
        if not re.match(pattern, phone):
            raise ValidationError("Введите корректный номер: +375(25|29|33|44)XXXXXXX или 80XXXXXXXXX.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с такой почтой уже зарегистрирован.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"\d", password):
            raise ValidationError("Пароль должен содержать минимум 8 символов, хотя бы 1 заглавную букву и цифру.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
            # создание профиля
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data["phone"],
                role=UserProfile.ROLE_CLIENT  # по умолчанию обычный пользователь
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label="Имя", required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label="Фамилия", required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label="Почта", required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = UserProfile
        fields = ["phone"]

        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

    def save(self, user, commit=True):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            super().save(commit=True)
        return user


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Старый пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

