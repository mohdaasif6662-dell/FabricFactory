from django import forms
from django.db.models import Sum

from .models import FabricRoll, FabricUsage


class FabricRollForm(forms.ModelForm):

    class Meta:
        model = FabricRoll

        fields = [
            'color',
            'categories',
            'total_rolls',
            'received_date',
        ]

        widgets = {
            'color': forms.TextInput(
                attrs={
                    'placeholder': 'Enter fabric color'
                }
            ),

            # Multiple categories ke liye checkboxes
            'categories': forms.CheckboxSelectMultiple(),

            'total_rolls': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter number of rolls',
                    'min': 1
                }
            ),

            'received_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        total_rolls = cleaned_data.get('total_rolls')

        # Edit case only
        if (
            self.instance
            and self.instance.pk
            and total_rolls is not None
        ):
            # Existing usage records ka total
            total_used = FabricUsage.objects.filter(
                fabric_id=self.instance.pk
            ).aggregate(
                total=Sum('used_rolls')
            )['total'] or 0

            # New total existing used rolls se kam nahi ho sakta
            if total_rolls < total_used:
                self.add_error(
                    'total_rolls',
                    f'Total rolls cannot be less than already used rolls ({total_used}).'
                )

        return cleaned_data


class FabricUsageForm(forms.ModelForm):

    class Meta:
        model = FabricUsage

        fields = [
            'fabric',
            'used_rolls',
            'usage_date',
            'note',
        ]

        widgets = {
            'used_rolls': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter used rolls',
                    'min': 1
                }
            ),

            'usage_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'note': forms.Textarea(
                attrs={
                    'placeholder': 'Optional note',
                    'rows': 3
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        fabric = cleaned_data.get('fabric')
        used_rolls = cleaned_data.get('used_rolls')

        if fabric and used_rolls is not None:

            # Current record ko exclude karke
            # baaki usage calculate karo
            total_used = FabricUsage.objects.filter(
                fabric=fabric
            ).exclude(
                pk=self.instance.pk
            ).aggregate(
                total=Sum('used_rolls')
            )['total'] or 0

            available_rolls = fabric.total_rolls - total_used

            if used_rolls > available_rolls:
                self.add_error(
                    'used_rolls',
                    f'Only {available_rolls} rolls are available.'
                )

        return cleaned_data