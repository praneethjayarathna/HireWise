import json
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


def _education_graduated_score(edu: dict) -> float:
    """
    Smooth 5-step education score — no cliff edge.

    Gap between job requirement level and resume level:
      0  (meets/exceeds)   → 1.00
      1  (one level below) → 0.70
      2                    → 0.45
      3+                   → 0.15
    No stated requirement  → 0.75 (neutral)
    Matching major adds    +0.08 bonus (capped at 1.0)

    Education level values (from EDUCATION_LEVELS):
      Certificate=1, Associate=2, Bachelor's=3, Master's=4, PhD=5
    """
    job_h = edu.get('job_highest')
    res_h = edu.get('resume_highest')

    if not job_h or not (job_h.get('level_value') or 0):
        return 0.75  # no education requirement stated

    job_lv = job_h.get('level_value') or 0
    res_lv = (res_h.get('level_value') or 0) if res_h else 0

    gap = job_lv - res_lv
    if gap <= 0:
        base = 1.00
    elif gap == 1:
        base = 0.70
    elif gap == 2:
        base = 0.45
    else:
        base = 0.15

    if edu.get('matching_majors'):
        base = min(1.0, base + 0.08)

    return base


def _experience_graduated_score(exp: dict) -> float:
    """
    Smooth experience score — no cliff edge.

    Level gap (ordinal 0–6, where Entry=1 … Expert=6 per EXPERIENCE_PATTERNS):
      0  (meets/exceeds)    → 1.00
      1  (one level below)  → 0.75
      2                     → 0.50
      3                     → 0.30
      4+                    → 0.15
    No stated requirement   → 0.75 (neutral)
    """
    job_exp = exp.get('job_experience', {})
    res_exp = exp.get('resume_experience', {})

    job_lv = job_exp.get('level_value') or 0
    res_lv = res_exp.get('level_value') or 0

    if not job_lv:
        return 0.75  # no experience requirement stated

    gap = job_lv - res_lv
    if gap <= 0:
        return 1.00
    elif gap == 1:
        return 0.75
    elif gap == 2:
        return 0.50
    elif gap == 3:
        return 0.30
    else:
        return 0.15


def _compute_rank_score(analysis: dict, custom_weights: dict = None):
    """
    Composite ranking score (0–100) using similarity-weighted, graduated scoring.

    Section scores (all 0–1 before weighting):
      Skills        – weighted by JD skill importance; partial SBERT credit
      Duties        – mean cosine similarity across all JD responsibilities
      Education     – graduated 5-step scale (no cliff edge)
      Experience    – graduated scale (no cliff edge)
      Certifications – quality-weighted relevance; neutral 0.5 when JD doesn't require
      Projects      – average max-skill-similarity per project

    custom_weights (optional): dict with keys skills/responsibilities/education/
      experience/certifications/projects as raw numbers (any scale); they are
      normalised internally so they sum to 1.0.

    Weights (dynamic, used when custom_weights is None):
      Default            Skills 35%  Duties 25%  Edu 13%  Exp 10%  Cert  8%  Proj  9%
      Entry-level JD     Skills 35%  Duties 18%  Edu 15%  Exp  5%  Cert  5%  Proj 22%
      Cert-required JD   Skills 31%  Duties 25%  Edu 12%  Exp 10%  Cert 12%  Proj 10%
    """
    skill = analysis.get('skill_analysis', {})
    resp  = analysis.get('responsibility_analysis', {})
    edu   = analysis.get('education_analysis', {})
    exp   = analysis.get('experience_analysis', {})
    cert  = analysis.get('certification_analysis', {})
    proj  = analysis.get('project_analysis', {})

    # --- 1. Skills: JD-importance-weighted coverage with partial SBERT credit ---
    skill_score = skill.get(
        'weighted_effective_rate',
        skill.get('effective_match_rate', skill.get('match_rate', 0))
    ) / 100.0
    skill_score = max(0.0, min(1.0, skill_score))

    # --- 2. Responsibilities: mean cosine similarity across all JD duties ---
    mean_sim = resp.get('mean_similarity')
    if mean_sim is not None:
        resp_score = max(0.0, min(1.0, float(mean_sim)))
    else:
        resp_score = max(0.0, min(1.0,
            resp.get('effective_score', resp.get('score', 0)) / 100.0
        ))

    # --- 3. Education: graduated scale ---
    edu_score = _education_graduated_score(edu)

    # --- 4. Experience: graduated scale ---
    exp_score = _experience_graduated_score(exp)

    # --- 5. Certifications: quality-weighted, neutral when JD doesn't need them ---
    # When the JD doesn't require certs and the candidate has none, treat as
    # neutral (0.5) for the composite so they are not unfairly penalised.
    # The display score (quality_score) is always 0.0 in this case.
    cert_total = cert.get('total_certifications', 0)
    cert_jd_req = cert.get('jd_requires_certs', False)
    cert_raw = cert.get('quality_score')
    if cert_total == 0 and not cert_jd_req:
        cert_score = 0.5  # neutral: certs irrelevant for this JD
    elif cert_raw is not None:
        cert_score = max(0.0, min(1.0, float(cert_raw)))
    else:
        cert_score = max(0.0, min(1.0, cert.get('overall_match_score', 0) / 100.0))

    # --- 6. Projects: avg max-skill-similarity per project ---
    proj_raw = proj.get('quality_score')
    if proj_raw is not None:
        proj_score = max(0.0, min(1.0, float(proj_raw)))
    else:
        proj_score = max(0.0, min(1.0, proj.get('overall_match_score', 0) / 100.0))

    # --- Weight selection ---
    if custom_weights:
        raw = {
            'skills': float(custom_weights.get('skills', 35)),
            'resp':   float(custom_weights.get('responsibilities', 25)),
            'edu':    float(custom_weights.get('education', 13)),
            'exp':    float(custom_weights.get('experience', 10)),
            'cert':   float(custom_weights.get('certifications', 8)),
            'proj':   float(custom_weights.get('projects', 9)),
        }
        total = sum(raw.values()) or 1.0
        w = {k: v / total for k, v in raw.items()}
    else:
        job_lv = (exp.get('job_experience', {}) or {}).get('level_value') or 0
        cert_required = bool(cert.get('jd_requires_certs', False))

        if job_lv <= 1:
            w = {'skills': 0.35, 'resp': 0.18, 'edu': 0.15, 'exp': 0.05, 'cert': 0.05, 'proj': 0.22}
        elif cert_required:
            w = {'skills': 0.31, 'resp': 0.25, 'edu': 0.12, 'exp': 0.10, 'cert': 0.12, 'proj': 0.10}
        else:
            w = {'skills': 0.35, 'resp': 0.25, 'edu': 0.13, 'exp': 0.10, 'cert': 0.08, 'proj': 0.09}

    composite = (
        skill_score * w['skills'] +
        resp_score  * w['resp']   +
        edu_score   * w['edu']    +
        exp_score   * w['exp']    +
        cert_score  * w['cert']   +
        proj_score  * w['proj']
    )
    rank_score = round(composite * 100, 1)

    breakdown = {
        'skills':           round(skill_score * 100, 1),
        'responsibilities': round(resp_score * 100, 1),
        'education':        round(edu_score * 100, 1),
        'experience':       round(exp_score * 100, 1),
        'certifications':   round((float(cert_raw) if cert_raw is not None else 0.0) * 100, 1),
        'projects':         round(proj_score * 100, 1),
        'education_met':    bool(edu.get('meets_requirement', False)),
        'experience_met':   bool(exp.get('meets_requirement', False)),
        # Applied weights (as percentages, rounded) for UI transparency
        'weights': {
            'skills':           round(w['skills'] * 100, 1),
            'responsibilities': round(w['resp']   * 100, 1),
            'education':        round(w['edu']    * 100, 1),
            'experience':       round(w['exp']    * 100, 1),
            'certifications':   round(w['cert']   * 100, 1),
            'projects':         round(w['proj']   * 100, 1),
        },
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
        overview_data    = compare_overviews(jd_overview, resume_overview)
        overview_matches = overview_data["matches"]
        overview_f1      = overview_data["f1_score"]

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

        custom_weights = None
        weights_raw = request.data.get('weights')
        if weights_raw:
            try:
                custom_weights = json.loads(weights_raw)
            except (json.JSONDecodeError, TypeError):
                custom_weights = None

        full_analysis = {
            'skill_analysis': skill_serializer.validated_data,
            'responsibility_analysis': resp_serializer.validated_data,
            'education_analysis': edu_serializer.validated_data,
            'experience_analysis': exp_serializer.validated_data,
            'certification_analysis': certification_analysis,
            'project_analysis': project_analysis,
        }
        rank_score, breakdown = _compute_rank_score(full_analysis, custom_weights=custom_weights)

        return Response(
            {
                "categorized_resume": resume_serializer.validated_data,
                "similarity_scores": score_serializer.validated_data,
                "overview_matches": overview_serializer.validated_data,
                "overview_f1_score": overview_f1,
                "skill_analysis": skill_serializer.validated_data,
                "education_analysis": edu_serializer.validated_data,
                "experience_analysis": exp_serializer.validated_data,
                "responsibility_analysis": resp_serializer.validated_data,
                "certification_analysis": certification_analysis,
                "project_analysis": project_analysis,
                "rank_score": rank_score,
                "score_breakdown": breakdown,
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
        overview_data    = compare_overviews(
            job_description.get("overview", []),
            categorized_resume.get("overview", []),
        )
        overview_matches = overview_data["matches"]
        overview_f1      = overview_data["f1_score"]

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
            "overview_f1_score": overview_f1,
            "skill_analysis": skill_analysis,
            "education_analysis": education_analysis,
            "experience_analysis": experience_analysis,
            "responsibility_analysis": responsibility_analysis,
            "certification_analysis": certification_analysis,
            "project_analysis": project_analysis,
        }

        custom_weights = None
        weights_raw = request.data.get('weights')
        if weights_raw:
            try:
                custom_weights = json.loads(weights_raw)
            except (json.JSONDecodeError, TypeError):
                custom_weights = None

        rank_score, breakdown = _compute_rank_score(full_analysis, custom_weights=custom_weights)

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
