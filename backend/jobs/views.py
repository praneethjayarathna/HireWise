from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .parsers import extract_text
from .categorizer import categorize, compute_similarity, compare_overviews
from .skills_extractor import compare_skills, compare_education, compare_experience, compare_responsibilities
from .skills_extractor import compare_skills, compare_education, compare_experience, compare_responsibilities
from .serializers import (
    JobDescriptionUploadSerializer,
    CategorizedJobDescriptionSerializer,
    ResumeAnalyzeRequestSerializer,
    SimilarityScoreSerializer,
    CategorizedResumeSerializer,
    SkillAnalysisSerializer,
    EducationAnalysisSerializer,
    ExperienceAnalysisSerializer,
    ResponsibilityAnalysisSerializer,
    OverviewMatchSerializer,
)


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


class ResumeAnalyzeView(APIView):
    """
    POST /api/jobs/resume/analyze/
    Upload a PDF or DOCX resume along with a job description, receive:
      - categorized resume sentences
      - similarity scores per category
      - overall weighted similarity score
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        upload_serializer = ResumeAnalyzeRequestSerializer(data=request.data)
        if not upload_serializer.is_valid():
            return Response(upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        resume_file = upload_serializer.validated_data["resume_file"]
        job_description = upload_serializer.validated_data["job_description"]

        valid_categories = {"overview", "responsibilities", "qualifications", "skills"}
        if not all(cat in job_description for cat in valid_categories):
            return Response(
                {"detail": "job_description must contain all four categories."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            resume_text = extract_text(resume_file, resume_file.name)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"detail": "Failed to parse the uploaded file."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        if not resume_text.strip():
            return Response(
                {"detail": "The uploaded resume appears to be empty or unreadable."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        categorized_resume = categorize(resume_text)
        scores = compute_similarity(job_description, categorized_resume)

        # Sentence-level overview comparison
        jd_overview = job_description.get("overview", [])
        resume_overview = categorized_resume.get("overview", [])
        overview_matches = compare_overviews(jd_overview, resume_overview)

        job_text = "\n".join(
            sentence for sentences in job_description.values() for sentence in sentences
        )
        skill_analysis = compare_skills(job_text, resume_text)
        education_analysis = compare_education(job_text, resume_text)
        experience_analysis = compare_experience(job_text, resume_text)
        responsibility_analysis = compare_responsibilities(job_text, resume_text)

        resume_serializer = CategorizedResumeSerializer(data=categorized_resume)
        resume_serializer.is_valid(raise_exception=True)

        score_serializer = SimilarityScoreSerializer(data=scores)
        score_serializer.is_valid(raise_exception=True)

        overview_serializer = OverviewMatchSerializer(data=overview_matches, many=True)
        overview_serializer.is_valid(raise_exception=True)

        skill_serializer = SkillAnalysisSerializer(data=skill_analysis)
        skill_serializer.is_valid(raise_exception=True)

        edu_serializer = EducationAnalysisSerializer(data=education_analysis)
        edu_serializer.is_valid(raise_exception=True)

        exp_serializer = ExperienceAnalysisSerializer(data=experience_analysis)
        exp_serializer.is_valid(raise_exception=True)

        resp_serializer = ResponsibilityAnalysisSerializer(data=responsibility_analysis)
        resp_serializer.is_valid(raise_exception=True)

        return Response(
            {
                "categorized_resume": resume_serializer.validated_data,
                "similarity_scores": score_serializer.validated_data,
                "overview_matches": overview_serializer.validated_data,
                "skill_analysis": skill_serializer.validated_data,
                "education_analysis": edu_serializer.validated_data,
                "experience_analysis": exp_serializer.validated_data,
                "responsibility_analysis": resp_serializer.validated_data,
            },
            status=status.HTTP_200_OK,
        )
