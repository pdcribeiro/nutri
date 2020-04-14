from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),

    path('clients/', views.ClientListView.as_view(), name='clients'),
    path('client/<int:pk>', views.ClientDetailView.as_view(), name='client-detail'),
    
    path('meetings/', views.MeetingListView.as_view(), name='meetings'),
    path('meeting/<int:pk>', views.MeetingDetailView.as_view(), name='meeting-detail'),

    path('plans/', views.PlanListView.as_view(), name='plans'),
    path('plan/<int:pk>', views.PlanDetailView.as_view(), name='plan-detail'),

    # path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    # path('borrowed/', views.LoanedBooksListView.as_view(), name='all-borrowed'),
    # path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),

    path('client/create/', views.ClientCreate.as_view(), name='client-create'),
    path('client/<int:pk>/update/', views.ClientUpdate.as_view(), name='client-update'),
    path('client/<int:pk>/delete/', views.ClientDelete.as_view(), name='client-delete'),

    # path('book/create/', views.BookCreate.as_view(), name='book-create'),
    # path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    # path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
]
