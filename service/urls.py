from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='index'),

    path('partners/', views.PartnerList.as_view(), name='partners'),
    path('partner/<int:pk>', views.PartnerDetail.as_view(), name='partner-detail'),
    path('partner/create/', views.PartnerCreate.as_view(), name='partner-create'),
    path('partner/<int:pk>/update/', views.PartnerUpdate.as_view(), name='partner-update'),
    path('partner/<int:pk>/delete/', views.PartnerDelete.as_view(), name='partner-delete'),

    path('clients/', views.ClientList.as_view(), name='clients'),
    path('client/<int:pk>', views.ClientDetail.as_view(), name='client-detail'),
    path('client/create/', views.ClientCreate.as_view(), name='client-create'),
    path('client/<int:pk>/update/', views.ClientUpdate.as_view(), name='client-update'),
    path('client/<int:pk>/delete/', views.ClientDelete.as_view(), name='client-delete'),

    path('measures/', views.MeasurementList.as_view(), name='measurements'),
    # path('measure/<int:pk>', views.MeasurementDetail.as_view(), name='measurement-detail'),
    path('measure/create/', views.MeasurementCreate.as_view(), name='measurement-create'),
    path('measure/<int:pk>/update/', views.MeasurementUpdate.as_view(), name='measurement-update'),
    path('measure/<int:pk>/delete/', views.MeasurementDelete.as_view(), name='measurement-delete'),
    
    path('meetings/', views.MeetingList.as_view(), name='meetings'),
    path('meeting/<int:pk>', views.MeetingDetail.as_view(), name='meeting-detail'),
    path('meeting/create/', views.MeetingCreate.as_view(), name='meeting-create'),
    path('meeting/create/<int:client_pk>/', views.MeetingCreate.as_view(), name='meeting-create'),
    path('meeting/create/<int:client_pk>/<int:duration>/', views.MeetingCreate.as_view(), name='meeting-create'),
    path('meeting/<int:pk>/update/', views.MeetingUpdate.as_view(), name='meeting-update'),
    path('meeting/<int:pk>/delete/', views.MeetingDelete.as_view(), name='meeting-delete'),

    path('meeting/<int:pk>/start/', views.MeetingStart.as_view(), name='meeting-start'),
    path('meeting/<int:pk>/measure/', views.MeetingMeasure.as_view(), name='meeting-measure'),
    # path('meeting/<int:pk>/calculate/', views.MeetingCalculate.as_view(), name='meeting-calculate'),
    # path('meeting/<int:pk>/plan/', views.MeetingPlan.as_view(), name='meeting-plan'),
    path('meeting/<int:pk>/finish/', views.MeetingFinish.as_view(), name='meeting-finish'),
    
    path('calendar/<int:client_pk>/', views.get_calendar, name='get-calendar'),

    path('plans/', views.PlanList.as_view(), name='plans'),
    path('plan/<int:pk>', views.PlanDetail.as_view(), name='plan-detail'),
    path('plan/create/', views.PlanCreate.as_view(), name='plan-create'),
    path('plan/create/<int:client_pk>/', views.PlanCreate.as_view(), name='plan-create'),
    path('plan/<int:pk>/update/', views.PlanUpdate.as_view(), name='plan-update'),
    path('plan/<int:pk>/delete/', views.PlanDelete.as_view(), name='plan-delete'),
    path('plan/<int:pk>/deliver/', views.deliver_plan, name='plan-deliver'),
]
