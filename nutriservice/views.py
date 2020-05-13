import datetime
import json

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

from nutriservice.models import Client, Meeting, Plan, PAL
# from nutriservice.forms import ClientForm, MealsFormSet
from nutriservice.forms import PlanForm

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


class ClientListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'nutriservice.view_client'
    model = Client
    paginate_by = 10

class ClientDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'nutriservice.view_client'
    model = Client

# class ClientCreate(PermissionRequiredMixin, CreateView):
#     permission_required = 'nutriservice.add_client'
#     model = Client
#     form_class = ClientForm

#     def form_valid(self, form):
#         if self.request.user.groups.filter(name='nutritionist').exists():
#             form.instance.nutritionist = self.request.user
#         return super().form_valid(form)

# class ClientUpdate(PermissionRequiredMixin, UpdateView):
#     permission_required = 'nutriservice.change_client'
#     model = Client
#     form_class = ClientForm

class ClientCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'nutriservice.add_client'
    model = Client
    fields = '__all__'

class ClientUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'nutriservice.change_client'
    model = Client
    fields = '__all__'

class ClientDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'nutriservice.delete_client'
    model = Client
    success_url = reverse_lazy('clients')


class PlanListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'nutriservice.view_plan'
    model = Plan
    paginate_by = 10

class PlanDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'nutriservice.view_plan'
    model = Plan

class PlanMixin:
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
            'age': today.year - client.born.year -
                ((today.month, today.day) <
                (client.born.month, client.born.day)),
            'height': float(client.height),
            'weight': float(client.weight),
            'body_fat': float(client.body_fat),
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
            },
            'js_context': json.dumps(js_context),
        })
        return context

    def get_success_url(self):
        return self.request.GET.get('next', None) or reverse('plans')

class PlanCreate(PermissionRequiredMixin, PlanMixin, CreateView):
    permission_required = 'nutriservice.add_plan'
    model = Plan
    form_class = PlanForm
    template_name = 'plan/index.html'

    def form_valid(self, form):
        form.instance.client = get_object_or_404(Client, pk=self.kwargs['client_pk'])
        form.instance.date = datetime.date.today()
        return super().form_valid(form)

class PlanUpdate(PermissionRequiredMixin, PlanMixin, UpdateView):
    permission_required = 'nutriservice.change_plan'
    model = Plan
    form_class = PlanForm
    template_name = 'plan/index.html'

class PlanDelete(PermissionRequiredMixin, PlanMixin, DeleteView):
    permission_required = 'nutriservice.delete_plan'
    model = Plan


class MeetingListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'nutriservice.view_meeting'
    model = Meeting
    paginate_by = 10

class MeetingDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'nutriservice.view_meeting'
    model = Meeting
