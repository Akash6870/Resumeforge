from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class CareerProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "email",
            "phone", "location", "linkedin_url", "portfolio_url",
            "professional_summary", "work_experience", "education",
            "skills", "certifications", "projects", "awards",
        )
        widgets = {
            "professional_summary": forms.Textarea(attrs={"rows": 4}),
            "work_experience":      forms.Textarea(attrs={"rows": 12}),
            "education":            forms.Textarea(attrs={"rows": 4}),
            "skills":               forms.Textarea(attrs={"rows": 3}),
            "certifications":       forms.Textarea(attrs={"rows": 3}),
            "projects":             forms.Textarea(attrs={"rows": 6}),
            "awards":               forms.Textarea(attrs={"rows": 3}),
        }