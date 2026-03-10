from django.urls import path

from . import views

urlpatterns = [
    path('', views.BasePage, name='home'),
    path('base/', views.BasePage, name='base'),
    path('login/', views.LoginPage, name='login'),
    path('logout/', views.LogoutPage, name='logout'),
    path('register/', views.RegisterPage, name='register'),
    path('tickets/create/', views.CreateTicketPage, name='create_ticket'),
]
