from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=120, blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    professional_summary = models.TextField(blank=True)
    work_experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    projects = models.TextField(blank=True)
    awards = models.TextField(blank=True)
    profile_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_full_profile_text(self) -> str:
        sections = [
            self.professional_summary,
            self.work_experience,
            self.education,
            self.skills,
            self.certifications,
            self.projects,
            self.awards,
        ]
        return " ".join(s for s in sections if s.strip())

    def __str__(self):
        return self.get_full_name() or self.username