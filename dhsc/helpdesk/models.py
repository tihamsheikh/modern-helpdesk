from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from uuid import uuid4

class Department(models.Model):
    class DepartmentName(models.TextChoices):
        DEVELOPMENT = "Development", "Development"
        R_AND_D = "R&D", "R&D"
        DESIGN = "Design", "Design"
        DEBUGGERS = "Debuggers", "Debuggers"
        TESTERS = "Testers", "Testers"
        EXICUTIONERS = "Exicutioners", "Exicutioners"

    name = models.CharField(max_length=60, unique=True, choices=DepartmentName.choices)

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    name = models.CharField(max_length=120)
    roll = models.CharField(max_length=40, unique=True)
    is_agent = models.BooleanField(default=False)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agents",
    )

    def clean(self):
        if self.department and not self.is_agent:
            raise ValidationError({"department": "Only agents can be assigned to a department."})

    def __str__(self):
        role = "Manager" if self.user.is_superuser else ("Agent" if self.is_agent else "Student")
        return f"{self.name} ({self.roll}) - {role}"


class Ticket(models.Model):
    class TicketMode(models.TextChoices):
        ONLINE = "online", "Online"
        OFFLINE = "offline", "Offline"

    class TicketStatus(models.TextChoices):
        UNREAD = "unread", "Unread"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETE = "complete", "Complete"

    ticket_id = models.BigAutoField(primary_key=True)
    user_ticket_id = models.UUIDField(default=uuid4, editable=False, null=True, unique=True)
    title = models.CharField(max_length=50)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="tickets")
    attachment = models.FileField(upload_to="ticket_attachments/", blank=True, null=True)
    mode = models.CharField(max_length=10, choices=TicketMode.choices)
    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.UNREAD,
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    # def clean(self):
    #     if self.created_by_id:
    #         student_profile = getattr(self.created_by, "student_profile", None)
    #         if student_profile is None or student_profile.is_agent or self.created_by.is_superuser:
    #             raise ValidationError("Only students can create tickets.")

    def __str__(self):
        return f"#{self.ticket_id} - {self.title}"
