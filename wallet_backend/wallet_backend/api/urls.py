from django.urls import path
from . import views

urlpatterns = [
    path('auth/signup/', views.SignupView.as_view(), name='signup'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('user/profile/', views.ProfileView.as_view(), name='profile'),
    path('user/change-pin/', views.ChangePinView.as_view(), name='change_pin'),
    path('transactions/', views.TransactionListView.as_view(), name='transactions'),
    path('transactions/send/', views.SendTransactionView.as_view(), name='send_transaction'),
    path('contacts/search/', views.ContactSearchView.as_view(), name='contact_search'),
]
