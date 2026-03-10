from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm, TicketForm
from .models import Ticket


def BasePage(request):
    tickets = Ticket.objects.select_related("created_by", "department").all()
    can_create_ticket = False
    if request.user.is_authenticated:
        student_profile = getattr(request.user, "student_profile", None)
        can_create_ticket = (
            student_profile is not None and 
            not student_profile.is_agent and 
            not request.user.is_superuser
        )
    return render(request, "base.html", {
            "tickets": tickets,
            "can_create_ticket": can_create_ticket,
        },
    )


# Login view
def LoginPage(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("base")
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html", {"form": form})


# Logout view
def LogoutPage(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


# Register view
def RegisterPage(request):
    form = RegisterForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()  # creates auth user + student profile
            messages.success(request, "Registration successful! You are registered as a student.")
            return redirect("login")
        messages.error(request, "Please correct the errors below.")

    return render(request, "register.html", {"form": form})


@login_required(login_url="login")
def CreateTicketPage(request):
    # student_profile = getattr(request.user, "student_profile", None)
    # if student_profile is None or student_profile.is_agent or request.user.is_superuser:
    #     messages.error(request, "Only students can create tickets.")
    #     return redirect("base")

    form = TicketForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.status = Ticket.TicketStatus.UNREAD
            ticket.save()
            messages.success(request, "Ticket created successfully.")
            return redirect("base")
        messages.error(request, "Please correct the errors below.")

    return render(request, "create_ticket.html", {"form": form})
