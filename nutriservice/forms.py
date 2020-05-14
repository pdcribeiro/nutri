from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from nutriservice.models import Client, Meal, Plan


MealsBaseFormSet = inlineformset_factory(Client, Meal, fields='__all__', extra=6, can_delete=False, max_num=6)

class MealsFormSet(MealsBaseFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add meal name labels.
        MEAL_NAMES = [
            'P.A.',
            'Manhã',
            'Almoço',
            'Tarde',
            'Jantar',
            'Ceia',
        ]
        for form, meal_name in zip(self, MEAL_NAMES):
            form.meal_name = meal_name

            # Save empty fields as well when creating object.
            if self.instance.id is None:
                form.has_changed = lambda: True


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'born']

    def __init__(self, *args, data=None, instance=None, **kwargs):
        super().__init__(*args, data=data, instance=instance, **kwargs)
        self.meals_formset = MealsFormSet(data=data, instance=instance)
    
    def is_valid(self):
        return super().is_valid() and self.meals_formset.is_valid()

    def save(self, *args, **kwargs):
        self.meals_formset.instance = super().save(*args, **kwargs)
        self.meals_formset.save(*args, **kwargs)
        return self.instance


class PlanForm(ModelForm):
    class Meta:
        model = Plan
        exclude = ['client', 'meeting']
