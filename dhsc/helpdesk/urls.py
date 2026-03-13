from django.urls import path

from . import views

urlpatterns = [
    path('', views.BasePage, name='home'),
    path('base/', views.BasePage, name='base'),
    path('login/', views.LoginPage, name='login'),
    path('logout/', views.LogoutPage, name='logout'),
    path('register/', views.RegisterPage, name='register'),
    path('tickets/create/', views.CreateTicketPage, name='create_ticket'),
    path('tickets/<uuid:user_ticket_id>/', views.TicketOverviewPage, name='ticket_overview'),
    path('tickets/show_all/', views.ShowTicketsPage, name='show_tickets'),
    path('manager/tickets/<uuid:user_ticket_id>/', views.ManagerTicketPage, name='manager_ticket'),
    path('manager/students/', views.ShowStudentsPage, name='show_students'),
    path('agent/tickets/<uuid:user_ticket_id>/', views.AgentTicketPage, name='agent_ticket'),


]
