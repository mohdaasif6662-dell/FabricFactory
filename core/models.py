from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class FabricRoll(models.Model):

    color = models.CharField(max_length=100)

    categories = models.ManyToManyField(
        Category,
        related_name='fabric_rolls',
        blank=True
    )

    total_rolls = models.PositiveIntegerField()

    received_date = models.DateField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='fabric_rolls'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.color} - {self.total_rolls} Rolls"

    @property
    def total_used_rolls(self):
        return sum(
            usage.used_rolls
            for usage in self.usages.all()
        )

    @property
    def available_rolls(self):
        return self.total_rolls - self.total_used_rolls


class FabricUsage(models.Model):

    fabric = models.ForeignKey(
        FabricRoll,
        on_delete=models.CASCADE,
        related_name='usages'
    )

    used_rolls = models.PositiveIntegerField()

    usage_date = models.DateField()

    note = models.TextField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='fabric_usages'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fabric.color} - {self.used_rolls} Used"