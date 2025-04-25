from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import TaskManagerUser, Organization, AuthToken
from accounts.forms import (
    CustomUserCreationForm,
    TaskManagerUserUpdateForm,
)  # Updated imports

# for admin site visit on "127.0.0.1:8000/tm-admin-portal/"

class TaskManagerUserAdmin(UserAdmin):
    list_display = (
        "id",
        "email",
        "username",
        "organization",
        "is_superuser",
        "is_staff",
        "is_active",
    )

    # Use the correct forms:
    form = TaskManagerUserUpdateForm  # For editing existing users
    add_form = CustomUserCreationForm  # For adding new users

    # Fieldsets for editing users
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Organization", {"fields": ("organization",)}),
    )

    # Fieldsets for adding users
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "organization",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    search_fields = ("username", "email", "organization__name")
    list_filter = ("is_active", "is_staff", "is_superuser", "organization")


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class AuthTokeAdmin(admin.ModelAdmin):
    list_display = ("user", "token")


admin.site.register(TaskManagerUser, TaskManagerUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(AuthToken, AuthTokeAdmin)
