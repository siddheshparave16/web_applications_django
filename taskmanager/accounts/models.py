from django.db import models
from django import forms
from django.contrib.auth.models import BaseUserManager, AbstractUser
import uuid


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, organization, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        if not organization:
            raise ValueError("The Organization field is required.")

        email = self.normalize_email(email)

        user = self.model(
            username=username, email=email, organization=organization, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username, email, organization, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not organization:
            raise ValueError("Superuser must have an organization specified.")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, organization, password, **extra_fields)


class TaskManagerUser(AbstractUser):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    # Required to make username non-unique at database level
    # while still maintaining organization-scoped uniqueness
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "organization"]

    objects = CustomUserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "username"],
                name="unique_username_per_organization",
            ),
            models.UniqueConstraint(
                fields=["organization", "email"], name="unique_email_per_organization"
            ),
        ]

    def __str__(self):
        return self.username or self.email or f"User {self.id}"


class AuthToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(TaskManagerUser, on_delete=models.CASCADE, editable=False)
