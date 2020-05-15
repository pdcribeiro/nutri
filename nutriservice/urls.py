from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('clients/', views.ClientListView.as_view(), name='clients'),
    path('client/<int:pk>', views.ClientDetailView.as_view(), name='client-detail'),
    path('client/create/', views.ClientCreate.as_view(), name='client-create'),
    path('client/<int:pk>/update/', views.ClientUpdate.as_view(), name='client-update'),
    path('client/<int:pk>/delete/', views.ClientDelete.as_view(), name='client-delete'),
    
    path('meetings/', views.MeetingListView.as_view(), name='meetings'),
    path('meeting/<int:pk>', views.MeetingDetailView.as_view(), name='meeting-detail'),
    path('meeting/<int:client_pk>/create/', views.MeetingCreate.as_view(), name='meeting-create'),
    path('meeting/<int:pk>/update/', views.MeetingUpdate.as_view(), name='meeting-update'),
    path('meeting/<int:pk>/delete/', views.MeetingDelete.as_view(), name='meeting-delete'),

    path('plans/', views.PlanListView.as_view(), name='plans'),
    path('plan/<int:pk>', views.PlanDetailView.as_view(), name='plan-detail'),
    path('plan/<int:client_pk>/create/', views.PlanCreate.as_view(), name='plan-create'),
    path('plan/<int:pk>/update/', views.PlanUpdate.as_view(), name='plan-update'),
    path('plan/<int:pk>/delete/', views.PlanDelete.as_view(), name='plan-delete'),
]
