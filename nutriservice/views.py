import datetime
import json

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic

from nutriservice.models import Partner, Client, Meeting, Plan, PAL
from nutriservice.forms import ClientForm, MeetingForm, PlanForm

@login_required
def index(request):
    """View function for site home page."""

    # Generate counts of some of the main objects
    num_clients = Client.objects.all().count()
    num_meetings = Meeting.objects.all().count()
    num_plans = Plan.objects.all().count()
    
    # # Number of visits to this view, as counted in the session variable.
    # num_visits = request.session.get('num_visits', 0)
    # request.session['num_visits'] = num_visits + 1

    context = {
        'num_clients': num_clients,
        'num_meetings': num_meetings,
        'num_plans': num_plans,
        # 'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)


def get_field_value(field, obj):
    value = field.value_to_string(obj)
    if field.many_to_one:
        obj = get_object_or_404(field.target_field.model, pk=value)
        return {'href': obj.get_absolute_url(), 'value': obj}
    else:
        return {'value': value}

class ListViewMixin:
    context_object_name = 'list'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lst = context['list']
        context.update({
            'cols': [field.verbose_name for field in lst[0]._meta.fields
                if field.name not in self.exclude],
            'rows': [{
                'id': obj.id,
                'fields': [get_field_value(field, obj) for field in obj._meta.fields
                    if field.name not in self.exclude]
            } for obj in lst],
            'buttons': [{'url': f'{self.slug}-detail', 'icon': 'file-alt'}],
        })
        if self.request.user.has_perm(f'nutriservice.change_{self.slug}'):
            context['buttons'].append({'url': f'{self.slug}-update', 'icon': 'edit'})
        if self.request.user.has_perm(f'nutriservice.delete_{self.slug}'):
            context['buttons'].append({'url': f'{self.slug}-delete', 'icon': 'trash-alt'})
        return context

class DetailViewMixin:
    context_object_name = 'object'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context['object']
        context.update({
            'fields': [{
                'name': field.verbose_name,
                'data': get_field_value(field, obj)
            } for field in obj._meta.fields if field.name not in self.exclude],
        })
        return context


class PartnerListView(PermissionRequiredMixin, ListViewMixin, generic.ListView):
    permission_required = 'nutriservice.view_partner'
    model = Partner
    exclude = ['id']
    template_name = 'nutriservice/template_list.html'
    slug = 'partner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Parceiros', 'url': 'partners', 'navbar': [], 'plural': 'parceiros',
        })
        if self.request.user.has_perm('nutriservice.add_partner'):
            context['navbar'] += [{
                'type': 'primary',
                'href': reverse('partner-create'),
                'text': 'Novo parceiro'}]
        return context

class PartnerDetailView(PermissionRequiredMixin, DetailViewMixin, generic.DetailView):
    permission_required = 'nutriservice.view_partner'
    model = Partner
    exclude = ['id']
    template_name = 'nutriservice/template_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Detalhes do parceiro'})
        return context

class PartnerCreate(PermissionRequiredMixin, generic.CreateView):
    permission_required = 'nutriservice.add_partner'
    model = Partner
    fields = '__all__'
    template_name = 'nutriservice/template_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Criar parceiro'})
        return context

class PartnerUpdate(PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'nutriservice.change_partner'
    model = Partner
    fields = '__all__'
    template_name = 'nutriservice/template_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Editar parceiro'})
        return context

class PartnerDelete(PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'nutriservice.delete_partner'
    model = Partner
    context_object_name = 'object'
    template_name = 'nutriservice/template_confirm_delete.html'
    success_url = reverse_lazy('partners')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Apagar parceiro', 'name': 'parceiro'})
        return context


class ClientListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'nutriservice.view_partner'
    model = Client
    paginate_by = 10

class ClientDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'nutriservice.view_client'
    model = Client

class ClientCreate(PermissionRequiredMixin, generic.CreateView):
    permission_required = 'nutriservice.add_client'
    model = Client
    form_class = ClientForm

    def form_valid(self, form):
        if self.request.user.groups.filter(name='nutritionist').exists():
            form.instance.nutritionist = self.request.user
        return super().form_valid(form)

class ClientUpdate(PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'nutriservice.change_client'
    model = Client
    form_class = ClientForm

class ClientDelete(PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'nutriservice.delete_client'
    model = Client
    success_url = reverse_lazy('clients')


class MeetingListView(PermissionRequiredMixin, ListViewMixin, generic.ListView):
    permission_required = 'nutriservice.view_meeting'
    model = Meeting
    exclude = ['id', 'duration']
    template_name = 'nutriservice/template_list.html'
    slug = 'meeting'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Consultas', 'url': 'meetings', 'navbar': [], 'plural': 'consultas',
        })
        if self.request.user.has_perm('nutriservice.add_meeting'):
            context['navbar'] += [{
                'type': 'primary',
                'href': reverse('meeting-create'),
                'text': 'Agendar consulta'}]
        return context

class MeetingDetailView(PermissionRequiredMixin, DetailViewMixin, generic.DetailView):
    permission_required = 'nutriservice.view_meeting'
    model = Meeting
    exclude = ['id']
    template_name = 'nutriservice/template_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Detalhes da consulta'})
        return context

@permission_required('nutriservice.view_meeting')
def calendar(request):
    return render(request, 'nutriservice/calendar.html')

class MeetingMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'next': self.request.GET.get('next', None) or reverse('plans')})
        return context
    
    def get_success_url(self):
        return self.request.GET.get('next', None) or reverse('meetings')

class MeetingCreate(PermissionRequiredMixin, MeetingMixin, generic.CreateView):
    permission_required = 'nutriservice.add_meeting'
    model = Meeting
    fields = '__all__'
    # form_class = MeetingForm

    def get_initial(self):
        self.initial.update({'date': datetime.date.today(),
            'time': datetime.datetime.now().strftime('%H:%M')})
        if 'duration' in self.kwargs:
            self.initial.update({'duration': self.kwargs['duration']})
        if 'client_pk' in self.kwargs:
            self.initial.update({'client': get_object_or_404(Client, pk=self.kwargs['client_pk'])})
        return super().get_initial()

    # def form_valid(self, form):
    #     if 'client_pk' in self.kwargs:
    #         form.instance.client = get_object_or_404(Client, pk=self.kwargs['client_pk'])
    #         form.instance.date = datetime.date.today()
    #     return super().form_valid(form)

class MeetingUpdate(PermissionRequiredMixin, MeetingMixin, generic.UpdateView):
    permission_required = 'nutriservice.change_meeting'
    model = Meeting
    form_class = MeetingForm

class MeetingDelete(PermissionRequiredMixin, MeetingMixin, generic.DeleteView):
    permission_required = 'nutriservice.delete_meeting'
    model = Meeting


class PlanListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'nutriservice.view_plan'
    model = Plan
    paginate_by = 10

class PlanDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'nutriservice.view_plan'
    model = Plan

class PlanMixin:
    def get_form(self, form_class=None):
        # form.fields['proteins'].widget = NumberInput(attrs={'type':'range', 'step': '5'})
        form = super().get_form(form_class)
        range_fields = ['proteins', 'carbs', 'fats']
        for field in form.fields:
            if field in range_fields:
                form.fields[field].widget = NumberInput(attrs={
                    'type':'range',
                    'class': 'custom-range',
                    'step': '5'})
            else:
                form.fields[field].widget.attrs.update({'class': 'form-control'})
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'client_pk' in self.kwargs:
            client = get_object_or_404(Client, pk=self.kwargs['client_pk'])
        else:
            client = get_object_or_404(Plan, pk=self.kwargs['pk']).client
        
        self.success_url = self.request.GET.get('next', None) or reverse('plans')
        today = datetime.date.today()
        js_context = {
            'gender': client.gender,
            # 'age': today.year - client.born.year -
            #     ((today.month, today.day) <
            #     (client.born.month, client.born.day)),
            'age': client.age,
            'height': float(client.height),
            'weight': float(client.weight),
            'body_fat': client.body_fat and float(client.body_fat) or '',
            'pal': str(client.pal),
            'pal_map': { str(key): val for [key, val] in PAL },
        }
        context.update({
            'next': self.request.GET.get('next', None) or reverse('plans'),
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

    def get_success_url(self):
        return self.request.GET.get('next', None) or reverse('plans')

class PlanCreate(PermissionRequiredMixin, PlanMixin, generic.CreateView):
    permission_required = 'nutriservice.add_plan'
    model = Plan
    form_class = PlanForm
    template_name = 'plan/index.html'

    def form_valid(self, form):
        form.instance.client = get_object_or_404(Client, pk=self.kwargs['client_pk'])
        form.instance.date = datetime.date.today()
        return super().form_valid(form)

class PlanUpdate(PermissionRequiredMixin, PlanMixin, generic.UpdateView):
    permission_required = 'nutriservice.change_plan'
    model = Plan
    form_class = PlanForm
    template_name = 'plan/index.html'

class PlanDelete(PermissionRequiredMixin, PlanMixin, generic.DeleteView):
    permission_required = 'nutriservice.delete_plan'
    model = Plan

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
