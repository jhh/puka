from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:  # ty: ignore[invalid-attribute-override]
        model = CustomUser
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    class Meta:  # ty: ignore[invalid-attribute-override]
        model = CustomUser
        fields = ("username", "email")
