# from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from nutriservice.models import Client, Meal


MealsBaseFormSet = inlineformset_factory(Client, Meal, fields='__all__', extra=6, can_delete=False, max_num=6)

class MealsFormSet(MealsBaseFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        meal_names = [
            'P.A.',
            'Manhã',
            'Almoço',
            'Tarde',
            'Jantar',
            'Ceia',
        ]
        for form, meal_name in zip(self, meal_names):
            form.meal_name = meal_name


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'born']

    def __init__(self, *args, data=None, instance=None, **kwargs):
        super().__init__(*args, data=data, instance=instance, **kwargs)
        self.meals_formset = MealsFormSet(data, instance=instance)
    
    def is_valid(self):
        return super().is_valid() and self.meals_formset.is_valid()

    def save(self, *args, **kwargs):
        self.meals_formset.instance = super().save(*args, **kwargs)
        self.meals_formset.save()
        return self.meals_formset.instance
