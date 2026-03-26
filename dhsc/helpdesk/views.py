from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AgentTicketStatusForm, CommentForm, LoginForm, ManagerTicketUpdateForm, RegisterForm, TicketForm, ManagerStudentUpdateForm
from .models import Ticket, Comment, Student



# the main view 
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

# ticket creation view
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



# the ticket view
def TicketOverviewPage(request, user_ticket_id):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("manager_ticket", user_ticket_id=user_ticket_id)
    if request.user.is_authenticated:
        student_profile = getattr(request.user, "student_profile", None)
        if student_profile and student_profile.is_agent:
            return redirect("agent_ticket", user_ticket_id=user_ticket_id)

    ticket = get_object_or_404(
        Ticket.objects.select_related("created_by", "department", "assiged_agent"),
        user_ticket_id=user_ticket_id,
    )
    comments = Comment.objects.select_related("author").filter(ticket=ticket)

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please login to add a comment.")
            return redirect("login")

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added successfully.")
            return redirect("ticket_overview", user_ticket_id=user_ticket_id)
        messages.error(request, "Comment could not be added.")
    else:
        comment_form = CommentForm()

    return render(
        request,
        "ticket_overview.html",
        {"ticket": ticket, "comments": comments, "comment_form": comment_form},
    )


@login_required(login_url="login")
def AgentTicketPage(request, user_ticket_id):
    student_profile = getattr(request.user, "student_profile", None)
    if not student_profile or not student_profile.is_agent:
        messages.error(request, "Only agents can update ticket status.")
        return redirect("ticket_overview", user_ticket_id=user_ticket_id)

    ticket = get_object_or_404(
        Ticket.objects.select_related("created_by", "department", "assiged_agent"),
        user_ticket_id=user_ticket_id,
        assiged_agent=student_profile,
    )
    comments = Comment.objects.select_related("author").filter(ticket=ticket)

    if request.method == "POST":
        if "update_status" in request.POST:
            status_form = AgentTicketStatusForm(request.POST, instance=ticket)
            comment_form = CommentForm()
            if status_form.is_valid():
                status_form.save()
                messages.success(request, "Ticket status updated successfully.")
                return redirect("agent_ticket", user_ticket_id=user_ticket_id)
            messages.error(request, "Could not update ticket status.")
        elif "add_comment" in request.POST:
            status_form = AgentTicketStatusForm(instance=ticket)
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                comment.save()
                messages.success(request, "Comment added successfully.")
                return redirect("agent_ticket", user_ticket_id=user_ticket_id)
            messages.error(request, "Comment could not be added.")
        else:
            status_form = AgentTicketStatusForm(instance=ticket)
            comment_form = CommentForm()
    else:
        status_form = AgentTicketStatusForm(instance=ticket)
        comment_form = CommentForm()

    return render(
        request,
        "agent_ticket.html",
        {
            "ticket": ticket,
            "comments": comments,
            "comment_form": comment_form,
            "status_form": status_form,
        },
    )


# show tickets based on logged in user's role
@login_required(login_url="login")
def ShowTicketsPage(request):
    user = request.user
    student_profile = getattr(user, "student_profile", None)

    if user.is_superuser:
        tickets = Ticket.objects.select_related("created_by", "department", "assiged_agent").all()
    elif student_profile and student_profile.is_agent:
        tickets = Ticket.objects.select_related("created_by", "department", "assiged_agent").filter(
            assiged_agent=student_profile
        )
    else:
        tickets = Ticket.objects.select_related("created_by", "department", "assiged_agent").filter(
            created_by=user
        )

    return render(request, "show_tickets.html", {"tickets": tickets})


@login_required(login_url="login")
def ManagerTicketPage(request, user_ticket_id):
    if not request.user.is_superuser:
        messages.error(request, "Only managers can update ticket.")
        return redirect("ticket_overview", user_ticket_id=user_ticket_id)

    ticket = get_object_or_404(
        Ticket.objects.select_related("created_by", "department", "assiged_agent"),
        user_ticket_id=user_ticket_id,
    )
    comments = Comment.objects.select_related("author").filter(ticket=ticket)

    if request.method == "POST":
        if "duplicate_ticket" in request.POST:
            with transaction.atomic():
                duplicated_ticket = Ticket.objects.create(
                    title=ticket.title,
                    description=ticket.description,
                    department=ticket.department,
                    attachment=ticket.attachment,
                    mode=ticket.mode,
                    status=ticket.status,
                    assiged_agent=ticket.assiged_agent,
                    created_by=ticket.created_by,
                )
            messages.success(request, "Ticket duplicated successfully.")
            return redirect("manager_ticket", user_ticket_id=duplicated_ticket.user_ticket_id)
        elif "update_ticket" in request.POST:
            manager_form = ManagerTicketUpdateForm(request.POST, instance=ticket, ticket=ticket)
            if manager_form.is_valid():
                manager_form.save()
                messages.success(request, "Ticket updated successfully.")
                return redirect("manager_ticket", user_ticket_id=user_ticket_id)
            messages.error(request, "Could not update the ticket.")
        elif "add_comment" in request.POST:
            manager_form = ManagerTicketUpdateForm(instance=ticket, ticket=ticket)
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                comment.save()
                messages.success(request, "Comment added successfully.")
                return redirect("manager_ticket", user_ticket_id=user_ticket_id)
            messages.error(request, "Comment could not be added.")
        else:
            manager_form = ManagerTicketUpdateForm(instance=ticket, ticket=ticket)
            comment_form = CommentForm()
    else:
        manager_form = ManagerTicketUpdateForm(instance=ticket, ticket=ticket)
        comment_form = CommentForm()

    return render(
        request,
        "manager_ticket.html",
        {
            "ticket": ticket,
            "comments": comments,
            "comment_form": comment_form,
            "manager_form": manager_form,
        },
    )


# show all student view for manager
@login_required(login_url="login")
def ShowStudentsPage(request):
    if not request.user.is_superuser:
        messages.error(request, "Only manager is allowed")
        return redirect("login")

    if request.method == "POST" and "update_student" in request.POST:
        student_form = ManagerStudentUpdateForm(request.POST)
        if student_form.is_valid():
            student = student_form.cleaned_data["student"]
            is_agent = student_form.cleaned_data["is_agent"] == "true"
            department = student_form.cleaned_data["department"] if is_agent else None

            student.is_agent = is_agent
            student.department = department
            student.save(update_fields=["is_agent", "department"])

            messages.success(request, f"{student.name} updated successfully.")
            return redirect("show_students")
        messages.error(request, "Could not update.")
    else:
        student_form = ManagerStudentUpdateForm()

    students = Student.objects.select_related("user", "department").all()

    return render(
        request,
        "show_students.html",
        {
            "students": students,
            "student_form": student_form,
        },
    )



