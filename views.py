from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .models import User
from .forms import RegisterForm, CareerProfileForm


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("engine:dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Welcome! Fill in your career profile to get started.")
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CareerProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["sections"] = [
            ("professional_summary", "Professional Summary", 4,
             "Write a 2–4 sentence pitch for the top of your resume."),
            ("work_experience", "Work Experience", 12,
             "Job Title | Company | Month Year – Month Year\n- Achievement bullet"),
            ("education", "Education", 4, "Degree | Institution | Year"),
            ("skills", "Skills", 3, "Comma-separated: Python, Django, REST APIs..."),
            ("projects", "Projects", 6, "Project Name | Stack | Description"),
            ("certifications", "Certifications", 3, "Certification | Issuer | Year"),
            ("awards", "Awards & Honours", 3, ""),
        ]
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Career profile saved successfully.")
        return super().form_valid(form)