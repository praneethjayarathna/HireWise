from django.urls import path
from .views import JobDescriptionAnalyzeView

urlpatterns = [
    path("analyze/", JobDescriptionAnalyzeView.as_view(), name="job-analyze"),
]
