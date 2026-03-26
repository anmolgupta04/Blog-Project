from django.urls import path

from .views import CustomLoginView, CustomLogoutView, SignUpView

urlpatterns = [
    path("register/", SignUpView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
]
