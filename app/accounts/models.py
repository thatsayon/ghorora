import hashlib
from datetime import timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from cloudinary.models import CloudinaryField

from app.common.enums import AuthProviderChoices, GenderChoices
from app.common.models import BaseModel


class CustomAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The email must be set"))

        extra_fields.setdefault("is_active", True)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class UserAccount(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), max_length=30, unique=True)

    full_name = models.CharField(_("full name"), max_length=50)
    profile_pic = CloudinaryField(blank=True, null=True)

    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        blank=True,
        null=True,
    )

    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProviderChoices.choices,
        default=AuthProviderChoices.EMAIL,
    )

    google_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_banned = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomAccountManager()

    def __str__(self):
        return self.email


class OTP(BaseModel):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="otps")
    otp = models.CharField(max_length=64)  # stores SHA-256 hex digest

    def set_otp(self, raw_otp: str):
        """Hash and store the OTP."""
        self.otp = hashlib.sha256(raw_otp.encode()).hexdigest()

    def check_otp(self, raw_otp: str) -> bool:
        """Check a raw OTP against the stored hash."""
        return self.otp == hashlib.sha256(raw_otp.encode()).hexdigest()

    def is_valid(self, expiry_minutes: int = 5) -> bool:
        """Check if the OTP is still within its validity window."""
        expiry_time = self.created_at + timedelta(minutes=expiry_minutes)
        return timezone.now() <= expiry_time

    def __str__(self):
        return f"{self.user.email} - OTP"
