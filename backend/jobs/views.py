from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .parsers import extract_text
from .categorizer import categorize
from .serializers import JobDescriptionUploadSerializer, CategorizedJobDescriptionSerializer


class JobDescriptionAnalyzeView(APIView):
    """
    POST /api/jobs/analyze/
    Upload a PDF or DOCX job description and receive it categorized into:
      - overview
      - responsibilities
      - qualifications
      - skills
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        upload_serializer = JobDescriptionUploadSerializer(data=request.data)
        if not upload_serializer.is_valid():
            return Response(upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = upload_serializer.validated_data["file"]

        try:
            raw_text = extract_text(file, file.name)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"detail": "Failed to parse the uploaded file."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        if not raw_text.strip():
            return Response(
                {"detail": "The uploaded file appears to be empty or unreadable."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        categorized = categorize(raw_text)

        out_serializer = CategorizedJobDescriptionSerializer(data=categorized)
        out_serializer.is_valid(raise_exception=True)
        return Response(out_serializer.validated_data, status=status.HTTP_200_OK)
