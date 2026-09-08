from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('COMPANY_ADMIN', 'Company Admin'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='COMPANY_ADMIN'
    )

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.username