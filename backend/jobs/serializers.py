from rest_framework import serializers


class JobDescriptionUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        ext = value.name.rsplit(".", 1)[-1].lower()
        if ext not in ("pdf", "docx", "doc"):
            raise serializers.ValidationError("Only PDF and DOCX files are supported.")
        max_mb = 10
        if value.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(f"File size must not exceed {max_mb} MB.")
        return value


class CategorizedJobDescriptionSerializer(serializers.Serializer):
    overview = serializers.ListField(child=serializers.CharField())
    responsibilities = serializers.ListField(child=serializers.CharField())
    qualifications = serializers.ListField(child=serializers.CharField())
    skills = serializers.ListField(child=serializers.CharField())


class ResumeUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        ext = value.name.rsplit(".", 1)[-1].lower()
        if ext not in ("pdf", "docx", "doc"):
            raise serializers.ValidationError("Only PDF and DOCX files are supported.")
        max_mb = 10
        if value.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(f"File size must not exceed {max_mb} MB.")
        return value


class ResumeAnalyzeRequestSerializer(serializers.Serializer):
    resume_file = serializers.FileField()
    job_description = serializers.JSONField()


class SimilarityScoreSerializer(serializers.Serializer):
    overview = serializers.FloatField()
    responsibilities = serializers.FloatField()
    qualifications = serializers.FloatField()
    skills = serializers.FloatField()
    overall = serializers.FloatField()


class CategorizedResumeSerializer(serializers.Serializer):
    overview = serializers.ListField(child=serializers.CharField())
    responsibilities = serializers.ListField(child=serializers.CharField())
    qualifications = serializers.ListField(child=serializers.CharField())
    skills = serializers.ListField(child=serializers.CharField())


class SkillAnalysisSerializer(serializers.Serializer):
    matching_skills = serializers.ListField(child=serializers.CharField())
    missing_skills = serializers.ListField(child=serializers.CharField())
    skill_variations = serializers.DictField(child=serializers.CharField(), required=False)
    job_skills_count = serializers.IntegerField()
    resume_skills_count = serializers.IntegerField()
    match_rate = serializers.FloatField()
