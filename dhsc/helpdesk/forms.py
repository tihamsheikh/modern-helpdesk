from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Ticket, Comment, Student, Department


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-control", "style": "max-width: 280px;"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "style": "max-width: 280px;"}),
    )


class RegisterForm(UserCreationForm):
    name = forms.CharField(
        label="Name",
        max_length=120,
        widget=forms.TextInput(attrs={"class": "form-control", "style": "max-width: 280px;"}),
    )
    roll = forms.CharField(
        label="Roll",
        max_length=40,
        widget=forms.TextInput(attrs={"class": "form-control", "style": "max-width: 280px;"}),
    )
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-control", "style": "max-width: 280px;"}),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "style": "max-width: 280px;"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "style": "max-width: 280px;"}),
    )

    class Meta:
        model = User
        fields = ("name", "roll", "username", "password1", "password2")

    def clean_roll(self):
        roll = self.cleaned_data["roll"].strip()
        if Student.objects.filter(roll__iexact=roll).exists():
            raise forms.ValidationError("This roll already exists.")
        return roll

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Student.objects.create(
                user=user,
                name=self.cleaned_data["name"].strip(),
                roll=self.cleaned_data["roll"].strip(),
            )
        return user


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("title", "description", "department", "attachment", "mode")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "attachment": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "mode": forms.RadioSelect(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {"content": forms.Textarea(attrs={"class": "form-control","placeholder": "Write your comment", "rows": 2})}


class ManagerTicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("status", "assiged_agent")#, "internal_note")
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "assiged_agent": forms.Select(attrs={"class": "form-select"}),
            # "internal_note": forms.Textarea(attrs={"class": "form-control", "rows": 1, "placeholder": "Note"})
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop("ticket", None)
        super().__init__(*args, **kwargs)

        queryset = Student.objects.filter(is_agent=True).select_related("user").order_by("name")
        self.fields["assiged_agent"].queryset = queryset


class ManagerStudentUpdateForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.select_related("user").order_by("name"),
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Select student",
    )
    is_agent = forms.ChoiceField(
        choices=(("true", "True"), ("false", "False")),
        widget=forms.Select(attrs={"class": "form-select"}),
        initial="false",
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.order_by("name"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label="Select department",
    )

    def __init__(self, *args, **kwargs):
        selected_student = kwargs.pop("student", None)
        super().__init__(*args, **kwargs)
        # refreshing
        self.fields["student"].queryset = Student.objects.select_related("user").order_by("name")
        self.fields["department"].queryset = Department.objects.order_by("name")

        if selected_student is not None:
            self.fields["student"].initial = selected_student
            self.fields["is_agent"].initial = "true" if selected_student.is_agent else "false"
            self.fields["department"].initial = selected_student.department


class AgentTicketStatusForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("status",)
        widgets = {"status": forms.Select(attrs={"class": "form-select"})}

