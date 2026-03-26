from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("bio",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("email", "bio")}),)
