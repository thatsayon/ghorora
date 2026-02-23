from django.contrib import admin

from .models import OTP, UserAccount


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "full_name", "auth_provider", "is_active", "is_banned", "date_joined"]
    search_fields = ["email", "username", "full_name"]
    list_filter = ["is_active", "is_banned", "auth_provider", "gender"]
    readonly_fields = ["id", "date_joined", "created_at", "updated_at"]


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "is_valid"]
    search_fields = ["user__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
