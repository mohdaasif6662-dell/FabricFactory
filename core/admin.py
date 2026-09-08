from django.contrib import admin

from .models import FabricRoll, FabricUsage


@admin.register(FabricRoll)
class FabricRollAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'color',
        'category',
        'total_rolls',
        'total_used_rolls',
        'available_rolls',
        'received_date',
        'created_by',
    )

    list_filter = (
        'category',
        'color',
        'received_date',
    )

    search_fields = (
        'color',
        'category',
    )

    ordering = (
        '-received_date',
    )


@admin.register(FabricUsage)
class FabricUsageAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'fabric',
        'used_rolls',
        'usage_date',
        'note',
        'created_by',
    )

    list_filter = (
        'usage_date',
    )

    search_fields = (
        'fabric__color',
        'fabric__category',
        'note',
    )

    ordering = (
        '-usage_date',
    )
    