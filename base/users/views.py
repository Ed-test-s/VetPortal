from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import EmailOrPhoneAuthenticationForm

from .forms import CustomUserCreationForm

from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash

from .forms import ProfileUpdateForm, CustomPasswordChangeForm
from django.contrib import messages

from django.http import JsonResponse
import json



def login_view(request):
    if request.method == "POST":
        form = EmailOrPhoneAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = EmailOrPhoneAuthenticationForm()
    return render(request, "users/login.html", {"form": form})



def logout_view(request):
    logout(request)
    return redirect("home")


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # сразу авторизация после регистрации
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})




@login_required
def profile_view(request):
    user_profile = request.user.profile
    form = ProfileUpdateForm(request.POST or None, instance=user_profile, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save(request.user)
        messages.success(request, "Данные обновлены!")
        return redirect("profile")

    return render(request, "users/profile.html", {"form": form})



@login_required
def delete_account_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "download":
            data = {
                "username": request.user.username,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": str(request.user.profile.phone) if request.user.profile.phone else None,
                "role": request.user.profile.get_role_display(),
            }
            response = HttpResponse(json.dumps(data, ensure_ascii=False, indent=4), content_type="application/json")
            response["Content-Disposition"] = f'attachment; filename="{request.user.username}_backup.json"'
            return response

        elif action == "delete":
            username = request.user.username
            request.user.delete()
            logout(request)
            messages.success(request, f"Аккаунт {username} удалён ❌")
            return redirect("home")

    return render(request, "users/delete_account.html")



@login_required
def change_password_view(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # обновляем сессию, чтобы не разлогинило
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно изменён ✅")
            return redirect("change_password")
        else:
            messages.error(request, "Исправьте ошибки в форме ⚠️")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, "users/change_password.html", {"form": form})



@login_required
def download_json(request):
    profile = request.user.profile
    data = {
        "username": request.user.username,
        "email": request.user.email,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "phone": profile.phone,
        "address": profile.address,
    }

    response = JsonResponse({"status": "ok", "filename": "user_data.json", "data": data})
    return response


@login_required
def download_json_view(request):
    data = {
        "username": request.user.username,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
        "phone": str(request.user.profile.phone) if request.user.profile.phone else None,
        "role": request.user.profile.get_role_display(),
    }
    return JsonResponse({
        "status": "ok",
        "filename": f"{request.user.username}_backup.json",
        "data": data
    })

