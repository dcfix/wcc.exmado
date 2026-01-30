from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


# Provide AdminUserCreationForm compatibility for older/newer Django versions.
try:
    # Newer Django may expose AdminUserCreationForm here
    from django.contrib.auth.forms import AdminUserCreationForm  # type: ignore
except Exception:
    class AdminUserCreationForm(UserCreationForm):
        usable_password = forms.BooleanField(required=False, initial=True, label="Set usable password")

        class Meta:
            model = CustomUser
            fields = ("username", "email", "first_name", "last_name")

        def save(self, commit=True):
            user = super().save(commit=False)
            # If usable_password unchecked, mark as unusable
            if not self.cleaned_data.get('usable_password'):
                user.set_unusable_password()
            if commit:
                user.save()
            return user


class CustomUserCreationForm(AdminUserCreationForm):

    class Meta(AdminUserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name")


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name")
