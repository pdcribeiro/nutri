from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

from nutriservice.models import Client, Meeting, Plan
from nutriservice.forms import ClientForm, MealsFormSet


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


class PlanListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'nutriservice.view_plan'
    model = Plan
    paginate_by = 10

class PlanDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'nutriservice.view_plan'
    model = Plan


class MeetingListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'nutriservice.view_meeting'
    model = Meeting
    paginate_by = 10

class MeetingDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'nutriservice.view_meeting'
    model = Meeting


class ClientCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'nutriservice.add_client'
    model = Client
    form_class = ClientForm

    def form_valid(self, form):
        if self.request.user.groups.filter(name='nutritionist').exists():
            form.instance.nutritionist = self.request.user
        return super().form_valid(form)

class ClientUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'nutriservice.change_client'
    model = Client
    form_class = ClientForm

class ClientDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'nutriservice.delete_client'
    model = Client
    success_url = reverse_lazy('clients')
