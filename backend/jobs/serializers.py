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
