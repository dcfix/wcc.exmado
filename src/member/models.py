from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class CustomUser(AbstractUser):
    """We'll be able to add custom user data at a later point, such as allowing members to login."""

    def __str__(self):
        return self.username

    class Meta:
        # …
        permissions = (("is_kiosk_user", "Kiosk mode only."),
                       )