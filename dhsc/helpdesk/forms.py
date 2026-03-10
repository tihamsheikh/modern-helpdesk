from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Student, Ticket


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
