from django.urls import path
from . import views


# urlpatterns = [
#     # path("", views.profile_view, name="profile"),
#     path("register/", views.register, name="register"),
#     path("login/", views.login_view, name="login"),
#     path("logout/", views.logout_view, name="logout"),
#     path("profile/", views.profile_view, name="profile"),
# ]



urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("profile/", views.profile_view, name="profile"),
    path("profile/changepassword/", views.change_password_view, name="change_password"),
    path("profile/deleteaccount/", views.delete_account_view, name="delete_account"),
]
