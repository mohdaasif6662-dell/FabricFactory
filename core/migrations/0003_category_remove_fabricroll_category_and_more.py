from django.db import migrations, models


def migrate_categories(apps, schema_editor):
    Category = apps.get_model('core', 'Category')
    FabricRoll = apps.get_model('core', 'FabricRoll')

    # Existing category choices
    category_names = {
        'COTTON': 'Cotton',
        'POLYESTER': 'Polyester',
        'COTTON_BLEND': 'Cotton Blend',
        'DENIM': 'Denim',
        'LINEN': 'Linen',
        'RAYON': 'Rayon',
        'WOOL': 'Wool',
        'OTHER': 'Other',
    }

    # Categories create karo
    categories = {}

    for code, name in category_names.items():
        category, created = Category.objects.get_or_create(
            name=name
        )
        categories[code] = category

    # Existing FabricRoll ki old category ko
    # new ManyToMany category me transfer karo
    for fabric in FabricRoll.objects.all():
        old_category = fabric.category

        if old_category in categories:
            fabric.categories.add(categories[old_category])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_fabricroll_category'),
    ]

    operations = [
        # 1. Category table create karo
        migrations.CreateModel(
            name='Category',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'name',
                    models.CharField(
                        max_length=50,
                        unique=True
                    )
                ),
            ],
        ),

        # 2. New ManyToMany field create karo
        migrations.AddField(
            model_name='fabricroll',
            name='categories',
            field=models.ManyToManyField(
                blank=True,
                related_name='fabric_rolls',
                to='core.category'
            ),
        ),

        # 3. Old category data ko new categories me transfer karo
        migrations.RunPython(
            migrate_categories,
            migrations.RunPython.noop
        ),

        # 4. Old category field remove karo
        migrations.RemoveField(
            model_name='fabricroll',
            name='category',
        ),
    ]