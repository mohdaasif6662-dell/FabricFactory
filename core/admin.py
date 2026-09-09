from django.contrib import admin
from .models import Category, FabricRoll, FabricUsage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(FabricRoll)
class FabricRollAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'color',
        'display_categories',
        'total_rolls',
        'total_used_rolls',
        'available_rolls',
        'received_date',
        'created_by',
    )

    list_filter = (
        'categories',
        'color',
        'received_date',
    )

    search_fields = (
        'color',
        'categories__name',
    )

    filter_horizontal = ('categories',)

    ordering = ('-received_date',)

    @admin.display(description='Categories')
    def display_categories(self, obj):
        return ", ".join(
            category.name
            for category in obj.categories.all()
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

    list_filter = ('usage_date',)

    search_fields = (
        'fabric__color',
        'fabric__categories__name',
        'note',
    )

    ordering = ('-usage_date',)