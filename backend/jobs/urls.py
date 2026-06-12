from django.urls import path
from .views import (
    JobDescriptionAnalyzeView,
    ResumeAnalyzeView,
    CreateJobSessionView,
    UploadResumeToSessionView,
    SessionRankingsView,
    ResumeDetailView,
)

urlpatterns = [
    path("analyze/", JobDescriptionAnalyzeView.as_view(), name="job-analyze"),
    path("resume/analyze/", ResumeAnalyzeView.as_view(), name="resume-analyze"),
    path("sessions/", CreateJobSessionView.as_view(), name="create-session"),
    path("sessions/<int:session_id>/resumes/", UploadResumeToSessionView.as_view(), name="session-upload-resume"),
    path("sessions/<int:session_id>/rankings/", SessionRankingsView.as_view(), name="session-rankings"),
    path("sessions/<int:session_id>/resumes/<int:resume_id>/", ResumeDetailView.as_view(), name="resume-detail"),
]
