from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('partners/', views.PartnerListView.as_view(), name='partners'),
    path('partner/<int:pk>', views.PartnerDetailView.as_view(), name='partner-detail'),
    path('partner/create/', views.PartnerCreate.as_view(), name='partner-create'),
    path('partner/<int:pk>/update/', views.PartnerUpdate.as_view(), name='partner-update'),
    path('partner/<int:pk>/delete/', views.PartnerDelete.as_view(), name='partner-delete'),

    path('clients/', views.ClientListView.as_view(), name='clients'),
    path('client/<int:pk>', views.ClientDetailView.as_view(), name='client-detail'),
    path('client/create/', views.ClientCreate.as_view(), name='client-create'),
    path('client/<int:pk>/update/', views.ClientUpdate.as_view(), name='client-update'),
    path('client/<int:pk>/delete/', views.ClientDelete.as_view(), name='client-delete'),
    
    path('meetings/', views.MeetingListView.as_view(), name='meetings'),
    path('meeting/<int:pk>', views.MeetingDetailView.as_view(), name='meeting-detail'),
    path('calendar/', views.calendar, name='calendar'),
    path('meeting/create/', views.MeetingCreate.as_view(), name='meeting-create'),
    path('meeting/create/<int:client_pk>/', views.MeetingCreate.as_view(), name='meeting-create'),
    path('meeting/create/<int:client_pk>/<int:duration>/', views.MeetingCreate.as_view(), name='meeting-create'),
    path('meeting/<int:pk>/update/', views.MeetingUpdate.as_view(), name='meeting-update'),
    path('meeting/<int:pk>/delete/', views.MeetingDelete.as_view(), name='meeting-delete'),

    path('plans/', views.PlanListView.as_view(), name='plans'),
    path('plan/<int:pk>', views.PlanDetailView.as_view(), name='plan-detail'),
    path('plan/create/', views.PlanCreate.as_view(), name='plan-create'),
    path('plan/create/<int:client_pk>/', views.PlanCreate.as_view(), name='plan-create'),
    path('plan/<int:pk>/update/', views.PlanUpdate.as_view(), name='plan-update'),
    path('plan/<int:pk>/delete/', views.PlanDelete.as_view(), name='plan-delete'),
    path('plan/<int:pk>/deliver/', views.deliver_plan, name='plan-deliver'),
]
