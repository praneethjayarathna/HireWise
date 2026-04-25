from django.urls import path
from .views import JobDescriptionAnalyzeView, ResumeAnalyzeView

urlpatterns = [
    path("analyze/", JobDescriptionAnalyzeView.as_view(), name="job-analyze"),
    path("resume/analyze/", ResumeAnalyzeView.as_view(), name="resume-analyze"),
]
