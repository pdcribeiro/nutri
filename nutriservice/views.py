from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

from nutriservice.models import Client, Meeting, Plan
from nutriservice.forms import ClientForm, MealsFormSet


def index(request):
    """View function for home page of site."""

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
    model = Client
    permission_required = 'nutriservice.view_client'
    paginate_by = 10

class ClientDetailView(PermissionRequiredMixin, generic.DetailView):
    model = Client
    permission_required = 'nutriservice.view_client'


class PlanListView(LoginRequiredMixin, generic.ListView):
    model = Plan
    paginate_by = 10

class PlanDetailView(LoginRequiredMixin, generic.DetailView):
    model = Plan


class MeetingListView(LoginRequiredMixin, generic.ListView):
    model = Meeting
    paginate_by = 10

class MeetingDetailView(LoginRequiredMixin, generic.DetailView):
    model = Meeting


'''TODO
- how to save blank/unchanged text fields; explore use of choices instead
'''

class ClientCreate(PermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    permission_required = 'nutriservice.add_client'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['form'].meals_formset = MealsFormSet()
    #     return context

    # def form_valid(self, form):
    #     self.object = form.save()
    # #     self.client_id = form.instance.id
    #     return super().form_valid(form)

    # def get_success_url(self):
    #     return reverse('client-detail', args=[str(self.client_id)])

class ClientUpdate(PermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    permission_required = 'nutriservice.change_client'

    # def form_valid(self, form):
    #     print(form)
    #     form.save()
    #     # self.client_id = form.instance.id
    #     return super().form_valid(form)

    # def get_success_url(self):
    #     print(vars(self))
    #     assert 1 == 0
    #     return reverse('client-detail', args=[str(self.client_id)])

    # def get_success_url(self):
    #     print(vars(self))
    #     assert 1==0
    #     return reverse('client-detail', args=[str(self.object.id)])


# class ClientCreate(PermissionRequiredMixin, CreateView):  #TODO review logic
#     model = Client
#     permission_required = 'nutriservice.add_client'
#     fields = ['name', 'born']

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['meals_formset'] = MealsFormSet()
#         return context

#     def form_valid(self, form):
#         meals_formset = MealsFormSet(self.request.POST)
#         if not meals_formset.is_valid():
#             raise ValidationError('Invalid meals formset.')
#         meals_formset.instance = self.object = form.save()
#         meals_formset.save()
#         return super().form_valid(form)

# class ClientUpdate(PermissionRequiredMixin, UpdateView):
#     model = Client
#     permission_required = 'nutriservice.add_client'
#     fields = ['name', 'born']

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['meals_formset'] = MealsFormSet(instance=self.object)
#         return context

#     def form_valid(self, form):
#         meals_formset = MealsFormSet(self.request.POST, instance=self.object)
#         if not meals_formset.is_valid():
#             raise ValidationError('Invalid meals formset.')
#         # meals_formset.instance = self.object = form.save()
#         form.save()
#         meals_formset.save()
#         return super().form_valid(form)

class ClientDelete(PermissionRequiredMixin, DeleteView):
    model = Client
    permission_required = 'nutriservice.delete_client'
    success_url = reverse_lazy('clients')
