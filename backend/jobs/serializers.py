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
    skills_from_projects = serializers.ListField(child=serializers.CharField(), required=False)
    skills_from_certifications = serializers.ListField(child=serializers.CharField(), required=False)
    job_skills_count = serializers.IntegerField()
    resume_skills_count = serializers.IntegerField()
    match_rate = serializers.FloatField()
    effective_match_rate = serializers.FloatField(required=False)


class EducationItemSerializer(serializers.Serializer):
    type = serializers.CharField()
    level = serializers.CharField(allow_null=True)
    level_value = serializers.IntegerField(allow_null=True)
    major = serializers.CharField(allow_null=True)
    qualification_type = serializers.CharField(allow_null=True)
    context = serializers.CharField(required=False, allow_null=True)
    confidence = serializers.FloatField(required=False)


class EducationAnalysisSerializer(serializers.Serializer):
    job_education = serializers.ListField(child=EducationItemSerializer())
    resume_education = serializers.ListField(child=EducationItemSerializer())
    job_highest = EducationItemSerializer(allow_null=True)
    resume_highest = EducationItemSerializer(allow_null=True)
    meets_requirement = serializers.BooleanField()
    meets_requirement_message = serializers.CharField()
    job_majors = serializers.ListField(child=serializers.CharField())
    resume_majors = serializers.ListField(child=serializers.CharField())
    matching_majors = serializers.ListField(child=serializers.CharField())


class ExperienceSerializer(serializers.Serializer):
    required_years = serializers.CharField(allow_null=True)
    years_text = serializers.CharField(allow_null=True)
    level = serializers.CharField(allow_null=True)
    level_value = serializers.IntegerField(allow_null=True)
    context = serializers.CharField(allow_null=True)


class ExperienceAnalysisSerializer(serializers.Serializer):
    job_experience = ExperienceSerializer()
    resume_experience = ExperienceSerializer()
    meets_requirement = serializers.BooleanField()
    meets_message = serializers.CharField()


class OverviewMatchSerializer(serializers.Serializer):
    job_sentence = serializers.CharField()
    resume_sentence = serializers.CharField()
    similarity = serializers.FloatField()


class DutyMatchSerializer(serializers.Serializer):
    job_duty = serializers.CharField()
    experience_duty = serializers.CharField()
    similarity = serializers.FloatField()


class ResponsibilityAnalysisSerializer(serializers.Serializer):
    job_responsibilities = serializers.ListField(child=serializers.CharField())
    resume_experience_duties = serializers.ListField(child=serializers.DictField())
    matched_duties = serializers.ListField(child=DutyMatchSerializer())
    matched_via_projects = serializers.ListField(child=serializers.DictField(), required=False)
    unmatched_responsibilities = serializers.ListField(child=serializers.CharField())
    score = serializers.FloatField()
    effective_score = serializers.FloatField(required=False)
    explanation = serializers.CharField()
