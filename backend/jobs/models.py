from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class JobSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_sessions')
    title = models.CharField(max_length=255)
    job_text = models.TextField()
    categorized_jd = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ResumeAnalysis(models.Model):
    session = models.ForeignKey(JobSession, on_delete=models.CASCADE, related_name='resumes')
    filename = models.CharField(max_length=255)
    rank_score = models.FloatField()
    score_breakdown = models.JSONField()
    analysis = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rank_score']
