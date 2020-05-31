import datetime

from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.forms.models import inlineformset_factory

from .models import Client, Meeting, Meal, Plan


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


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['user', 'nutritionist']

    def __init__(self, *args, data=None, instance=None, **kwargs):
        super().__init__(*args, data=data, instance=instance, **kwargs)
        self.meals_formset = MealsFormSet(data=data, instance=instance)
    
    def is_valid(self):
        return super().is_valid() and self.meals_formset.is_valid()

    def save(self, *args, **kwargs):
        self.meals_formset.instance = super().save(*args, **kwargs)
        self.meals_formset.save(*args, **kwargs)
        return self.instance


# class MeetingForm(forms.ModelForm):
#     class Meta:
#         model = Meeting
#         exclude = ['event']from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control mb-2',
        'placeholder': 'utilizador'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3',
        'placeholder': 'palavra-passe'}))


# def append_to_dict_item(dict_, item, appendix):
#     dict_[item] = (dict_[item] if item in dict_ else '') + appendix

# class BootstrapMixin:
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name in self.fields:
#             field = self.fields[field_name]
#             attrs = field.widget.attrs
#             if isinstance(field, forms.ChoiceField):
#                 append_to_dict_item(attrs, 'class', 'custom-select ')
#             else:
#                 append_to_dict_item(attrs, 'class', 'form-control ')


class MeetingStartForm(forms.Form):
    last_meeting_notes = forms.CharField(widget=forms.Textarea, disabled=True, label='Notas da última consulta')
    notes = forms.CharField(widget=forms.Textarea)

class MeetingMeasureForm(forms.Form):
    date = forms.DateField(
        initial=datetime.date.today, label='Data',
        widget=forms.DateInput(attrs={ 'placeholder': 'dia-mês-ano' }))
    value = forms.DecimalField(
        label='Nova medição', widget=forms.NumberInput(attrs={ 'placeholder': 'valor' }))
    unit = forms.CharField(
        label='Unidade', widget=forms.TextInput(attrs={
            # 'readonly': '',
            # 'class': 'form-control-plaintext ',
            'placeholder': 'unidade'}))
    notes = forms.CharField(widget=forms.Textarea)

class MeetingCalculateForm(forms.Form):
    pass

class MeetingPlanForm(forms.Form):
    pass

class MeetingFinishForm(forms.Form):
    notes = forms.CharField(widget=forms.Textarea)
