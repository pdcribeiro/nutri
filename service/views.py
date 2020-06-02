import datetime
import json
import os

from django import forms
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic, View
from django.views.generic.edit import ModelFormMixin

from .models import Partner, Client, Measure, Measurement, Meeting, Plan, PAL
from .forms import ClientForm, MeetingStartForm, MeetingMeasureForm, MeetingCalculateForm, MeetingPlanForm, MeetingFinishForm


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


class ViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

class ListMixin(ViewMixin, generic.ListView):
    context_object_name = 'list'
    paginate_by = 10
    template_name = 'common/generic_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

class DetailMixin(ViewMixin, generic.DetailView):
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

class DeleteViewMixin(ViewMixin):
    context_object_name = 'object'
    template_name = 'common/generic_confirm_delete.html'

class FormMixin:
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
        num_plans = Plan.objects.all().count()
        
        # # Number of visits to this view, as counted in the session variable.
        # num_visits = request.session.get('num_visits', 0)
        # request.session['num_visits'] = num_visits + 1

        context = {
            'title': 'Início',
            'url': 'home',
            'num_clients': num_clients,
            'num_meetings': num_meetings,
            'num_plans': num_plans,
            # 'num_visits': num_visits,
        }

        return render(request, 'index.html', context=context)


class PartnerList(PermissionRequiredMixin, ListMixin):
    permission_required = 'service.view_partner'
    model = Partner
    context = { 'title': 'Parceiros', 'url': 'partners', 'plural': 'parceiros' }
    exclude = ['id']
    slug = 'partner'
    add_btn_str = 'Novo parceiro'

class PartnerDetail(PermissionRequiredMixin, DetailMixin):
    permission_required = 'service.view_partner'
    model = Partner
    context = { 'title': 'Detalhes do parceiro' }
    exclude = ['id']
    slug = 'partner'

class PartnerFormMixin(GoogleApiMixin, FormMixin, ViewMixin):
    model = Partner
    fields = '__all__'
    template_name = 'service/partner_form.html'

class PartnerCreate(PermissionRequiredMixin, PartnerFormMixin, generic.CreateView):
    permission_required = 'service.add_partner'
    context = { 'title': 'Criar parceiro' }

class PartnerUpdate(PermissionRequiredMixin, PartnerFormMixin, generic.UpdateView):
    permission_required = 'service.change_partner'
    context = { 'title': 'Editar parceiro' }

class PartnerDelete(PermissionRequiredMixin, DeleteViewMixin, generic.DeleteView):
    permission_required = 'service.delete_partner'
    model = Partner
    success_url = reverse_lazy('partners')
    context = { 'title': 'Apagar parceiro', 'name': 'parceiro' }


class ClientList(PermissionRequiredMixin, ListMixin):
    permission_required = 'service.view_client'
    model = Client
    context = { 'title': 'Clientes', 'url': 'clients', 'plural': 'clientes' }
    fields = ['name', 'gender', 'age', 'weight', 'partner']
    slug = 'client'
    add_btn_str = 'Novo cliente'

class ClientDetail(PermissionRequiredMixin, DetailMixin):
    permission_required = 'service.view_client'
    model = Client
    context_object_name = 'client'
    template_name = 'service/client_detail.html'
    context = { 'title': 'Detalhes do cliente' }
    exclude = ['id', 'user', 'nutritionist']
    slug = 'client'

class ClientFormMixin(FormMixin, ViewMixin):
    model = Client
    form_class = ClientForm
    template_name = 'service/client_form.html'

class ClientCreate(PermissionRequiredMixin, ClientFormMixin, generic.CreateView):
    permission_required = 'service.add_client'
    context = { 'title': 'Novo cliente' }

    def form_valid(self, form):
        if self.request.user.groups.filter(name='nutritionist').exists():
            form.instance.nutritionist = self.request.user
        return super().form_valid(form)

class ClientUpdate(PermissionRequiredMixin, ClientFormMixin, generic.UpdateView):
    permission_required = 'service.change_client'
    context = { 'title': 'Editar cliente' }

class ClientDelete(PermissionRequiredMixin, DeleteViewMixin, generic.DeleteView):
    permission_required = 'service.delete_client'
    model = Client
    success_url = reverse_lazy('clients')
    context = { 'title': 'Apagar cliente', 'name': 'cliente' }

class ClientBasedCreateMixin(generic.CreateView):
    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'client': get_object_or_404(Client, pk=self.kwargs['client_pk'])
                if 'client_pk' in self.kwargs else None})
        return initial

class ClientBasedUpdateMixin(generic.UpdateView):
    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'client': get_object_or_404(self.model, pk=self.kwargs['pk']).client})
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['client'].disabled = True
        return form


class MeetingList(PermissionRequiredMixin, ListMixin):
    permission_required = 'service.view_meeting'
    model = Meeting
    template_name = 'service/meeting_list.html'
    context = { 'title': 'Consultas', 'url': 'meetings', 'plural': 'consultas' }
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
        # if self.request.user.has_perm('service.add_meeting'):
        #     context['navbar'] = [
        #         { 'text': 'Agendar consulta', 'type': 'primary', 'href': reverse('meeting-create', args=[30]) },
        #         { 'text': 'Agendar rastreio', 'type': 'primary', 'href': reverse('meeting-create', args=[60]) },
        #         { 'text': 'Agendar outro', 'type': 'secondary', 'href': reverse('meeting-create') },
        #     ]
        # Add 'view' list item button
        if self.request.user.has_perm(f'service.change_{self.slug}'):
            context['buttons'].insert(0, { 'url': f'{self.slug }-start', 'icon': 'play'})
        return context

class MeetingDetail(PermissionRequiredMixin, DetailMixin):
    permission_required = 'service.view_meeting'
    model = Meeting
    context = { 'title': 'Detalhes da consulta' }
    exclude = ['id', 'client', 'date', 'time']
    slug = 'meeting'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meeting = get_object_or_404(Meeting, pk=self.kwargs['pk'])
        subheading = f"{meeting.date.strftime('%d-%m-%Y')} | {str(meeting.time)[:-3]}"
        context.update({ 'heading': meeting.client, 'subheading': subheading })
        return context

class MeetingFormMixin(GoogleApiMixin, FormMixin, ViewMixin):
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
        initial = super().get_initial()
        if 'duration' in self.kwargs:
            initial.update({ 'duration': self.kwargs['duration'] })
        return initial

class MeetingUpdate(PermissionRequiredMixin, MeetingFormMixin, ClientBasedUpdateMixin):
    permission_required = 'service.change_meeting'
    context = { 'title': 'Editar consulta' }
    
    def form_valid(self, form):
        self.object.state = 's'
        self.object.save()
        return super().form_valid(form)

class MeetingDelete(PermissionRequiredMixin, MeetingFormMixin, generic.DeleteView):
    permission_required = 'service.delete_meeting'
    model = Meeting
    template_name = 'service/meeting_confirm_delete.html'
    context = { 'title': 'Apagar consulta', 'name': 'consulta' }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meeting = get_object_or_404(Meeting, pk=self.kwargs['pk'])
        context['js_context'].update({
            'calendarId': meeting.client.partner.calendar,
            'eventId': meeting.event,
        })
        return context


class MeetingMixin(PermissionRequiredMixin, FormMixin, ViewMixin, generic.FormView):
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

class MeetingStart(MeetingMixin):
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

class MeetingMeasure(MeetingMixin):
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
        return self.request.path
    
# def MeetingCalculate(MeetingMixin):
#     form_class = MeetingCalculateForm
#     template_name = 'common/meeting_calculate_form.html'
#     context = { 'title': 'Medições' }

# def MeetingPlan(MeetingMixin):
#     form_class = MeetingPlanForm
#     template_name = 'common/meeting_plan_form.html'
#     context = { 'title': 'Medições' }

class MeetingFinish(MeetingMixin):
    form_class = MeetingFinishForm
    template_name = 'service/meeting_finish.html'
    success_url = reverse_lazy('meetings')
    context = { 'title': 'Fim da consulta' }
    
    def form_valid(self, form):
        self.meeting.state = 'f'
        self.meeting.save()
        return super().form_valid(form)
    

class MeasurementList(PermissionRequiredMixin, ListMixin):
    permission_required = 'service.view_measurement'
    model = Measurement
    context = { 'title': 'Medições', 'url': 'measurements', 'plural': 'medições' }
    exclude = ['id']
    slug = 'measurement'
    add_btn_str = 'Nova medição'

class MeasurementFormMixin(FormMixin, ViewMixin):
    model = Measurement
    fields = '__all__'

class MeasurementCreate(PermissionRequiredMixin, MeasurementFormMixin, ClientBasedCreateMixin):
    permission_required = 'service.add_measurement'
    context = { 'title': 'Nova medição' }

class MeasurementUpdate(PermissionRequiredMixin, MeasurementFormMixin, ClientBasedUpdateMixin):
    permission_required = 'service.change_measurement'
    context = { 'title': 'Editar medição' }

class MeasurementDelete(PermissionRequiredMixin, DeleteViewMixin, generic.DeleteView):
    permission_required = 'service.delete_measurement'
    model = Measurement
    context = { 'title': 'Apagar medição', 'name': 'medição' }


class PlanList(PermissionRequiredMixin, ListMixin):
    permission_required = 'service.view_plan'
    model = Plan
    context = { 'title': 'Planos', 'url': 'plans', 'plural': 'planos' }
    fields = ['client', 'date', 'daily_energy']
    slug = 'plan'
    add_btn_str = 'Novo plano'

class PlanDetail(PermissionRequiredMixin, DetailMixin):
    permission_required = 'service.view_plan'
    model = Plan
    context = { 'title': 'Detalhes do plano' }
    exclude = ['id', 'client', 'date']
    slug = 'plan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan = get_object_or_404(Plan, pk=self.kwargs['pk'])
        context.update({ 'heading': plan.client, 'subheading': plan.date.strftime('%d-%m-%Y') })
        return context

class PlanFormMixin(FormMixin, ViewMixin):
    model = Plan
    fields = '__all__'
    template_name = 'plan/index.html'
    success_url = reverse_lazy('plans')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in ['proteins', 'carbs', 'fats']:
            form.fields[field].widget = NumberInput(attrs={
                'type': 'range',
                'class': 'custom-range',
                'step': '5'})
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'client_pk' in self.kwargs:
            client = get_object_or_404(Client, pk=self.kwargs['client_pk'])
        elif 'pk' in self.kwargs:
            client = get_object_or_404(Plan, pk=self.kwargs['pk']).client
        else:
            return context
        
        # today = datetime.date.today()
        js_context = {
            'gender': client.gender,
            # 'age': today.year - client.born.year -
            #     ((today.month, today.day) <
            #     (client.born.month, client.born.day)),
            'age': client.age,
            'height': float(client.height),
            'weight': float(client.weight),
            'bodyFat': client.body_fat and float(client.body_fat) or '',
            'pal': str(client.pal),
            'palMap': { str(key): val for [key, val] in PAL },
        }
        context.update({
            'client': client,
            # 'plan': plan,
            'columns': {
                'client_info': ['Atual', 'Objetivo'],
                'calculations': ['Atual', 'Objetivo'],
                'niddk_calculator': ['Duração', 'Mudança no PAL', 'Atingir', 'Manter'],
                'macronutrients': ['Percentagem', 'Quantidade', 'Quantidade por peso'],
                # 'initial_dosages': ['Leite meio-gordo', 'Leite magro', 'Fruta', 'Vegetais'],
                # 'optimal_dosages': ['Carne e eq', 'Pão e eq', 'Gordura'],
                'food_dosages': ['Quantidade'],
            },
            'js_context': json.dumps(js_context),
        })
        return context

class PlanCreate(PermissionRequiredMixin, PlanFormMixin, ClientBasedCreateMixin):
    permission_required = 'service.add_plan'
    context = { 'title': 'Novo plano' }

    def form_valid(self, form):
        client_id = form.cleaned_data['client'].id
        if 'reload' in self.request.POST and client_id:
            url = reverse('plan-create', args=[client_id])
            return redirect(url + '?next=' + self.get_next())
        form.instance.date = datetime.date.today()
        return super().form_valid(form)

class PlanUpdate(PermissionRequiredMixin, PlanFormMixin, ClientBasedUpdateMixin):
    permission_required = 'service.change_plan'
    context = { 'title': 'Editar plano' }

class PlanDelete(PermissionRequiredMixin, DeleteViewMixin, generic.DeleteView):
    permission_required = 'service.delete_plan'
    model = Plan
    context = { 'title': 'Apagar plano', 'name': 'plano' }

@permission_required('service.view_plan')
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
    return render(request, 'plan/deliverable.html', context=context)


def get_calendar(request, client_pk):
    client = get_object_or_404(Client, pk=client_pk)
    return HttpResponse(client.partner.calendar)
