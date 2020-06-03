import datetime
import json
import os

from django import forms
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic, View
from django.views.generic.edit import ModelFormMixin

from .models import Partner, Client, Measure, Measurement, Meeting, PrePlan, PAL
from .forms import ClientForm, MeetingStartForm, MeetingMeasureForm, MeetingCalculateForm, MeetingPrePlanForm, MeetingFinishForm


def get_field_value(field, obj):
    value = field.value_to_string(obj)
    if value == 'None':
        return { 'value': '' }
    if field.choices:
        get_display = getattr(obj, f'get_{field.name}_display')
        return { 'value': get_display() }
    elif field.many_to_one:
        obj = get_object_or_404(field.target_field.model, pk=value)
        if hasattr(obj, 'get_absolute_url') and callable(obj.get_absolute_url):
            return { 'href': obj.get_absolute_url(), 'value': obj }
        else:
            return { 'value': obj }
    else:
        return { 'value': value }

def filter_fields(obj, field):
    if hasattr(obj, 'fields'):
        if hasattr(obj, 'exclude'):
            raise Exception("Can't have both 'fields' and 'exclude' attributes when filtering fields.")
        else:
            return field in obj.fields
    elif hasattr(obj, 'exclude'):
        return field not in obj.exclude
    return True

def check_url_reverse(url_name, *args, **kwargs):
    try:
        reverse(url_name, *args, **kwargs)
    except:
        return False
    return True

def append_to_dict_item(dict_, item, appendix):
    dict_[item] = (dict_[item] if item in dict_ else '') + appendix

def get_param_to_dict(request, name, dict_, model=None):
    """Adds object from GET request to dict."""
    param = request.GET.get(name)
    if model:
        obj = get_object_or_404(model, pk=param) if param else None
        return add_to_dict(dict_, name, obj)
    return add_to_dict(dict_, name, param)

def add_to_dict(dict_, key, val):
    dict_[key] = val
    return dict_


class ViewMixin:
    title_prefix = ''
    title_suffix = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'title' not in context and hasattr(self, 'model'):
            context['title'] = self.title_prefix + self.model._meta.verbose_name + self.title_suffix
        context.update({ 'next': self.get_next() })
        if hasattr(self, 'context'):
            context.update(self.context)
        return context

    def get_success_url(self):
        return self.get_next()

    def get_next(self):
        return (self.request.GET.get('next')
            or hasattr(self, 'success_url') and self.success_url
            or reverse('index'))

class ListViewMixin(ViewMixin, generic.ListView):
    context_object_name = 'list'
    paginate_by = 10
    template_name = 'common/generic_list.html'
    
    def get_context_data(self, **kwargs):
        # Add default title to self.context
        if not hasattr(self, 'context'): self.context = {}
        elif 'title' not in self.context:
            self.context['title'] = self.model._meta.verbose_name_plural.capitalize()
        # Run parent method
        context = super().get_context_data(**kwargs)
        # Build list
        lst = context['list']
        context.update({
            'navbar': [],
            'cols': [field.verbose_name for field in lst[0]._meta.fields
                if filter_fields(self, field.name)] if lst else [],
            'rows': [{
                'object': obj,
                'fields': [get_field_value(field, obj) for field in obj._meta.fields
                    if filter_fields(self, field.name)],
                'color': hasattr(obj, 'get_color') and obj.get_color() or None,
            } for obj in lst],
            'buttons': [],
            'model_vbname_plural': self.model._meta.verbose_name_plural,
        })
        # Add 'add item' button to navbar
        if self.request.user.has_perm(f'service.add_{self.slug}'):
            context['navbar'].append({
                'icon': 'fas fa-plus', 'type': 'primary',
                'text': self.add_btn_str if hasattr(self, 'add_btn_str') else 'Criar',
                'href': f"{reverse(f'{self.slug}-create')}?next={self.request.path}"})
        # Add 'view' list item button
        if (self.request.user.has_perm(f'service.view_{self.slug}')
                and check_url_reverse(f'{self.slug}-detail', args=[0])):
            context['buttons'].append({ 'url': f'{self.slug }-detail', 'icon': 'file-alt'})
        # Add 'edit' list item button
        if (self.request.user.has_perm(f'service.change_{self.slug}')
                and check_url_reverse(f'{self.slug}-update', args=[0])):
            context['buttons'].append({ 'url': f'{self.slug }-update', 'icon': 'edit'})
        # Add 'delete' list item button
        if (self.request.user.has_perm(f'service.delete_{self.slug}')
                and check_url_reverse(f'{self.slug}-delete', args=[0])):
            context['buttons'].append({ 'url': f'{self.slug }-delete', 'icon': 'trash-alt'})
        return context

class DetailViewMixin(ViewMixin, generic.DetailView):
    context_object_name = 'object'
    template_name = 'common/generic_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context['object']
        context.update({
            'navbar': [],
            'fields': [{
                'name': field.verbose_name,
                **get_field_value(field, obj),
            } for field in obj._meta.fields if filter_fields(self, field.name)],
        })
        if self.request.user.has_perm(f'service.change_{self.slug}'):
            context['navbar'] += [{
                'icon': 'fas fa-edit', 'text': 'Editar', 'type': 'primary',
                'href': reverse(f'{self.slug}-update', args=[self.kwargs['pk']])}]
        if self.request.user.has_perm(f'service.delete_{self.slug}'):
            context['navbar'] += [{
                'icon': 'fas fa-trash-alt', 'text': 'Apagar', 'type': 'secondary',
                'href': reverse(f'{self.slug}-delete', args=[self.kwargs['pk']])}]
        return context

class CreateViewMixin(ViewMixin, generic.CreateView):
    template_name = 'common/generic_form.html'
    title_prefix = 'Criar '

class UpdateViewMixin(ViewMixin, generic.UpdateView):
    template_name = 'common/generic_form.html'
    title_prefix = 'Editar '

class DeleteViewMixin(ViewMixin, generic.DeleteView):
    context_object_name = 'object'
    template_name = 'common/generic_confirm_delete.html'
    title_prefix = 'Apagar '
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({ 'model_vb_name': self.model._meta.verbose_name })
        return context

class FormViewMixin:
    template_name = 'common/generic_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name in form.fields:
            field = form.fields[field_name]
            attrs = field.widget.attrs
            if isinstance(field, forms.ChoiceField):
                append_to_dict_item(attrs, 'class', 'custom-select ')
            else:
                append_to_dict_item(attrs, 'class', 'form-control ')
        return form

class GoogleApiMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'js_context': {
                'CLIENT_ID': os.environ.get('GOOGLE_CLIENT_ID'),
                'API_KEY': os.environ.get('GOOGLE_API_KEY'),
            }
        })
        return context


class Home(LoginRequiredMixin, ViewMixin, View):
    def get(self, request):
        # Generate counts of some of the main objects
        num_clients = Client.objects.all().count()
        num_meetings = Meeting.objects.all().count()
        num_preplans = PrePlan.objects.all().count()
        
        # # Number of visits to this view, as counted in the session variable.
        # num_visits = request.session.get('num_visits', 0)
        # request.session['num_visits'] = num_visits + 1

        context = {
            'title': 'Início',
            'url': 'home',
            'num_clients': num_clients,
            'num_meetings': num_meetings,
            'num_preplans': num_preplans,
            # 'num_visits': num_visits,
        }

        return render(request, 'index.html', context=context)


class PartnerList(PermissionRequiredMixin, ListViewMixin):
    permission_required = 'service.view_partner'
    model = Partner
    context = { 'url': 'partners' }
    exclude = ['id']
    slug = 'partner'
    add_btn_str = 'Novo parceiro'

class PartnerDetail(PermissionRequiredMixin, DetailViewMixin):
    permission_required = 'service.view_partner'
    model = Partner
    exclude = ['id']
    slug = 'partner'

class PartnerFormMixin(GoogleApiMixin, FormViewMixin):
    model = Partner
    fields = '__all__'
    template_name = 'service/partner_form.html'

class PartnerCreate(PermissionRequiredMixin, PartnerFormMixin, CreateViewMixin):
    permission_required = 'service.add_partner'

class PartnerUpdate(PermissionRequiredMixin, PartnerFormMixin, UpdateViewMixin):
    permission_required = 'service.change_partner'

class PartnerDelete(PermissionRequiredMixin, DeleteViewMixin):
    permission_required = 'service.delete_partner'
    model = Partner
    success_url = reverse_lazy('partners')


class ClientList(PermissionRequiredMixin, ListViewMixin):
    permission_required = 'service.view_client'
    model = Client
    context = { 'url': 'clients' }
    fields = ['name', 'gender', 'age', 'weight', 'partner']
    slug = 'client'
    add_btn_str = 'Novo cliente'

class ClientDetail(PermissionRequiredMixin, DetailViewMixin):
    permission_required = 'service.view_client'
    model = Client
    context_object_name = 'client'
    template_name = 'service/client_detail.html'
    exclude = ['id', 'user', 'nutritionist']
    slug = 'client'

class ClientFormMixin(FormViewMixin):
    model = Client
    form_class = ClientForm
    template_name = 'service/client_form.html'

class ClientCreate(PermissionRequiredMixin, ClientFormMixin, CreateViewMixin):
    permission_required = 'service.add_client'

    def form_valid(self, form):
        if self.request.user.groups.filter(name='nutritionist').exists():
            form.instance.nutritionist = self.request.user
        return super().form_valid(form)

class ClientUpdate(PermissionRequiredMixin, ClientFormMixin, UpdateViewMixin):
    permission_required = 'service.change_client'

class ClientDelete(PermissionRequiredMixin, DeleteViewMixin):
    permission_required = 'service.delete_client'
    model = Client
    success_url = reverse_lazy('clients')

@permission_required('service.add_plan')
def get_client_data(request, pk):
    client = get_object_or_404(Client, pk=pk)
    # today = datetime.date.today()
    return JsonResponse({
        'gender': client.gender,
        # 'age': today.year - client.born.year -
        #     ((today.month, today.day) <
        #     (client.born.month, client.born.day)),
        'age': client.age,
        'height': float(client.height),
        'weight': float(client.weight),
        'bodyFat': float(client.body_fat) if client.body_fat else '',
        'pal': str(client.pal),
        'palMap': { str(key): val for [key, val] in PAL },
    })

@permission_required('service.add_meeting')
def get_client_calendar(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return JsonResponse({ 'id': client.partner.calendar })

class ClientBasedCreateMixin(CreateViewMixin):
    def get_initial(self):
        return get_param_to_dict(self.request, 'client', super().get_initial(), Client)

class ClientBasedUpdateMixin(UpdateViewMixin):
    def get_initial(self):
        return add_to_dict(super().get_initial(), 'client' , self.object.client)

    def get_form(self, form_class=None):
        """Disables client field."""
        form = super().get_form(form_class)
        form.fields['client'].disabled = True
        return form


class MeetingList(PermissionRequiredMixin, ListViewMixin):
    permission_required = 'service.view_meeting'
    model = Meeting
    template_name = 'service/meeting_list.html'
    context = { 'url': 'meetings' }
    exclude = ['id', 'duration', 'event', 'phase', 'notes']
    slug = 'meeting'
    add_btn_str = 'Agendar consulta'

    def get_context_data(self, **kwargs):
        for meeting in Meeting.objects.all():
            meeting.check_missed()
        context = super().get_context_data(**kwargs)
        # Remove seconds from time fields
        if context['rows']:
            time_idx = context['cols'].index('Hora')
            for row in context['rows']:
                field = row['fields'][time_idx]
                field['value'] = field['value'][:-3]
        # Add custom navbar buttons
        if self.request.user.has_perm('service.add_meeting'):
            create_url = reverse('meeting-create')
            context['navbar'] = [
                {'icon': 'fas fa-plus', 'text': 'Agendar consulta', 'type': 'primary',
                    'href': create_url + '?duration=60&next=' + self.request.path},
                {'icon': 'fas fa-plus', 'text': 'Agendar rastreio', 'type': 'primary',
                    'href': create_url + '?duration=30&summary=rastreio&next=' + self.request.path},
                {'icon': 'fas fa-plus', 'text': 'Agendar outro', 'type': 'secondary',
                    'href': create_url + '?next=' + self.request.path}]
        # Add 'view' list item button
        if self.request.user.has_perm(f'service.change_{self.slug}'):
            context['buttons'].insert(0, { 'url': f'{self.slug }-start', 'icon': 'play'})
        return context

class MeetingDetail(PermissionRequiredMixin, DetailViewMixin):
    permission_required = 'service.view_meeting'
    model = Meeting
    exclude = ['id', 'client', 'date', 'time']
    slug = 'meeting'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meeting = get_object_or_404(Meeting, pk=self.kwargs['pk'])
        subheading = f"{meeting.date.strftime('%d-%m-%Y')} | {str(meeting.time)[:-3]}"
        context.update({ 'heading': meeting.client, 'subheading': subheading })
        return context

class MeetingFormMixin(GoogleApiMixin, FormViewMixin):
    model = Meeting
    fields = ['client', 'date', 'time', 'duration', 'summary', 'event']
    template_name = 'service/meeting_form.html'
    success_url = reverse_lazy('meetings')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].widget.attrs['placeholder'] = 'dia-mês-ano'
        form.fields['time'].widget.attrs['placeholder'] = 'hora:minuto'
        form.fields['event'].widget = forms.HiddenInput()
        form.fields['event'].required = False
        return form

class MeetingCreate(PermissionRequiredMixin, MeetingFormMixin, ClientBasedCreateMixin):
    permission_required = 'service.add_meeting'
    context = { 'title': 'Agendar consulta' }

    def get_initial(self):
        return get_param_to_dict(self.request, 'duration', super().get_initial())

class MeetingUpdate(PermissionRequiredMixin, MeetingFormMixin, ClientBasedUpdateMixin):
    permission_required = 'service.change_meeting'
    
    def form_valid(self, form):
        self.object.state = 's'
        self.object.save()
        return super().form_valid(form)

class MeetingDelete(PermissionRequiredMixin, MeetingFormMixin, DeleteViewMixin):
    permission_required = 'service.delete_meeting'
    model = Meeting
    template_name = 'service/meeting_confirm_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meeting = get_object_or_404(Meeting, pk=self.kwargs['pk'])
        context['js_context'].update({
            'calendarId': meeting.client.partner.calendar,
            'eventId': meeting.event,
        })
        return context


class MeetingFlowMixin(PermissionRequiredMixin, FormViewMixin, ViewMixin, generic.FormView):
    permission_required = 'service.change_meeting'
    model = Meeting

    def setup(self, request, *args, **kwargs):
        """Get meeting object."""
        self.meeting = get_object_or_404(Meeting, pk=kwargs['pk'])
        self.client = self.meeting.client
        return super().setup(request, *args, **kwargs)

    def get_initial(self):
        """Get meeting notes."""
        initial = super().get_initial()
        initial.update({ 'notes': self.meeting.notes })
        return initial

    def form_valid(self, form):
        """Save meeting notes."""
        self.meeting.notes = form.cleaned_data['notes']
        self.meeting.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        """Go to next or success url."""
        if hasattr(self, 'next_step_url'):
            url = reverse(self.next_step_url, kwargs={ 'pk': self.meeting.id })
            next_ = self.request.GET.get('next')
            if next_: url += '?next=' + next_
            return url
        else:
            return super().get_success_url()

class MeetingStart(MeetingFlowMixin):
    form_class = MeetingStartForm
    template_name = 'common/meeting_flow.html'
    context = { 'title': 'Início da consulta' }
    next_step_url = 'meeting-measure'
    
    def dispatch(self, request, *args, **kwargs):
        self.last_meeting = self.meeting.get_previous()
        if self.last_meeting is None:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial.update({ 'last_meeting_notes': self.last_meeting.notes })
        return initial
    
    def form_valid(self, form):
        self.meeting.state = 'o'
        self.meeting.save()
        return super().form_valid(form)

class MeetingMeasure(MeetingFlowMixin):
    form_class = MeetingMeasureForm
    template_name = 'service/meeting_measure.html'
    context = { 'title': 'Medições' }
    next_step_url = 'meeting-finish'

    def get_initial(self):
        """Get default measure unit."""
        initial = super().get_initial()
        measure_name = self.request.GET.get('measure') or 'weight'
        self.measure = Measure.objects.get(name__exact=measure_name)
        initial.update({ 'unit': self.measure.unit })
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields:
            if field != 'notes':
                form.fields[field].widget.attrs['class'] += 'border-0 '
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.meeting.client
        context.update({
            'meeting': self.meeting,
            'client': client,
            'measures': Measure.objects.all(),
            'current_measure': self.measure,
            'measurements': client.measurement_set.filter(measure=self.measure),
            'next_step_url': super().get_success_url()})
        return context

    def form_valid(self, form):
        """Save new measurement."""
        measurement = Measurement(
            client=self.meeting.client, meeting=self.meeting, measure=self.measure,
            value=form.cleaned_data['value'], unit=form.cleaned_data['unit'],
            date=form.cleaned_data['date'])
        measurement.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.request.get_full_path()
    
# def MeetingCalculate(MeetingFlowMixin):
#     form_class = MeetingCalculateForm
#     template_name = 'common/generic_form.html'
#     context = { 'title': 'Medições' }

# def MeetingPlan(MeetingFlowMixin):
#     form_class = MeetingPlanForm
#     template_name = 'common/generic_form.html'
#     context = { 'title': 'Medições' }

class MeetingFinish(MeetingFlowMixin):
    form_class = MeetingFinishForm
    template_name = 'service/meeting_finish.html'
    success_url = reverse_lazy('meetings')
    context = { 'title': 'Fim da consulta' }
    
    def form_valid(self, form):
        self.meeting.state = 'f'
        self.meeting.save()
        return super().form_valid(form)
    

class MeasurementList(PermissionRequiredMixin, ListViewMixin):
    permission_required = 'service.view_measurement'
    model = Measurement
    context = { 'url': 'measurements' }
    exclude = ['id']
    slug = 'measurement'
    add_btn_str = 'Nova medição'

class MeasurementFormMixin(FormViewMixin):
    model = Measurement
    fields = '__all__'

class MeasurementCreate(PermissionRequiredMixin, MeasurementFormMixin, ClientBasedCreateMixin):
    permission_required = 'service.add_measurement'

class MeasurementUpdate(PermissionRequiredMixin, MeasurementFormMixin, ClientBasedUpdateMixin):
    permission_required = 'service.change_measurement'

class MeasurementDelete(PermissionRequiredMixin, DeleteViewMixin):
    permission_required = 'service.delete_measurement'
    model = Measurement


class PrePlanList(PermissionRequiredMixin, ListViewMixin):
    permission_required = 'service.view_preplan'
    model = PrePlan
    context = { 'url': 'preplans' }
    fields = ['client', 'date', 'daily_energy']
    slug = 'preplan'
    add_btn_str = 'Novos cálculos'

class PrePlanDetail(PermissionRequiredMixin, DetailViewMixin):
    permission_required = 'service.view_preplan'
    model = PrePlan
    exclude = ['id', 'client', 'date']
    slug = 'preplan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        preplan = get_object_or_404(PrePlan, pk=self.kwargs['pk'])
        context.update({ 'heading': preplan.client, 'subheading': preplan.date.strftime('%d-%m-%Y') })
        return context

class PrePlanFormMixin(FormViewMixin):
    model = PrePlan
    fields = '__all__'
    template_name = 'preplan/index.html'
    success_url = reverse_lazy('preplans')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Setup range inputs
        for field in ['protein', 'carbs', 'fats']:
            form.fields[field].widget = NumberInput(attrs={
                'type': 'range',
                'class': 'custom-range',
                'step': '5'})
        # Get client
        if 'pk' in self.kwargs: self.client = self.object.client
        else:
            client_pk = self.request.GET.get('client')
            if client_pk: self.client = get_object_or_404(Client, pk=client_pk)
            else: return form
        # Get meeting queryset
        form.fields['meeting'].queryset = self.client.meeting_set.filter(date__lte=datetime.date.today())
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not hasattr(self, 'client'): return context
        context.update({
            'client': self.client,
            # 'preplan': preplan,
            'columns': {
                'client_info': ['Atual', 'Objetivo'],
                'calculations': ['Atual', 'Objetivo'],
                'niddk_calculator': ['Duração', 'Mudança no PAL', 'Atingir', 'Manter'],
                'macronutrients': ['Percentagem', 'Quantidade', 'Quantidade por peso'],
                # 'initial_dosages': ['Leite meio-gordo', 'Leite magro', 'Fruta', 'Vegetais'],
                # 'optimal_dosages': ['Carne e eq', 'Pão e eq', 'Gordura'],
                'food_dosages': ['Quantidade'],
            },
            # 'js_context': json.dumps(js_context),
        })
        return context

class PrePlanCreate(PermissionRequiredMixin, PrePlanFormMixin, ClientBasedCreateMixin):
    permission_required = 'service.add_preplan'

    def get_initial(self):
        return get_param_to_dict(self.request, 'meeting', super().get_initial(), Meeting)

    def form_valid(self, form):
        client_id = form.cleaned_data['client'].id
        if 'reload' in self.request.POST and client_id:
            url = reverse('preplan-create')
            return redirect(f'{url}?client={client_id}&next={self.get_next()}')
        form.instance.date = datetime.date.today()
        return super().form_valid(form)

class PrePlanUpdate(PermissionRequiredMixin, PrePlanFormMixin, ClientBasedUpdateMixin):
    permission_required = 'service.change_preplan'

class PrePlanDelete(PermissionRequiredMixin, DeleteViewMixin):
    permission_required = 'service.delete_preplan'
    model = PrePlan

"""@permission_required('service.view_plan')
def deliver_plan(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    client_name = plan.client.name
    context = {
        'client_name': client_name,
        'meals': [
            {'time': '08:00', 'name': 'Pequeno-almoço', 'content': [
                '1 rissol',
                '1 copo de bagaço',
            ]},
            {'time': '13:00', 'name': 'Almoço', 'content': [
                '1 pão com panado',
                '1 caneca de vinho da casa',
            ]},
            {'time': '21:00', 'name': 'Jantar', 'content': [
                '2 pratos de rojões',
                '6 colheres de sopa de arroz de sarrabulho',
                '1/2 garrafa de tinto',
            ]},
        ],
        'recommendations': [
            {'name': 'Alimentação', 'content': [
                'Cuidado com as carnes vermelhas.',
            ]},
            {'name': 'Atividade física', 'content': [
                'Passear o cão.',
            ]},
            {'name': 'Outros', 'content': [
                'Não bater na mulher.',
            ]},
        ],
    }
    return render(request, 'plan/deliverable.html', context=context)"""
