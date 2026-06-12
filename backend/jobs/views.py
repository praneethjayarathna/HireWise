from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JobSession, ResumeAnalysis
from .parsers import extract_text
from .categorizer import categorize, compute_similarity, compare_overviews
from .skills_extractor import (
    compare_skills,
    compare_education,
    compare_experience,
    compare_responsibilities,
    compare_certifications_with_job,
    compare_projects_with_job,
    extract_projects,
    extract_certifications,
)
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


def _compute_rank_score(analysis: dict):
    """
    Composite ranking score (0–100) from all analysis dimensions.

    Weights:
      Skills (effective)   35 %
      Responsibilities     25 %
      Education            15 %
      Experience           10 %
      Certifications        8 %
      Projects              7 %
    """
    skill = analysis.get('skill_analysis', {})
    resp  = analysis.get('responsibility_analysis', {})
    edu   = analysis.get('education_analysis', {})
    exp   = analysis.get('experience_analysis', {})
    cert  = analysis.get('certification_analysis', {})
    proj  = analysis.get('project_analysis', {})

    skill_rate = skill.get('effective_match_rate', skill.get('match_rate', 0)) / 100.0
    resp_score = resp.get('effective_score', resp.get('score', 0)) / 100.0
    edu_ok     = 1.0 if edu.get('meets_requirement', False) else 0.3
    exp_ok     = 1.0 if exp.get('meets_requirement', False) else 0.3
    cert_rate  = cert.get('overall_match_score', 0) / 100.0
    proj_rate  = proj.get('overall_match_score', 0) / 100.0

    composite = (
        skill_rate * 0.35 +
        resp_score * 0.25 +
        edu_ok     * 0.15 +
        exp_ok     * 0.10 +
        cert_rate  * 0.08 +
        proj_rate  * 0.07
    )
    rank_score = round(composite * 100, 1)

    breakdown = {
        'skills':           round(skill_rate * 100, 1),
        'responsibilities': round(resp_score * 100, 1),
        'education_met':    bool(edu.get('meets_requirement', False)),
        'experience_met':   bool(exp.get('meets_requirement', False)),
        'certifications':   round(cert_rate * 100, 1),
        'projects':         round(proj_rate * 100, 1),
    }
    return rank_score, breakdown


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

        # Extract once, reuse across all comparison functions to avoid redundant parsing
        resume_projects = extract_projects(resume_text)
        resume_certifications = extract_certifications(resume_text)

        skill_analysis = compare_skills(
            job_text, resume_text,
            projects=resume_projects,
            certifications=resume_certifications,
        )
        education_analysis = compare_education(job_text, resume_text)
        experience_analysis = compare_experience(job_text, resume_text)
        responsibility_analysis = compare_responsibilities(
            job_text, resume_text,
            projects=resume_projects,
        )
        certification_analysis = compare_certifications_with_job(
            resume_text, job_text,
            extracted_certs=resume_certifications,
        )
        project_analysis = compare_projects_with_job(
            resume_text, job_text,
            extracted_projects=resume_projects,
        )

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
                "certification_analysis": certification_analysis,
                "project_analysis": project_analysis,
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Screening dashboard: session-based multi-resume ranking
# ---------------------------------------------------------------------------

class CreateJobSessionView(APIView):
    """
    POST /api/jobs/sessions/
    Upload a JD file → create a persistent session for batch resume screening.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        upload_ser = JobDescriptionUploadSerializer(data=request.data)
        if not upload_ser.is_valid():
            return Response(upload_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        file = upload_ser.validated_data["file"]
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
        session = JobSession.objects.create(
            user=request.user,
            title=file.name,
            job_text=raw_text,
            categorized_jd=categorized,
        )
        return Response(
            {
                "session_id": session.id,
                "title": session.title,
                "categorized_jd": categorized,
                "created_at": session.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class UploadResumeToSessionView(APIView):
    """
    POST /api/jobs/sessions/{session_id}/resumes/
    Analyze one resume against the session JD; persist result with rank score.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, session_id):
        try:
            session = JobSession.objects.get(id=session_id, user=request.user)
        except JobSession.DoesNotExist:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        upload_ser = JobDescriptionUploadSerializer(data=request.data)
        if not upload_ser.is_valid():
            return Response(upload_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        file = upload_ser.validated_data["file"]
        try:
            resume_text = extract_text(file, file.name)
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

        job_text = session.job_text
        job_description = session.categorized_jd

        categorized_resume = categorize(resume_text)
        scores = compute_similarity(job_description, categorized_resume)
        overview_matches = compare_overviews(
            job_description.get("overview", []),
            categorized_resume.get("overview", []),
        )

        resume_projects = extract_projects(resume_text)
        resume_certifications = extract_certifications(resume_text)

        skill_analysis = compare_skills(
            job_text, resume_text,
            projects=resume_projects,
            certifications=resume_certifications,
        )
        education_analysis = compare_education(job_text, resume_text)
        experience_analysis = compare_experience(job_text, resume_text)
        responsibility_analysis = compare_responsibilities(
            job_text, resume_text,
            projects=resume_projects,
        )
        certification_analysis = compare_certifications_with_job(
            resume_text, job_text,
            extracted_certs=resume_certifications,
        )
        project_analysis = compare_projects_with_job(
            resume_text, job_text,
            extracted_projects=resume_projects,
        )

        full_analysis = {
            "categorized_resume": categorized_resume,
            "similarity_scores": scores,
            "overview_matches": overview_matches,
            "skill_analysis": skill_analysis,
            "education_analysis": education_analysis,
            "experience_analysis": experience_analysis,
            "responsibility_analysis": responsibility_analysis,
            "certification_analysis": certification_analysis,
            "project_analysis": project_analysis,
        }

        rank_score, breakdown = _compute_rank_score(full_analysis)

        resume_obj = ResumeAnalysis.objects.create(
            session=session,
            filename=file.name,
            rank_score=rank_score,
            score_breakdown=breakdown,
            analysis=full_analysis,
        )

        return Response(
            {
                "id": resume_obj.id,
                "filename": resume_obj.filename,
                "rank_score": resume_obj.rank_score,
                "score_breakdown": resume_obj.score_breakdown,
                "analysis": full_analysis,
            },
            status=status.HTTP_201_CREATED,
        )


class SessionRankingsView(APIView):
    """
    GET /api/jobs/sessions/{session_id}/rankings/
    Returns all resumes for a session sorted by rank score (highest first).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = JobSession.objects.get(id=session_id, user=request.user)
        except JobSession.DoesNotExist:
            return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        resumes = session.resumes.all()
        return Response(
            {
                "session_id": session.id,
                "title": session.title,
                "total_resumes": resumes.count(),
                "rankings": [
                    {
                        "id": r.id,
                        "filename": r.filename,
                        "rank_score": r.rank_score,
                        "score_breakdown": r.score_breakdown,
                        "created_at": r.created_at,
                    }
                    for r in resumes
                ],
            }
        )


class ResumeDetailView(APIView):
    """
    GET /api/jobs/sessions/{session_id}/resumes/{resume_id}/
    Returns the full analysis for one resume in a session.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id, resume_id):
        try:
            resume = ResumeAnalysis.objects.get(
                id=resume_id,
                session__id=session_id,
                session__user=request.user,
            )
        except ResumeAnalysis.DoesNotExist:
            return Response({"detail": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "id": resume.id,
                "filename": resume.filename,
                "rank_score": resume.rank_score,
                "score_breakdown": resume.score_breakdown,
                "analysis": resume.analysis,
            }
        )
