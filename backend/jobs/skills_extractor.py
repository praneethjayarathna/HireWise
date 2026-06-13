import re
import datetime
import threading
from typing import Dict, List, Set, Optional, Tuple

import numpy as np

from .model_loader import get_model as _get_model

# ---------------------------------------------------------------------------
# Module-level embedding caches
# ---------------------------------------------------------------------------
_skill_embeddings: Optional[np.ndarray] = None
_skill_labels: Optional[List[str]] = None
_skill_variants: Optional[Dict[str, List[str]]] = None

_edu_embeddings: Optional[np.ndarray] = None
_edu_labels: Optional[List[str]] = None
_edu_levels: Optional[Dict[str, int]] = None

_major_embeddings: Optional[np.ndarray] = None
_major_labels: Optional[List[str]] = None

_qual_embeddings: Optional[np.ndarray] = None
_qual_labels: Optional[List[str]] = None

_cert_embeddings: Optional[np.ndarray] = None
_cert_labels: Optional[List[str]] = None
_cert_variants: Optional[Dict[str, List[str]]] = None

_db_lock = threading.Lock()

SKILL_THRESHOLD = 0.55
MATCH_THRESHOLD = 0.70
EDU_THRESHOLD = 0.60

# ---------------------------------------------------------------------------
# Skill database
# ---------------------------------------------------------------------------

PROGRAMMING_LANGUAGES: Dict[str, List[str]] = {
    "Python": ["python", "python3", "python programming"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript", "ts"],
    "Java": ["java", "java ee", "java se"],
    "C++": ["c++", "cpp", "c plus plus"],
    "C#": ["c#", "csharp", "dot net", ".net"],
    "Go": ["go", "golang"],
    "Rust": ["rust"],
    "Ruby": ["ruby", "ruby language"],
    "PHP": ["php"],
    "Swift": ["swift", "swift ios"],
    "Kotlin": ["kotlin", "kotlin android"],
    "Scala": ["scala"],
    # "r" alone is too ambiguous — require explicit phrase
    "R": ["r programming", "r language", "rstudio", "r statistical"],
    "Dart": ["dart", "dart flutter"],
    "SQL": ["sql", "mysql", "postgresql", "plsql", "tsql", "sql query"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3", "stylesheet"],
    "Bash": ["bash", "shell scripting", "bash script"],
    "PowerShell": ["powershell", "ps1"],
    "YAML": ["yaml", "yml"],
    "JSON": ["json"],
    "XML": ["xml"],
    "GraphQL": ["graphql", "gql"],
    "MATLAB": ["matlab", "matlab programming"],
}

FRONTEND_FRAMEWORKS: Dict[str, List[str]] = {
    "React": ["react", "reactjs", "react.js", "react library"],
    "Vue": ["vue", "vuejs", "vue.js", "vue3"],
    "Angular": ["angular", "angularjs", "angular 2"],
    "Next.js": ["nextjs", "next.js", "next react"],
    "Svelte": ["svelte", "sveltejs"],
    "Nuxt": ["nuxt", "nuxtjs", "nuxt.js"],
    "Gatsby": ["gatsby", "gatsbyjs"],
    "Remix": ["remix", "remix.run"],
    "SvelteKit": ["sveltekit", "svelte kit"],
    "React Native": ["react native", "reactnative"],
    "Flutter": ["flutter"],
    "Electron": ["electron", "electronjs"],
}

BACKEND_FRAMEWORKS: Dict[str, List[str]] = {
    "Django": ["django", "django rest", "django rest framework", "drf"],
    "Flask": ["flask", "flask python"],
    "FastAPI": ["fastapi", "fast api"],
    "Express": ["express", "expressjs", "express.js", "node express"],
    "NestJS": ["nestjs", "nest.js", "nest framework"],
    "Spring": ["spring framework", "spring java"],
    "Spring Boot": ["spring boot", "springboot", "spring-boot"],
    "Rails": ["rails", "ruby on rails", "ror"],
    "Laravel": ["laravel", "laravel php"],
    "ASP.NET": ["asp.net", "asp.net core", ".net core", "dotnet core"],
    "FastAPI": ["fastapi", "fast api"],
    "Gin": ["gin go", "gin framework"],
    "Fiber": ["fiber go", "gofiber"],
    "Fastify": ["fastify"],
    "Hapi": ["hapijs", "hapi.js"],
    "Koa": ["koa", "koajs"],
    "Phoenix": ["phoenix elixir"],
    "Pyramid": ["pyramid framework"],
}

CSS_FRAMEWORKS: Dict[str, List[str]] = {
    "Tailwind": ["tailwind", "tailwindcss", "tailwind css"],
    "Bootstrap": ["bootstrap", "bs5"],
    "Material UI": ["material ui", "mui", "@mui"],
    "Ant Design": ["ant design", "antd"],
    "Chakra UI": ["chakra", "chakra ui"],
    "Styled Components": ["styled-components", "styled components"],
    "Sass": ["sass", "scss"],
    "Vuetify": ["vuetify"],
    "Quasar": ["quasar framework"],
}

DATABASES: Dict[str, List[str]] = {
    "PostgreSQL": ["postgresql", "postgres", "psql"],
    "MySQL": ["mysql", "mysql database"],
    "MongoDB": ["mongodb", "mongo", "mongo db"],
    "Redis": ["redis", "redis cache"],
    "Elasticsearch": ["elasticsearch", "elastic search", "elk"],
    "DynamoDB": ["dynamodb", "dynamo db", "aws dynamodb"],
    "SQLite": ["sqlite", "sqlite3"],
    "Oracle": ["oracle", "oracle db", "oracle database"],
    "SQL Server": ["sql server", "mssql", "ms sql"],
    "Cassandra": ["cassandra", "apache cassandra"],
    "Neo4j": ["neo4j", "neo4j graph"],
    "Firebase": ["firebase", "firebase realtime"],
    "Supabase": ["supabase"],
    "ClickHouse": ["clickhouse"],
    "InfluxDB": ["influxdb", "influx db"],
    "TimescaleDB": ["timescaledb"],
}

DEVOPS_CLOUD: Dict[str, List[str]] = {
    "Docker": ["docker", "docker container", "docker-compose", "docker compose"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Helm": ["helm", "helm chart"],
    "Terraform": ["terraform", "terraform iac"],
    "Ansible": ["ansible", "ansible automation"],
    "Jenkins": ["jenkins", "jenkins ci"],
    "GitLab CI": ["gitlab ci", "gitlab-runner"],
    "GitHub Actions": ["github actions", "gha", "github workflow"],
    "CircleCI": ["circleci"],
    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda aws"],
    "Azure": ["azure", "microsoft azure"],
    "GCP": ["gcp", "google cloud", "google cloud platform"],
    "Vercel": ["vercel"],
    "Netlify": ["netlify"],
    "Heroku": ["heroku"],
    "Nginx": ["nginx"],
    "Prometheus": ["prometheus"],
    "Grafana": ["grafana"],
    "Datadog": ["datadog"],
    "Sentry": ["sentry"],
    "Git": ["git", "github", "gitlab", "bitbucket", "version control"],
    "Linux": ["linux", "ubuntu", "centos", "debian"],
}

TESTING: Dict[str, List[str]] = {
    "Pytest": ["pytest", "unittest", "python test"],
    "Jest": ["jest", "jestjs"],
    "Mocha": ["mocha", "mochajs"],
    "Cypress": ["cypress", "cypress e2e"],
    "Playwright": ["playwright"],
    "Selenium": ["selenium", "selenium webdriver"],
    "JUnit": ["junit", "testng"],
    "Cucumber": ["cucumber", "gherkin", "bdd"],
}

AI_ML_FRAMEWORKS: Dict[str, List[str]] = {
    "TensorFlow": ["tensorflow", "tf", "tensorflow keras"],
    "PyTorch": ["pytorch", "torch", "pytorch lightning"],
    "Keras": ["keras", "keras api"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "Hugging Face": ["hugging face", "huggingface", "transformers", "hf transformers"],
    "XGBoost": ["xgboost", "xgb"],
    "LightGBM": ["lightgbm", "lgbm"],
    "CatBoost": ["catboost"],
    "OpenCV": ["opencv", "cv2", "open cv"],
    "NLTK": ["nltk", "natural language toolkit"],
    "spaCy": ["spacy", "spacy nlp"],
    "LangChain": ["langchain", "lang chain"],
    "OpenAI": ["openai", "gpt api", "openai api"],
    "ONNX": ["onnx", "onnx runtime"],
    "MLflow": ["mlflow", "ml flow"],
    "Ray": ["ray", "ray tune", "ray rllib"],
    "Weights & Biases": ["wandb", "weights and biases", "weights & biases"],
    "FastAI": ["fastai", "fast.ai"],
}

DATA_SCIENCE_LIBRARIES: Dict[str, List[str]] = {
    "pandas": ["pandas", "pd dataframe"],
    "NumPy": ["numpy", "np array", "numerical python"],
    "Matplotlib": ["matplotlib", "plt", "pyplot"],
    "Seaborn": ["seaborn", "sns"],
    "SciPy": ["scipy", "scientific python"],
    "Plotly": ["plotly", "plotly dash"],
    "Jupyter": ["jupyter", "jupyter notebook", "jupyter lab"],
    "Streamlit": ["streamlit"],
    "Dash": ["dash plotly", "plotly dash"],
    "Apache Spark": ["apache spark", "pyspark", "spark dataframe"],
    "Dask": ["dask", "dask dataframe"],
    "Polars": ["polars"],
    "Power BI": ["power bi", "powerbi", "ms power bi"],
    "Tableau": ["tableau"],
    "Apache Airflow": ["airflow", "apache airflow"],
    "dbt": ["dbt", "data build tool"],
}

MESSAGE_QUEUES: Dict[str, List[str]] = {
    "Apache Kafka": ["kafka", "apache kafka", "kafka streaming"],
    "RabbitMQ": ["rabbitmq", "rabbit mq"],
    "Celery": ["celery", "celery worker"],
    "AWS SQS": ["aws sqs", "sqs", "amazon sqs"],
    "Google Pub/Sub": ["google pubsub", "gcp pubsub", "pub/sub"],
    "Apache ActiveMQ": ["activemq", "apache activemq"],
    "NATS": ["nats", "nats messaging"],
    "ZeroMQ": ["zeromq", "zmq"],
    "Redis Streams": ["redis streams", "redis pub/sub"],
}

METHODOLOGIES: Dict[str, List[str]] = {
    "Agile": ["agile", "agile methodology", "agile development", "agile software"],
    "Scrum": ["scrum", "scrum methodology", "scrum framework"],
    "Kanban": ["kanban", "kanban board"],
    "SAFe": ["safe", "scaled agile", "scaled agile framework"],
    "DevOps": ["devops", "dev ops", "devops practices", "devops culture"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous delivery", "continuous deployment"],
    "TDD": ["tdd", "test driven development", "test-driven development"],
    "BDD": ["bdd", "behavior driven development", "behaviour driven development"],
    "Microservices": ["microservices", "microservice architecture", "micro services"],
    "REST API": ["rest api", "restful api", "rest services", "restful services", "restful"],
    "gRPC": ["grpc", "grpc api", "protocol buffers"],
    "GraphQL API": ["graphql api", "graphql endpoint"],
    "WebSocket": ["websocket", "web socket", "websockets"],
    "OAuth": ["oauth", "oauth2", "oauth 2.0"],
    "JWT": ["jwt", "json web token"],
    "System Design": ["system design", "distributed systems", "high availability", "scalable systems"],
    "Code Review": ["code review", "pull request", "peer review", "pr review"],
    "Version Control": ["version control", "git workflow", "branching strategy"],
    "OOP": ["object oriented", "oop", "object-oriented programming"],
    "Functional Programming": ["functional programming", "fp", "pure functions"],
}

ALL_SKILL_CATEGORIES: Dict[str, Dict[str, List[str]]] = {
    "Programming Languages": PROGRAMMING_LANGUAGES,
    "Frontend Frameworks": FRONTEND_FRAMEWORKS,
    "Backend Frameworks": BACKEND_FRAMEWORKS,
    "CSS Frameworks": CSS_FRAMEWORKS,
    "Databases": DATABASES,
    "DevOps & Cloud": DEVOPS_CLOUD,
    "Testing": TESTING,
    "AI/ML Frameworks": AI_ML_FRAMEWORKS,
    "Data Science Libraries": DATA_SCIENCE_LIBRARIES,
    "Message Queues": MESSAGE_QUEUES,
    "Methodologies & Practices": METHODOLOGIES,
}


# ---------------------------------------------------------------------------
# Skill extraction helpers
# ---------------------------------------------------------------------------

def _build_skill_database():
    global _skill_embeddings, _skill_labels, _skill_variants

    if _skill_embeddings is not None:
        return

    with _db_lock:
        if _skill_embeddings is not None:
            return

        model = _get_model()

        all_labels: List[str] = []
        all_variants: Dict[str, List[str]] = {}

        for category, skills in ALL_SKILL_CATEGORIES.items():
            for skill_name, variants in skills.items():
                for variant in variants:
                    normalized = variant.lower().strip()
                    all_labels.append(normalized)
                    if skill_name not in all_variants:
                        all_variants[skill_name] = []
                    all_variants[skill_name].append(normalized)

        _skill_labels = all_labels
        _skill_variants = all_variants
        _skill_embeddings = model.encode(all_labels, convert_to_numpy=True, show_progress_bar=False)


def _cosine_similarity_vec(a: np.ndarray, b: np.ndarray) -> float:
    a_norm = a / (np.linalg.norm(a) + 1e-10)
    b_norm = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a_norm, b_norm))


def _find_skills_in_text(text: str) -> Dict[str, float]:
    _build_skill_database()

    model = _get_model()
    text_lower = text.lower()

    sentences = re.split(r'[.!?\n]+', text_lower)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    if not sentences:
        sentences = [text_lower]

    text_embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)

    skill_scores: Dict[str, float] = {}

    for idx, skill_lower in enumerate(_skill_labels):
        skill_emb = _skill_embeddings[idx]
        similarities = text_embeddings @ skill_emb
        max_sim = float(np.max(similarities))

        if max_sim >= SKILL_THRESHOLD:
            for skill_name, variants in _skill_variants.items():
                if skill_lower in variants and skill_name not in skill_scores:
                    skill_scores[skill_name] = max_sim
                elif skill_lower in variants:
                    skill_scores[skill_name] = max(skill_scores[skill_name], max_sim)

    return skill_scores


def _semantic_skill_match(
    job_skills: Dict[str, float],
    resume_skills: Dict[str, float]
) -> Tuple[List[str], List[str], Dict[str, str]]:
    model = _get_model()

    job_skill_list = list(job_skills.keys())
    resume_skill_list = list(resume_skills.keys())

    if not job_skill_list or not resume_skill_list:
        return [], list(job_skills.keys()), {}

    job_embeddings = model.encode(job_skill_list, convert_to_numpy=True, show_progress_bar=False)
    resume_embeddings = model.encode(resume_skill_list, convert_to_numpy=True, show_progress_bar=False)

    j_norm = job_embeddings / (np.linalg.norm(job_embeddings, axis=1, keepdims=True) + 1e-10)
    r_norm = resume_embeddings / (np.linalg.norm(resume_embeddings, axis=1, keepdims=True) + 1e-10)
    similarity_matrix = j_norm @ r_norm.T

    matched = []
    missing = []
    variations: Dict[str, str] = {}

    matched_indices = set()
    for i, job_skill in enumerate(job_skill_list):
        best_j = int(np.argmax(similarity_matrix[i]))
        best_sim = float(similarity_matrix[i, best_j])

        if best_j not in matched_indices and best_sim >= MATCH_THRESHOLD:
            matched.append(resume_skill_list[best_j])
            matched_indices.add(best_j)
            if resume_skill_list[best_j] != job_skill:
                variations[job_skill] = resume_skill_list[best_j]
        else:
            # Try next best not already matched
            found = False
            order = np.argsort(similarity_matrix[i])[::-1]
            for j in order:
                if j not in matched_indices and similarity_matrix[i, j] >= MATCH_THRESHOLD:
                    matched.append(resume_skill_list[j])
                    matched_indices.add(j)
                    if resume_skill_list[j] != job_skill:
                        variations[job_skill] = resume_skill_list[j]
                    found = True
                    break
            if not found:
                missing.append(job_skill)

    return matched, missing, variations


def extract_skills_with_scores(text: str) -> Dict[str, Dict[str, float]]:
    text_lower = text.lower()
    text_normalized = re.sub(r'[^a-z0-9\s\.\-\+\#/]', ' ', text_lower)
    text_normalized = re.sub(r'\s+', ' ', text_normalized)

    result: Dict[str, Dict[str, float]] = {}
    for category in ALL_SKILL_CATEGORIES:
        result[category] = {}

    for category, skills in ALL_SKILL_CATEGORIES.items():
        for skill_name, variants in skills.items():
            for variant in variants:
                pattern = r'\b' + re.escape(variant.lower()) + r'\b'
                if re.search(pattern, text_normalized):
                    result[category][skill_name] = 0.90
                    break

    return {cat: skills for cat, skills in result.items() if skills}


def extract_skills(text: str) -> Dict[str, List[str]]:
    skills_with_scores = extract_skills_with_scores(text)
    result: Dict[str, List[str]] = {}
    for category, scores in skills_with_scores.items():
        result[category] = sorted(scores.keys())
    return result


def extract_all_skills(text: str) -> List[str]:
    skills_with_scores = extract_skills_with_scores(text)
    all_skills = []
    for category, scores in skills_with_scores.items():
        all_skills.extend(sorted(scores.keys()))
    return all_skills


# ---------------------------------------------------------------------------
# Certification → skill mapping (predefined, IT-domain only)
# ---------------------------------------------------------------------------

CERT_SKILL_MAPPING: Dict[str, List[str]] = {
    "AWS Certified Solutions Architect": [
        "AWS", "EC2", "S3", "IAM", "VPC", "CloudFormation", "Lambda", "RDS", "System Design",
    ],
    "AWS Certified Developer": [
        "AWS", "Lambda", "DynamoDB", "S3", "API Gateway", "CloudWatch", "Python", "REST API",
    ],
    "AWS Certified SysOps Administrator": [
        "AWS", "EC2", "CloudFormation", "CloudWatch", "IAM", "Linux",
    ],
    "AWS Certified DevOps Engineer": [
        "AWS", "Docker", "Kubernetes", "CI/CD", "Jenkins", "CloudFormation", "DevOps",
    ],
    "AWS Certified Machine Learning": [
        "AWS", "Python", "TensorFlow", "scikit-learn", "Machine Learning", "Data Science Libraries",
    ],
    "Google Cloud Professional Architect": [
        "GCP", "Kubernetes", "System Design", "Cloud Computing",
    ],
    "Google Cloud Professional Data Engineer": [
        "GCP", "Apache Spark", "TensorFlow", "Python", "pandas", "Apache Airflow",
    ],
    "Google Cloud Associate Cloud Engineer": [
        "GCP", "Kubernetes", "Docker", "Linux",
    ],
    "Microsoft Azure Fundamentals": [
        "Azure",
    ],
    "Microsoft Azure Administrator": [
        "Azure", "PowerShell", "Linux",
    ],
    "Microsoft Azure Solutions Architect": [
        "Azure", "System Design", "Cloud Computing",
    ],
    "Certified Kubernetes Administrator": [
        "Kubernetes", "Docker", "Linux", "CI/CD", "Helm",
    ],
    "Certified Kubernetes Application Developer": [
        "Kubernetes", "Docker", "Go", "Python",
    ],
    "Terraform Associate": [
        "Terraform", "AWS", "Azure", "GCP", "DevOps", "CI/CD",
    ],
    "CISSP": [
        "Cybersecurity", "OAuth", "JWT",
    ],
    "CompTIA Security+": [
        "Cybersecurity",
    ],
    "CompTIA Network+": [
        "Networking",
    ],
    "Cisco CCNA": [
        "Networking",
    ],
    "PMP": [
        "Agile", "Scrum",
    ],
    "Certified ScrumMaster": [
        "Scrum", "Agile", "Kanban",
    ],
    "Tableau Certified Data Analyst": [
        "Tableau",
    ],
    "PowerBI Data Analyst": [
        "Power BI",
    ],
    "TensorFlow Developer Certificate": [
        "TensorFlow", "Python", "scikit-learn", "Deep Learning",
    ],
    "Deep Learning Specialization": [
        "TensorFlow", "PyTorch", "Python", "scikit-learn", "Deep Learning", "Machine Learning",
    ],
    "MongoDB University": [
        "MongoDB",
    ],
    "Oracle Certified Professional": [
        "Oracle", "SQL", "Java",
    ],
}


def _get_implied_skills_from_certs(certifications: List[Dict[str, any]]) -> Dict[str, Set[str]]:
    """
    Return {cert_name: {skill, ...}} for each certification.

    For known certs uses CERT_SKILL_MAPPING.  For unknown certs, falls back to
    running the keyword skill extractor on the certification name itself
    (e.g. 'Google TensorFlow Developer Certificate' → TensorFlow, Python).
    """
    result: Dict[str, Set[str]] = {}
    for cert in certifications:
        name = cert.get("certification", "")
        if not name:
            continue
        if name in CERT_SKILL_MAPPING:
            result[name] = set(CERT_SKILL_MAPPING[name])
        else:
            # Mine skills from the cert name text
            mined = extract_skills_with_scores(name)
            implied = {skill for cat in mined.values() for skill in cat}
            if implied:
                result[name] = implied
    return result


def compare_skills(
    job_text: str,
    resume_text: str,
    projects: Optional[List[Dict[str, any]]] = None,
    certifications: Optional[List[Dict[str, any]]] = None,
) -> Dict[str, any]:
    """
    Skill comparison enriched with project and certification evidence.

    Direct skills (from resume text) are matched first.
    Skills discovered in project descriptions and implied by certifications
    fill in additional coverage for skills not listed in the skills section.

    Returns
    -------
    dict with:
      matching_skills          – directly matched from resume text
      missing_skills           – not found through any source
      skill_variations         – semantic name variations (e.g. sklearn ↔ scikit-learn)
      skills_from_projects     – job skills covered by project descriptions
      skills_from_certifications – job skills covered by cert implications
      job_skills_count
      resume_skills_count
      match_rate               – direct-evidence match rate (%)
      effective_match_rate     – total coverage including projects & certs (%)
    """
    job_skills = extract_skills_with_scores(job_text)
    resume_skills_direct = extract_skills_with_scores(resume_text)

    job_flat: Dict[str, float] = {
        name: score for cat in job_skills.values() for name, score in cat.items()
    }
    resume_flat: Dict[str, float] = {
        name: score for cat in resume_skills_direct.values() for name, score in cat.items()
    }

    # --- Layer 1: direct skill matching ---
    exact_match = set(job_flat) & set(resume_flat)
    semantic_match, still_missing, variations = _semantic_skill_match(job_flat, resume_flat)
    direct_matched: Set[str] = set(exact_match) | set(semantic_match)
    direct_missing: Set[str] = set(still_missing) - set(semantic_match)

    # --- Layer 2: skills from project descriptions ---
    project_skill_names: Set[str] = set()
    if projects:
        project_text = " ".join(
            f"{p.get('project_title', '')} {p.get('description', '')}"
            for p in projects
        )
        if project_text.strip():
            proj_skills = extract_skills_with_scores(project_text)
            proj_flat = {name for cat in proj_skills.values() for name in cat}
            # Only count skills that are in the JD AND not already directly matched
            project_skill_names = (direct_missing & proj_flat) | _semantic_overlap(
                direct_missing, proj_flat
            )

    # --- Layer 3: skills implied by certifications ---
    cert_skill_names: Set[str] = set()
    if certifications:
        cert_implied = _get_implied_skills_from_certs(certifications)
        all_implied: Set[str] = set()
        for skills in cert_implied.values():
            all_implied |= skills
        # Only count skills that are in the JD AND not already covered
        remaining = direct_missing - project_skill_names
        cert_skill_names = (remaining & all_implied) | _semantic_overlap(
            remaining, all_implied
        )

    # Build final answer
    all_matched = sorted(direct_matched | project_skill_names | cert_skill_names)
    all_missing = sorted(direct_missing - project_skill_names - cert_skill_names)

    return {
        "matching_skills": sorted(direct_matched),
        "missing_skills": all_missing,
        "skill_variations": variations,
        "skills_from_projects": sorted(project_skill_names),
        "skills_from_certifications": sorted(cert_skill_names),
        "job_skills_count": len(job_flat),
        "resume_skills_count": len(resume_flat),
        "match_rate": round(len(direct_matched) / len(job_flat) * 100, 1) if job_flat else 0,
        "effective_match_rate": round(len(all_matched) / len(job_flat) * 100, 1) if job_flat else 0,
    }


def _semantic_overlap(job_missing: Set[str], candidate_skills: Set[str]) -> Set[str]:
    """
    Return the subset of *job_missing* skills that are semantically covered
    by *candidate_skills* (threshold MATCH_THRESHOLD).
    Only called when the two sets don't overlap exactly.
    """
    if not job_missing or not candidate_skills:
        return set()
    model = _get_model()
    jm_list = list(job_missing)
    cs_list = list(candidate_skills)
    jm_embs = model.encode(jm_list, convert_to_numpy=True, show_progress_bar=False)
    cs_embs = model.encode(cs_list, convert_to_numpy=True, show_progress_bar=False)
    jm_norm = jm_embs / (np.linalg.norm(jm_embs, axis=1, keepdims=True) + 1e-10)
    cs_norm = cs_embs / (np.linalg.norm(cs_embs, axis=1, keepdims=True) + 1e-10)
    sim = jm_norm @ cs_norm.T   # (n_missing, n_candidates)
    covered: Set[str] = set()
    for i, skill in enumerate(jm_list):
        if float(sim[i].max()) >= MATCH_THRESHOLD:
            covered.add(skill)
    return covered


# ---------------------------------------------------------------------------
# Education extraction
# ---------------------------------------------------------------------------

EDUCATION_LEVELS: Dict[str, int] = {
    "Certificate": 1,
    "Associate": 2,
    "Bachelor's": 3,
    "Master's": 4,
    "PhD": 5,
}

EDUCATION_LEVEL_PATTERNS: Dict[str, List[str]] = {
    "PhD": [
        "phd", "ph.d", "ph d", "doctor of philosophy", "doctorate",
        "doctoral", "phd degree", "doctorate degree", "phd in",
        "philosophy doctorate", "d.phil", "doctor of science", "d.sc",
    ],
    "Master's": [
        "master", "master's", "masters", "master's degree", "ms", "m.s",
        "m.sc", "mba", "msc", "ma", "m.a",
        "master of science", "master of arts", "master of business",
        "master of computer applications", "mca", "master degree",
        "postgraduate", "post graduate", "mtech", "m.tech", "m.eng",
        "ms in", "master's in",
    ],
    "Bachelor's": [
        "bachelor", "bachelor's", "bachelors", "bachelor's degree",
        "bs", "b.s", "bsc", "bs degree",
        "b.e", "be", "b tech", "btech", "b.tech", "bachelor of engineering",
        "bachelor of science", "bachelor of arts", "ba", "b.a",
        "undergraduate", "ug degree", "bs in", "bachelor's in", "b.sc",
        "engineering degree",
    ],
    "Associate": [
        "associate", "associate's", "associate degree",
        "associate of science", "associate of arts",
        "advanced diploma", "higher diploma", "diploma in",
    ],
    "Certificate": [
        "certificate", "certification", "certified", "certificate course",
        "professional certificate", "nanodegree",
    ],
}

MAJOR_PATTERNS: Dict[str, List[str]] = {
    "Computer Science": [
        "computer science", "cs", "computing", "computational science",
        "computer science and engineering",
    ],
    "Software Engineering": [
        "software engineering", "software development", "software systems",
        "software technology",
    ],
    "Information Technology": [
        "information technology", "it", "information systems",
        "information technology management",
    ],
    "Data Science": [
        "data science", "data analytics", "data engineering",
        "data analysis", "big data",
    ],
    "Artificial Intelligence": [
        "artificial intelligence", "machine learning", "deep learning",
        "neural networks", "natural language processing", "computer vision",
        "ai ml", "intelligent systems",
    ],
    "Electrical Engineering": [
        "electrical engineering", "electronics", "electronic engineering",
        "electronics and communication", "ece", "electrical and electronics",
    ],
    "Mathematics": [
        "mathematics", "maths", "applied mathematics", "statistics",
        "mathematical sciences",
    ],
    "Cybersecurity": [
        "cyber security", "cybersecurity", "information security",
        "network security",
    ],
    "Cloud Computing": [
        "cloud computing", "cloud architecture", "cloud engineering",
        "cloud infrastructure",
    ],
    "Web Development": [
        "web development", "web engineering", "frontend engineering",
        "backend engineering", "full stack development",
    ],
    "Mobile Development": [
        "mobile development", "mobile engineering", "ios development",
        "android development",
    ],
    "Networking": [
        "networking", "computer networks", "network engineering",
        "telecommunications",
    ],
    "Database": [
        "database", "database management", "database systems", "dbms",
    ],
}

QUALIFICATION_TYPE_PATTERNS: Dict[str, List[str]] = {
    "Bachelor of Science": [
        "bachelor of science", "b.sc", "bsc", "bs", "b.s",
    ],
    "Bachelor of Engineering": [
        "bachelor of engineering", "b.e", "be", "bachelor of technology",
        "b.tech", "btech",
    ],
    "Bachelor of Arts": [
        "bachelor of arts", "b.a", "ba",
    ],
    "Master of Science": [
        "master of science", "m.sc", "msc", "ms", "m.s",
    ],
    "Master of Engineering": [
        "master of engineering", "m.e", "m.eng", "master of technology",
        "m.tech",
    ],
    "Master of Arts": [
        "master of arts", "m.a", "ma",
    ],
    "Master of Business Administration": [
        "master of business administration", "mba",
    ],
    "Doctor of Philosophy": [
        "doctor of philosophy", "phd", "ph.d", "doctorate",
    ],
}


def _build_education_semantic_db():
    global _edu_embeddings, _edu_labels, _edu_levels
    global _major_embeddings, _major_labels
    global _qual_embeddings, _qual_labels

    if _edu_embeddings is not None:
        return

    with _db_lock:
        if _edu_embeddings is not None:
            return

        model = _get_model()

        edu_labels = []
        for edu_type, variants in EDUCATION_LEVEL_PATTERNS.items():
            for variant in variants:
                edu_labels.append(variant.lower().strip())
        _edu_labels = edu_labels
        _edu_levels = EDUCATION_LEVELS
        _edu_embeddings = model.encode(edu_labels, convert_to_numpy=True, show_progress_bar=False)

        major_labels = []
        for major, variants in MAJOR_PATTERNS.items():
            for variant in variants:
                major_labels.append(variant.lower().strip())
        _major_labels = major_labels
        _major_embeddings = model.encode(major_labels, convert_to_numpy=True, show_progress_bar=False)

        qual_labels = []
        for qual, variants in QUALIFICATION_TYPE_PATTERNS.items():
            for variant in variants:
                qual_labels.append(variant.lower().strip())
        _qual_labels = qual_labels
        _qual_embeddings = model.encode(qual_labels, convert_to_numpy=True, show_progress_bar=False)


def extract_education(text: str) -> Dict[str, List[Dict[str, any]]]:
    """
    Proximity-aware education extraction.

    For each sentence that contains an education level keyword, look for a
    matching major and qualification type within the same sentence and its
    immediate neighbours.  This prevents incorrectly assigning the same major
    to every detected degree level.
    """
    _build_education_semantic_db()

    text_clean = text.replace("\r\n", "\n").replace("\r", "\n")
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', text_clean) if len(s.strip()) > 5]

    result: Dict[str, List[Dict[str, any]]] = {edu_type: [] for edu_type in EDUCATION_LEVEL_PATTERNS}
    seen_entries: Set[Tuple[str, Optional[str]]] = set()

    for i, sent in enumerate(sentences):
        sent_lower = sent.lower()

        # Find the highest education level mentioned in this sentence
        found_level: Optional[str] = None
        for edu_type, variants in EDUCATION_LEVEL_PATTERNS.items():
            for variant in variants:
                if re.search(r'\b' + re.escape(variant) + r'\b', sent_lower):
                    current_val = EDUCATION_LEVELS.get(found_level, 0) if found_level else 0
                    if EDUCATION_LEVELS.get(edu_type, 0) > current_val:
                        found_level = edu_type
                    break

        if found_level is None:
            continue

        # Build context window: current sentence + neighbours
        window_sentences = sentences[max(0, i - 1): min(len(sentences), i + 2)]
        context_window = " ".join(window_sentences).lower()

        # Find major within the context window
        found_major: Optional[str] = None
        for major, variants in MAJOR_PATTERNS.items():
            for variant in variants:
                if re.search(r'\b' + re.escape(variant) + r'\b', context_window):
                    found_major = major
                    break
            if found_major:
                break

        # Find qualification type within the current sentence
        found_qual: Optional[str] = None
        for qual_type, variants in QUALIFICATION_TYPE_PATTERNS.items():
            for variant in variants:
                if re.search(r'\b' + re.escape(variant) + r'\b', sent_lower):
                    found_qual = qual_type
                    break
            if found_qual:
                break

        entry_key = (found_level, found_major)
        if entry_key in seen_entries:
            continue
        seen_entries.add(entry_key)

        full_qual = (
            f"{found_qual} in {found_major}" if found_major and found_qual
            else found_qual or found_level
        )

        entry = {
            "type": found_level,
            "level": found_level,
            "level_value": EDUCATION_LEVELS.get(found_level, 0),
            "major": found_major,
            "qualification_type": found_qual,
            "full_qualification": full_qual,
            "confidence": 1.0,
            "context": sent.strip()[:200],
        }
        result[found_level].append(entry)

    return {edu_type: items for edu_type, items in result.items() if items}


def get_highest_education(education_data: Dict[str, List[Dict[str, any]]]) -> Optional[Dict[str, any]]:
    if not education_data:
        return None

    highest = None
    highest_level = 0

    for edu_type, items in education_data.items():
        for item in items:
            level_val = item.get("level_value") or EDUCATION_LEVELS.get(item.get("level")) or 0
            if level_val > highest_level:
                highest_level = level_val
                highest = item

    return highest


def meets_requirement(
    job_education: Dict[str, List[Dict[str, any]]],
    resume_education: Dict[str, List[Dict[str, any]]]
) -> Dict[str, any]:
    job_highest = get_highest_education(job_education)
    resume_highest = get_highest_education(resume_education)

    if not job_highest:
        return {
            "meets_requirement": True,
            "job_requirement": None,
            "resume_qualification": resume_highest,
            "message": "No specific education requirement found in job description",
        }

    if not resume_highest:
        return {
            "meets_requirement": False,
            "job_requirement": job_highest,
            "resume_qualification": None,
            "message": "No education qualifications found in resume",
        }

    job_level = job_highest.get("level_value") or EDUCATION_LEVELS.get(job_highest.get("level")) or 0
    resume_level = resume_highest.get("level_value") or EDUCATION_LEVELS.get(resume_highest.get("level")) or 0

    meets = resume_level >= job_level

    return {
        "meets_requirement": meets,
        "job_requirement": job_highest,
        "resume_qualification": resume_highest,
        "message": "Resume meets education requirement" if meets else "Resume education level is below requirement",
    }


def compare_education(job_text: str, resume_text: str) -> Dict[str, any]:
    job_education = extract_education(job_text)
    resume_education = extract_education(resume_text)

    def _flatten(edu_dict):
        return [
            {
                "type": edu_type,
                "level": item.get("level"),
                "level_value": item.get("level_value"),
                "major": item.get("major"),
                "qualification_type": item.get("qualification_type"),
                "context": item.get("context"),
                "confidence": item.get("confidence"),
            }
            for edu_type, items in edu_dict.items()
            for item in items
        ]

    job_flat = _flatten(job_education)
    resume_flat = _flatten(resume_education)

    requirement_check = meets_requirement(job_education, resume_education)

    return {
        "job_education": job_flat,
        "resume_education": resume_flat,
        "job_highest": get_highest_education(job_education),
        "resume_highest": get_highest_education(resume_education),
        "meets_requirement": requirement_check["meets_requirement"],
        "meets_requirement_message": requirement_check["message"],
        "job_majors": list({item.get("major") for item in job_flat if item.get("major")}),
        "resume_majors": list({item.get("major") for item in resume_flat if item.get("major")}),
        "matching_majors": list(
            {item.get("major") for item in job_flat if item.get("major")}
            & {item.get("major") for item in resume_flat if item.get("major")}
        ),
    }


# ---------------------------------------------------------------------------
# Experience extraction
# ---------------------------------------------------------------------------

EXPERIENCE_PATTERNS: Dict[str, List[str]] = {
    "Entry Level (0-1 years)": [
        "0-1 years", "0 to 1 year", "1 year", "0 years", "fresh graduate",
        "new graduate", "no experience required", "entry level", "fresher",
    ],
    "Junior (1-2 years)": [
        "1-2 years", "1 to 2 years", "2 years", "1 year minimum",
        "one year", "one to two years", "1+ year", "1+ years",
    ],
    "Mid-Level (2-3 years)": [
        "2-3 years", "2 to 3 years", "3 years", "2 years minimum",
        "two year", "two to three years", "2+ year", "2+ years",
        "mid level", "mid-level", "intermediate",
    ],
    "Senior (3-5 years)": [
        "3-5 years", "3 to 5 years", "5 years", "3 years minimum",
        "three year", "three to five years", "3+ year", "3+ years", "4 years",
        "senior", "senior level", "3-4 years",
    ],
    "Lead (5-7 years)": [
        "5-7 years", "5 to 7 years", "7 years", "5 years minimum",
        "five year", "five to seven years", "5+ year", "5+ years", "6 years",
        "lead", "lead level", "team lead",
    ],
    "Principal (7-10 years)": [
        "7-10 years", "7 to 10 years", "10 years", "7 years minimum",
        "seven year", "seven to ten years", "7+ year", "7+ years",
        "principal", "principal level", "8 years", "9 years",
    ],
    "Expert (10+ years)": [
        "10+ years", "10 years plus", "more than 10 years", "10-12 years",
        "expert", "expert level", "staff engineer",
        "10 years minimum", "10+", "ten plus years",
    ],
}

EXPERIENCE_LEVELS: Dict[str, int] = {
    "Entry Level (0-1 years)": 1,
    "Junior (1-2 years)": 2,
    "Mid-Level (2-3 years)": 3,
    "Senior (3-5 years)": 4,
    "Lead (5-7 years)": 5,
    "Principal (7-10 years)": 6,
    "Expert (10+ years)": 7,
}

_MONTHS_MAP = {
    'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
    'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
    'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
    'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
    'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
    'dec': 12, 'december': 12,
}

_MONTH_RE = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
_SEP_RE = r'\s*[-–—]\s*'
_PRESENT_RE = r'(?:present|current|now|till date|to date)'


def _years_from_level(years: float) -> str:
    if years >= 10:
        return "Expert (10+ years)"
    if years >= 7:
        return "Principal (7-10 years)"
    if years >= 5:
        return "Lead (5-7 years)"
    if years >= 3:
        return "Senior (3-5 years)"
    if years >= 2:
        return "Mid-Level (2-3 years)"
    if years >= 1:
        return "Junior (1-2 years)"
    return "Entry Level (0-1 years)"


def _extract_experience_from_dates(text: str) -> Optional[Dict[str, any]]:
    """
    Calculate total work experience from employment date ranges found in the text.

    Handles formats such as:
      • "Jan 2019 – Mar 2023"
      • "2019 – 2023"
      • "March 2020 - Present"
      • "2018 to present"
    """
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    text_lower = text.lower()
    total_months = 0
    ranges_found: List[str] = []
    seen_starts: Set[Tuple[int, int]] = set()

    # Pattern 1: "Mon YYYY – Mon YYYY" or "Mon YYYY – Present"
    full_pattern = re.compile(
        rf'({_MONTH_RE})\s+(\d{{4}})\s*[-–—]\s*'
        rf'(?:({_MONTH_RE})\s+(\d{{4}})|({_PRESENT_RE}))',
        re.IGNORECASE,
    )
    for m in full_pattern.finditer(text_lower):
        start_mon = _MONTHS_MAP.get(m.group(1)[:3].lower(), 1)
        start_yr = int(m.group(2))
        if m.group(5):  # present
            end_mon, end_yr = current_month, current_year
        else:
            end_mon = _MONTHS_MAP.get(m.group(3)[:3].lower(), 12)
            end_yr = int(m.group(4))

        if not (1970 <= start_yr <= current_year and start_yr <= end_yr <= current_year + 1):
            continue
        key = (start_yr, start_mon)
        if key in seen_starts:
            continue
        seen_starts.add(key)
        diff = (end_yr - start_yr) * 12 + (end_mon - start_mon)
        total_months += max(0, diff)
        ranges_found.append(m.group(0))

    # Pattern 2: "YYYY – YYYY"
    year_range_re = re.compile(r'\b(\d{4})\s*[-–—]\s*(\d{4})\b')
    for m in year_range_re.finditer(text_lower):
        sy, ey = int(m.group(1)), int(m.group(2))
        if not (1970 <= sy <= current_year and sy < ey <= current_year + 1):
            continue
        if ey - sy > 50:
            continue
        key = (sy, 1)
        if key in seen_starts:
            continue
        seen_starts.add(key)
        total_months += (ey - sy) * 12
        ranges_found.append(m.group(0))

    # Pattern 3: "YYYY – Present" / "YYYY to present"
    year_present_re = re.compile(
        rf'\b(\d{{4}})\s*(?:[-–—]|to)\s*{_PRESENT_RE}',
        re.IGNORECASE,
    )
    for m in year_present_re.finditer(text_lower):
        sy = int(m.group(1))
        if not (1970 <= sy <= current_year):
            continue
        key = (sy, 1)
        if key in seen_starts:
            continue
        seen_starts.add(key)
        total_months += (current_year - sy) * 12
        ranges_found.append(m.group(0))

    if not ranges_found or total_months <= 0:
        return None

    total_years = round(total_months / 12, 1)
    type_name = _years_from_level(total_years)

    return {
        "required_years": total_years,
        "years_text": f"{total_years} years (from date ranges)",
        "level": type_name,
        "level_value": EXPERIENCE_LEVELS[type_name],
        "context": f"Date ranges found: {', '.join(ranges_found[:5])}",
    }


def _extract_experience_years(text: str) -> Dict[str, List[Dict[str, any]]]:
    text_lower = text.lower()

    title_words = {'senior', 'junior', 'lead', 'principal', 'staff', 'manager', 'director', 'head', 'chief', 'intern', 'associate'}
    context_exclude_patterns = [
        r'\bsenior\s+(software|engineer|developer|analyst|designer|architect|consultant|manager)',
        r'\bjunior\s+(software|engineer|developer|analyst|designer)',
        r'\blead\s+(software|engineer|developer|analyst|designer|manager)',
        r'\bprincipal\s+(software|engineer|developer|architect|analyst)',
        r'\bstaff\s+(software|engineer|developer|analyst)',
        r'\bsenior\s+(lecturer|professor|teacher|researcher)',
        r'\breferences?\s*[:|-]',
    ]

    found: Dict[str, List[Dict[str, any]]] = {exp_type: [] for exp_type in EXPERIENCE_PATTERNS}

    for exp_type, variants in EXPERIENCE_PATTERNS.items():
        for variant in variants:
            pattern = r'\b' + re.escape(variant.lower()) + r'\b'
            for match in re.finditer(pattern, text_lower):
                ctx_start = max(0, match.start() - 80)
                ctx_end = min(len(text_lower), match.end() + 80)
                context = text_lower[ctx_start:ctx_end].strip()

                is_title_context = any(
                    re.search(ep, context, re.IGNORECASE) for ep in context_exclude_patterns
                )
                if variant.lower() in title_words and is_title_context:
                    continue

                found[exp_type].append({
                    "type": exp_type,
                    "years": exp_type.split()[1].strip('()') if len(exp_type.split()) > 1 else exp_type,
                    "level": EXPERIENCE_LEVELS[exp_type],
                    "variant": variant,
                    "context": context,
                    "confidence": 0.5,
                })

    return {exp_type: items for exp_type, items in found.items() if items}


def _extract_years_numbers(text: str) -> List[Dict[str, any]]:
    text_lower = text.lower()

    years_patterns = [
        (r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp|professional)', 'explicit_years'),
        (r'(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs?)', 'range_years'),
        (r'(?:minimum|min)\s*(\d+)\s*(?:years?|yrs?)', 'min_years'),
        (r'(?:at least|atleast)\s*(\d+)\s*(?:years?|yrs?)', 'atleast_years'),
        (r'(?:over|more than)\s*(\d+)\s*(?:years?|yrs?)', 'over_years'),
        (r'(\d+)\s*\+\s*(?:years?|yrs?)', 'plus_years'),
    ]

    found = []
    seen_years: Set[int] = set()

    for pattern, match_type in years_patterns:
        for match in re.finditer(pattern, text_lower):
            years = int(match.group(2)) if match_type == 'range_years' else int(match.group(1))
            if years in seen_years:
                continue
            seen_years.add(years)

            type_name = _years_from_level(years)

            ctx_start = max(0, match.start() - 50)
            ctx_end = min(len(text_lower), match.end() + 50)

            found.append({
                "type": type_name,
                "years": years,
                "level": EXPERIENCE_LEVELS[type_name],
                "variant": match.group(0),
                "context": text_lower[ctx_start:ctx_end].strip(),
                "confidence": 0.98,
            })

    return found


def extract_experience_requirement(text: str) -> Dict[str, any]:
    """Extract experience requirement from a job description (keyword/number based)."""
    number_results = _extract_years_numbers(text)

    # Pick the highest explicitly stated numeric requirement
    numeric_years = 0
    numeric_result = None
    for item in number_results:
        years_val = item.get("years", 0)
        try:
            years = int(years_val)
        except (ValueError, TypeError):
            years = 0
        if years > numeric_years:
            numeric_years = years
            numeric_result = item

    if numeric_result:
        return {
            "required_years": numeric_result["years"],
            "years_text": numeric_result["type"],
            "level": numeric_result["type"],
            "level_value": numeric_result["level"],
            "context": numeric_result["context"],
        }

    # Fall back to pattern matching (handles words like "senior", "junior")
    pattern_results = _extract_experience_years(text)
    highest = None
    highest_level = 0
    for exp_type, items in pattern_results.items():
        for item in items:
            if item.get("level", 0) > highest_level:
                highest_level = item["level"]
                highest = item

    if not highest:
        return {
            "required_years": None,
            "years_text": None,
            "level": None,
            "level_value": None,
            "context": None,
        }

    return {
        "required_years": highest.get("years"),
        "years_text": highest.get("type"),
        "level": highest.get("type"),
        "level_value": highest.get("level"),
        "context": highest.get("context"),
    }


def extract_experience_from_resume(text: str) -> Dict[str, any]:
    """
    Extract total experience from a resume.

    Prefers date-range calculation (e.g. '2019-2023') over keyword matching,
    because resumes contain work history dates rather than phrases like
    '5+ years of experience'.
    """
    date_result = _extract_experience_from_dates(text)
    if date_result:
        return date_result

    # Fallback: look for explicit year statements
    return extract_experience_requirement(text)


def compare_experience(job_text: str, resume_text: str) -> Dict[str, any]:
    job_exp = extract_experience_requirement(job_text)
    resume_exp = extract_experience_from_resume(resume_text)

    job_level = job_exp.get("level_value") or 0
    resume_level = resume_exp.get("level_value") or 0

    meets = resume_level >= job_level if job_exp.get("level_value") else True

    return {
        "job_experience": job_exp,
        "resume_experience": resume_exp,
        "meets_requirement": meets,
        "meets_message": (
            "Resume meets experience requirement" if meets
            else ("Resume experience is below requirement" if job_exp.get("level_value")
                  else "No experience requirement found")
        ),
    }


# ---------------------------------------------------------------------------
# Responsibility & experience duty matching
# ---------------------------------------------------------------------------

RESPONSIBILITY_ANCHORS = [
    "key responsibilities and engineering duties",
    "what you will build, develop and deploy",
    "design and implement software systems and APIs",
    "write clean, testable code and conduct code reviews",
    "collaborate with product and engineering teams",
    "maintain and improve existing software and infrastructure",
    "troubleshoot, debug and optimise application performance",
    "will be responsible for delivering software features",
    "expected to architect and build scalable backend services",
    "core engineering duties and technical deliverables",
]

EXPERIENCE_ANCHORS = [
    "software engineering experience and professional background",
    "developed and deployed production applications",
    "designed and implemented backend services and REST APIs",
    "led engineering projects and mentored developers",
    "built and maintained cloud infrastructure on aws or azure",
    "worked on distributed systems and microservices",
    "implemented ci/cd pipelines and automated deployments",
    "contributed to open source or personal software projects",
    "previous roles as software engineer or developer",
    "full stack or backend development work history",
]

_RESP_SECTION_KEYWORDS = [
    "responsibilities", "duties", "key responsibilities", "role responsibilities",
    "what you will do", "what you'll do", "your role", "job duties",
    "core responsibilities", "primary responsibilities", "the role",
    "you will", "you'll be", "in this role",
]

_EXP_SECTION_KEYWORDS = [
    "work experience", "professional experience", "employment history",
    "work history", "career history", "experience",
    "engineering experience", "technical experience",
]

_SECTION_STOP_WORDS = [
    "education", "skills", "certifications", "projects", "certificates",
    "publications", "awards", "languages", "summary", "objective",
    "references", "volunteer", "training", "courses", "interests",
    "hobbies", "achievements", "activities", "qualifications",
    "benefits", "about us", "about the company", "compensation",
]


def _extract_section_lines(
    text: str,
    section_keywords: List[str],
    stop_words: Optional[List[str]] = None,
    min_len: int = 20,
    fallback: bool = True,
) -> List[str]:
    """
    Extract lines that belong to the section identified by *section_keywords*.
    Stops when a line matching any *stop_words* is encountered.
    When *fallback* is True and no section header is found, returns all
    non-trivial lines. Set fallback=False to return [] instead (e.g. for
    certifications, where a full-document scan produces false positives).
    """
    if stop_words is None:
        stop_words = _SECTION_STOP_WORDS

    text_clean = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [l.strip() for l in text_clean.split("\n") if l.strip()]

    section_lines: List[str] = []
    in_section = False

    for line in lines:
        line_lower = line.lower()

        if not in_section:
            for kw in section_keywords:
                if kw in line_lower and len(line) < 80:
                    in_section = True
                    break
            continue

        # Check for a new section header
        if any(sw in line_lower and len(line) < 60 for sw in stop_words):
            break

        if len(line) >= min_len:
            section_lines.append(line)

    if not section_lines and fallback:
        # Fallback: return all non-trivial lines
        section_lines = [l.strip() for l in lines if len(l.strip()) >= min_len]

    return section_lines


def _lines_to_sentences(lines: List[str], min_len: int = 20) -> List[str]:
    sentences: List[str] = []
    for line in lines:
        parts = re.split(r'(?<=[.!?])\s+', line)
        for part in parts:
            part = part.strip()
            if len(part) >= min_len:
                sentences.append(part)
    return sentences


def _extract_responsibilities(text: str) -> List[str]:
    model = _get_model()

    lines = _extract_section_lines(text, _RESP_SECTION_KEYWORDS)
    sentences = _lines_to_sentences(lines)

    if not sentences:
        return []

    anchor_embeddings = model.encode(RESPONSIBILITY_ANCHORS, convert_to_numpy=True, show_progress_bar=False)
    sentence_embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)

    a_norm = anchor_embeddings / (np.linalg.norm(anchor_embeddings, axis=1, keepdims=True) + 1e-10)
    s_norm = sentence_embeddings / (np.linalg.norm(sentence_embeddings, axis=1, keepdims=True) + 1e-10)
    max_sims = (a_norm @ s_norm.T).max(axis=0)

    seen: Set[str] = set()
    responsibilities: List[str] = []
    for i, sentence in enumerate(sentences):
        if max_sims[i] > 0.35:
            norm = sentence.lower().strip()
            if norm not in seen:
                seen.add(norm)
                responsibilities.append(sentence)

    return responsibilities


def _extract_professional_experience(text: str) -> List[Dict[str, any]]:
    model = _get_model()

    lines = _extract_section_lines(text, _EXP_SECTION_KEYWORDS)
    sentences = _lines_to_sentences(lines)

    if not sentences:
        return []

    anchor_embeddings = model.encode(EXPERIENCE_ANCHORS, convert_to_numpy=True, show_progress_bar=False)
    sentence_embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)

    a_norm = anchor_embeddings / (np.linalg.norm(anchor_embeddings, axis=1, keepdims=True) + 1e-10)
    s_norm = sentence_embeddings / (np.linalg.norm(sentence_embeddings, axis=1, keepdims=True) + 1e-10)
    max_sims = (a_norm @ s_norm.T).max(axis=0)

    seen: Set[str] = set()
    items: List[Dict[str, any]] = []
    for i, sentence in enumerate(sentences):
        if max_sims[i] > 0.30:
            norm = sentence.lower().strip()
            if norm not in seen:
                seen.add(norm)
                items.append({
                    "duty": sentence,
                    "confidence": round(float(max_sims[i]), 3),
                })

    return items


def _semantic_compare_duties(
    responsibilities: List[str],
    experience_items: List[Dict[str, any]]
) -> Dict[str, any]:
    if not responsibilities or not experience_items:
        return {
            "matched_duties": [],
            "unmatched_responsibilities": responsibilities or [],
            "explanation": "Could not extract duties or experience to compare",
            "score": 0,
        }

    model = _get_model()

    resp_embeddings = model.encode(responsibilities, convert_to_numpy=True, show_progress_bar=False)
    exp_texts = [item["duty"] for item in experience_items]
    exp_embeddings = model.encode(exp_texts, convert_to_numpy=True, show_progress_bar=False)

    r_norm = resp_embeddings / (np.linalg.norm(resp_embeddings, axis=1, keepdims=True) + 1e-10)
    e_norm = exp_embeddings / (np.linalg.norm(exp_embeddings, axis=1, keepdims=True) + 1e-10)
    similarity_matrix = r_norm @ e_norm.T

    matched: List[Dict[str, any]] = []
    unmatched: List[str] = []
    matched_resp: Set[int] = set()
    matched_exp: Set[int] = set()

    # Sort responsibilities by their best available match (greedy, highest first)
    best_per_resp = [
        (i, int(np.argmax(similarity_matrix[i])), float(np.max(similarity_matrix[i])))
        for i in range(len(responsibilities))
    ]
    best_per_resp.sort(key=lambda x: x[2], reverse=True)

    for i, best_j, best_sim in best_per_resp:
        if i in matched_resp:
            continue
        if best_j in matched_exp:
            # Find next best available
            order = np.argsort(similarity_matrix[i])[::-1]
            found = False
            for j in order:
                if j not in matched_exp and similarity_matrix[i, j] > 0.50:
                    matched.append({
                        "job_duty": responsibilities[i],
                        "experience_duty": exp_texts[j],
                        "similarity": round(float(similarity_matrix[i, j]), 3),
                    })
                    matched_resp.add(i)
                    matched_exp.add(j)
                    found = True
                    break
            if not found:
                unmatched.append(responsibilities[i])
        elif best_sim > 0.50:
            matched.append({
                "job_duty": responsibilities[i],
                "experience_duty": exp_texts[best_j],
                "similarity": round(best_sim, 3),
            })
            matched_resp.add(i)
            matched_exp.add(best_j)
        else:
            unmatched.append(responsibilities[i])

    score = round(len(matched) / len(responsibilities) * 100, 1) if responsibilities else 0

    if score >= 80:
        explanation = f"Excellent match ({score}%): Resume demonstrates strong alignment with most job responsibilities."
    elif score >= 60:
        explanation = f"Good match ({score}%): Resume covers majority of expected duties."
    elif score >= 40:
        explanation = f"Partial match ({score}%): Resume shows some relevant experience but missing key responsibilities."
    else:
        explanation = f"Low match ({score}%): Limited alignment found between job duties and resume experience."

    if matched:
        sample = "; ".join(m["job_duty"][:50] for m in matched[:2])
        explanation += f" Key aligned duties: {sample}"

    return {
        "matched_duties": matched,
        "unmatched_responsibilities": unmatched,
        "explanation": explanation,
        "score": score,
    }


def compare_responsibilities(
    job_text: str,
    resume_text: str,
    projects: Optional[List[Dict[str, any]]] = None,
) -> Dict[str, any]:
    """
    Match job responsibilities against resume experience and — when provided —
    project descriptions.

    Projects are treated as practical evidence of duties performed.  Any job
    responsibility not covered by work experience is re-matched against project
    descriptions, giving candidates who demonstrate skills through projects
    (academic, personal, open-source) fair credit.

    Returns both experience-only ``score`` and ``effective_score`` (experience +
    projects) so the UI can show the full picture.
    """
    job_responsibilities = _extract_responsibilities(job_text)
    resume_experience = _extract_professional_experience(resume_text)

    # --- Pass 1: match against work experience ---
    exp_comparison = _semantic_compare_duties(job_responsibilities, resume_experience)
    matched_via_exp = exp_comparison["matched_duties"]
    unmatched_after_exp: List[str] = exp_comparison["unmatched_responsibilities"]

    # --- Pass 2: match remaining duties against project descriptions ---
    matched_via_proj: List[Dict[str, any]] = []
    still_unmatched = unmatched_after_exp

    if unmatched_after_exp and projects:
        project_items = [
            {
                "duty": f"{p.get('project_title', 'Project')}: {p.get('description', '')}",
                "confidence": p.get("confidence", 0.5),
            }
            for p in projects
            if p.get("description", "").strip()
        ]
        if project_items:
            proj_comparison = _semantic_compare_duties(unmatched_after_exp, project_items)
            for m in proj_comparison["matched_duties"]:
                matched_via_proj.append({
                    "job_duty": m["job_duty"],
                    "project_contribution": m["experience_duty"],
                    "similarity": m["similarity"],
                })
            still_unmatched = proj_comparison["unmatched_responsibilities"]

    total = len(job_responsibilities)
    exp_score = exp_comparison["score"]
    effective_score = round((len(matched_via_exp) + len(matched_via_proj)) / total * 100, 1) if total else 0

    # Build explanation using the effective score
    if effective_score >= 80:
        explanation = f"Excellent match ({effective_score}%): Strong coverage across work experience and projects."
    elif effective_score >= 60:
        explanation = f"Good match ({effective_score}%): Most responsibilities covered through experience and/or projects."
    elif effective_score >= 40:
        explanation = f"Partial match ({effective_score}%): Some alignment found; projects supplement work experience."
    else:
        explanation = f"Low match ({effective_score}%): Limited alignment with job responsibilities."

    if matched_via_exp:
        sample = "; ".join(m["job_duty"][:50] for m in matched_via_exp[:2])
        explanation += f" Directly matched: {sample}"
    if matched_via_proj:
        proj_sample = "; ".join(m["job_duty"][:50] for m in matched_via_proj[:1])
        explanation += f" Project evidence: {proj_sample}"

    return {
        "job_responsibilities": job_responsibilities[:10],
        "resume_experience_duties": resume_experience[:10],
        "matched_duties": matched_via_exp,
        "matched_via_projects": matched_via_proj,
        "unmatched_responsibilities": still_unmatched,
        "score": exp_score,
        "effective_score": effective_score,
        "explanation": explanation,
    }


# ---------------------------------------------------------------------------
# Certification patterns & extraction
# ---------------------------------------------------------------------------

CERTIFICATION_PATTERNS: Dict[str, List[str]] = {
    "AWS Certified Solutions Architect": [
        "aws certified solutions architect", "aws solutions architect", "aws architect certification",
        "aws certified architect", "amazon solutions architect",
    ],
    "AWS Certified Developer": [
        "aws certified developer", "aws developer certification", "aws developer associate",
    ],
    "AWS Certified SysOps Administrator": [
        "aws certified sysops", "aws sysops administrator", "aws sysops certification",
    ],
    "AWS Certified DevOps Engineer": [
        "aws certified devops engineer", "aws devops engineer", "aws devops certification",
    ],
    "AWS Certified Machine Learning": [
        "aws certified machine learning", "aws ml certification", "aws machine learning specialty",
    ],
    "Google Cloud Professional Architect": [
        "google cloud professional architect", "gcp professional architect", "google cloud architect",
        "gcp architect certification",
    ],
    "Google Cloud Professional Data Engineer": [
        "google cloud data engineer", "gcp data engineer", "google cloud professional data engineer",
    ],
    "Google Cloud Associate Cloud Engineer": [
        "google cloud associate engineer", "gcp associate cloud engineer",
    ],
    "Microsoft Azure Fundamentals": [
        "azure fundamentals", "az-900", "microsoft azure fundamentals",
    ],
    "Microsoft Azure Administrator": [
        "azure administrator", "az-104", "microsoft azure administrator",
    ],
    "Microsoft Azure Solutions Architect": [
        "azure solutions architect", "az-305", "microsoft azure architect",
    ],
    "PMP": [
        "pmp", "project management professional", "pmp certification", "pmp certified",
    ],
    "Certified ScrumMaster": [
        "certified scrummaster", "csm", "certified scrum master",
    ],
    "CISSP": [
        "cissp", "certified information systems security professional",
    ],
    "CompTIA Security+": [
        "comptia security+", "security+", "comptia security plus",
    ],
    "CompTIA Network+": [
        "comptia network+", "network+",
    ],
    "Cisco CCNA": [
        "ccna", "cisco ccna", "cisco certified network associate",
    ],
    "Cisco CCNP": [
        "ccnp", "cisco ccnp", "cisco certified network professional",
    ],
    "Certified Kubernetes Administrator": [
        "certified kubernetes administrator", "cka",
    ],
    "Certified Kubernetes Application Developer": [
        "certified kubernetes application developer", "ckad",
    ],
    "Terraform Associate": [
        "terraform associate", "hashicorp terraform", "terraform certification",
    ],
    "ITIL Foundation": [
        "itil foundation", "itil v4", "itil certification",
    ],
    "Six Sigma Green Belt": [
        "six sigma green belt", "lean six sigma green belt",
    ],
    "Six Sigma Black Belt": [
        "six sigma black belt", "lean six sigma black belt",
    ],
    "Oracle Certified Professional": [
        "oracle certified professional", "ocp", "oracle certification",
    ],
    "Salesforce Certified Administrator": [
        "salesforce administrator", "salesforce certified administrator",
    ],
    "Tableau Certified Data Analyst": [
        "tableau certified data analyst", "tableau certification",
    ],
    "Google Analytics Certification": [
        "google analytics certification", "gaiq",
    ],
    "PowerBI Data Analyst": [
        "powerbi data analyst", "pl-300", "power bi certified",
    ],
    "MongoDB University": [
        "mongodb university", "mongodb certification course",
    ],
    "TensorFlow Developer Certificate": [
        "tensorflow developer certificate", "google tensorflow certificate",
    ],
    "Deep Learning Specialization": [
        "deep learning specialization", "deeplearning.ai", "andrew ng deep learning",
    ],
    "edX Certificate": [
        "edx course", "edx certificate", "edx certification",
    ],
    "Coursera Certificate": [
        "coursera course", "coursera certificate", "coursera specialization",
        "coursera professional certificate",
    ],
    "Udemy Certificate": [
        "udemy course", "udemy certificate",
    ],
    "Certified Embedded Systems Developer": [
        "certified embedded systems developer", "cesd",
    ],
    "NVIDIA CUDA Certification": [
        "nvidia cuda certification", "cuda programming certification", "cuda certification",
    ],
    "IoT Certification": [
        "internet of things certification", "iot certification",
    ],
    "MATLAB Certification": [
        "matlab certification", "matlab course",
    ],
    "ROS Certification": [
        "ros certification", "robot operating system certification",
    ],
}

CERTIFICATION_ANCHORS = [
    "certifications", "certificates", "credentials", "professional certifications",
    "technical certifications", "certified", "certification in", "certification:",
    "professional certificate", "qualifications", "licenses",
]


def _build_certification_database():
    global _cert_embeddings, _cert_labels, _cert_variants

    if _cert_embeddings is not None:
        return

    with _db_lock:
        if _cert_embeddings is not None:
            return

        model = _get_model()
        cert_labels = []
        cert_variants_map: Dict[str, List[str]] = {}

        for cert_name, variants in CERTIFICATION_PATTERNS.items():
            for variant in variants:
                lv = variant.lower().strip()
                cert_labels.append(lv)
                if cert_name not in cert_variants_map:
                    cert_variants_map[cert_name] = []
                cert_variants_map[cert_name].append(lv)

        _cert_labels = cert_labels
        _cert_variants = cert_variants_map
        _cert_embeddings = model.encode(cert_labels, convert_to_numpy=True, show_progress_bar=False)


def extract_certifications(text: str) -> List[Dict[str, any]]:
    _build_certification_database()
    model = _get_model()

    cert_section_keywords = [
        "certifications", "certificates", "credentials", "certification",
        "professional certifications", "technical certifications",
    ]
    section_header_words = {
        "certifications", "certificates", "credentials", "certification",
        "professional", "technical", "licenses", "accreditations",
    }

    # fallback=False: if the resume has no certifications section, return []
    # rather than running every resume line through SBERT (which causes false
    # positives like "Certified Embedded Systems Developer" on a CV that has
    # no certifications at all).
    cert_section_lines = _extract_section_lines(text, cert_section_keywords, min_len=3, fallback=False)

    target_lines = [l.strip() for l in cert_section_lines if l.strip()]

    candidate_entries: List[str] = []
    for line in target_lines:
        line_clean = re.sub(r'^[\s•\-*–—]+', '', line).strip()
        if not line_clean or len(line_clean) < 3:
            continue
        words = {w.strip().lower() for w in re.split(r'[\s,;:]+', line_clean) if w.strip()}
        if words and words.issubset(section_header_words):
            continue
        if ',' in line_clean:
            for p in line_clean.split(','):
                p = p.strip()
                if len(p) > 3:
                    pw = {w.strip().lower() for w in re.split(r'[\s,;:]+', p) if w.strip()}
                    if not pw.issubset(section_header_words):
                        candidate_entries.append(p)
        else:
            candidate_entries.append(line_clean)

    candidate_entries = list(dict.fromkeys(candidate_entries))

    if not candidate_entries:
        return []

    entry_embeddings = model.encode(candidate_entries, convert_to_numpy=True, show_progress_bar=False)
    c_norm = _cert_embeddings / (np.linalg.norm(_cert_embeddings, axis=1, keepdims=True) + 1e-10)
    e_norm = entry_embeddings / (np.linalg.norm(entry_embeddings, axis=1, keepdims=True) + 1e-10)
    sim_matrix = c_norm @ e_norm.T

    found: List[Dict[str, any]] = []
    seen: Set[str] = set()

    for i, entry in enumerate(candidate_entries):
        entry_lower = entry.lower()

        exact_match = None
        for cert_name, variants in _cert_variants.items():
            if cert_name in seen:
                continue
            for variant in variants:
                if variant in entry_lower or entry_lower in variant:
                    exact_match = cert_name
                    break
            if exact_match:
                break

        if exact_match:
            seen.add(exact_match)
            found.append({
                "certification": exact_match,
                "matched_variant": entry,
                "context": entry,
                "confidence": 1.0,
            })
            continue

        col = sim_matrix[:, i]
        max_sim = float(col.max())
        if max_sim < 0.50:
            continue

        best_idx = int(np.argmax(col))
        best_label = _cert_labels[best_idx]
        best_name = next(
            (cn for cn, vs in _cert_variants.items() if best_label in vs),
            None,
        )

        if best_name and best_name not in seen:
            seen.add(best_name)
            found.append({
                "certification": best_name,
                "matched_variant": entry,
                "context": entry,
                "confidence": round(max_sim, 3),
            })

    return found


# ---------------------------------------------------------------------------
# Projects extraction
# ---------------------------------------------------------------------------

PROJECT_SECTION_KEYWORDS = [
    "projects", "project experience", "key projects", "academic projects",
    "personal projects", "professional projects", "major projects",
    "project work", "software projects", "development projects",
]

PROJECT_ACTION_VERBS = [
    "developed", "designed", "built", "created", "implemented", "architected",
    "engineered", "constructed", "established", "launched", "delivered",
    "led", "managed", "spearheaded", "drove", "coordinated",
    "migrated", "integrated", "automated", "configured", "deployed",
    "optimized", "refactored", "redesigned", "restructured", "modernized",
]


def extract_projects(text: str) -> List[Dict[str, any]]:
    model = _get_model()

    text_clean = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [l.strip() for l in text_clean.split("\n") if l.strip()]

    project_section_header_words = {
        "projects", "project", "key", "academic", "personal", "professional",
        "major", "software", "development", "experience", "work",
    }

    trigger_line_skipped = False
    raw_project_lines: List[str] = []
    in_project_section = False
    project_started = False

    for line in lines:
        line_lower = line.lower()
        if not project_started:
            for kw in PROJECT_SECTION_KEYWORDS:
                if kw in line_lower and len(line) < 50:
                    in_project_section = True
                    project_started = True
                    trigger_line_skipped = True
                    break
            if not in_project_section:
                continue
        if in_project_section:
            if trigger_line_skipped:
                trigger_line_skipped = False
                continue

            known_section_headers = [
                # major section names
                "education", "experience", "skills", "certifications",
                "employment", "summary", "objective", "references",
                "work experience", "publications", "awards",
                "languages", "language", "additional",
                "interests", "hobbies", "leadership", "volunteer",
                "honors", "achievements", "affiliations", "memberships",
                "training", "courses", "patents", "activities",
                "extracurricular", "community",
                # compound / multi-word section headers
                "personal skills", "technical skills", "core skills",
                "professional skills", "professional experience",
                "key skills", "soft skills", "hard skills",
                # skills sub-section headers (e.g. "Programming Languages :")
                "programming languages", "frameworks and libraries",
                "frameworks", "libraries", "other tools", "tools",
                "core competencies", "competencies", "technical expertise",
                "technical stack", "tech stack", "technology stack",
            ]
            # (1) Exact-line match: avoids "personal skills" triggering on bare
            # "skills" via substring, but still catches compound entries we
            # added explicitly (e.g. "personal skills", "technical skills").
            line_core = line_lower.strip().rstrip(':. ').strip()
            is_header = any(line_core == oh for oh in known_section_headers)

            # (2) ALL-CAPS compound headers joined by "&", "/", "and", etc.
            # e.g. "LANGUAGES & ADDITIONAL", "SKILLS & EXPERIENCE".
            # Only triggered for lines that are entirely uppercase (section
            # headings), never for mixed-case prose.
            _allcaps_break_words = {
                'education', 'certifications', 'employment', 'references',
                'publications', 'awards', 'achievements', 'languages',
                'activities', 'hobbies', 'interests', 'volunteer',
                'leadership', 'memberships', 'affiliations', 'extracurricular',
                'patents', 'honors', 'courses', 'training', 'summary',
                'objective', 'experience', 'additional',
            }
            is_allcaps_compound = (
                len(line) < 60
                and line.strip().isupper()
                and bool(
                    set(re.split(r'[\s&,/|]+', line_lower.strip()))
                    & _allcaps_break_words
                )
            )

            # (3) Short lines ending with ':' are subsection headers
            # (e.g. "Programming Languages :").
            is_colon_header = (
                len(line) < 60
                and line_lower.rstrip().endswith(':')
                and line_lower.count(':') == 1
                and not re.search(r'https?:|//|\d:\d', line_lower)
            )

            if is_header or is_allcaps_compound or is_colon_header:
                break

            if (
                len(line) < 50
                and line[0].isupper()
                and not line.startswith(('•', '-', '*', '–', '—'))
            ):
                first_word = line_lower.split()[0].rstrip(':;,.') if line_lower.split() else ''
                not_action = first_word not in {
                    'developed', 'built', 'created', 'designed', 'implemented',
                    'architected', 'engineered', 'led', 'managed',
                }
                is_single_section_word = (
                    len(line_lower.split()) == 1
                    and line_lower.rstrip('.') in {
                        'education', 'experience', 'skills', 'certifications',
                        'publications', 'awards', 'languages', 'interests',
                        'hobbies', 'leadership', 'volunteer', 'activities',
                        'references', 'summary', 'objective', 'training',
                        'courses', 'patents', 'memberships', 'affiliations',
                        'achievements', 'honors',
                    }
                )
                if not_action and is_single_section_word:
                    break

            words = {w.strip().lower() for w in re.split(r'[\s,;:]+', line) if w.strip()}
            if words and words.issubset(project_section_header_words):
                continue
            raw_project_lines.append(line)

    if not raw_project_lines:
        return []

    project_blocks: List[Dict[str, str]] = []
    current_title: Optional[str] = None
    current_bullets: List[str] = []

    description_verbs = {
        "developed", "designed", "built", "created", "implemented", "architected",
        "engineered", "launched", "delivered", "led", "managed", "spearheaded",
        "migrated", "integrated", "automated", "configured", "deployed",
        "optimized", "refactored", "wrote", "coded", "programmed",
    }
    common_start_words = {
        "the", "a", "an", "some", "this", "that", "these", "those",
        "our", "my", "for", "with", "using", "through", "via",
        "built", "developed", "designed", "created", "implemented",
    }

    def is_bullet_line(l: str) -> bool:
        return bool(re.match(r'^[\s•\-*–—>]+', l))

    def is_action_line(l: str) -> bool:
        first = l.lower().split()[0].rstrip(',;:') if l.split() else ''
        return first in description_verbs or first.endswith('ed')

    def is_tech_line(l: str) -> bool:
        lower = l.lower()
        # Explicit "Tech: ..." / "Stack: ..." labels
        if any(lower.startswith(kw) and ':' in lower
               for kw in ["stack", "tech", "technologies", "tools", "language",
                          "framework", "database", "library", "api", "platform"]):
            return True
        # Comma-separated list of 3+ short tokens with no sentence verbs
        # → looks like a tech-stack enumeration ("PHP, HTML, CSS, MySQL")
        parts = [p.strip() for p in l.split(',')]
        if len(parts) >= 3 and all(0 < len(p) <= 30 and len(p.split()) <= 3 for p in parts):
            return True
        return False

    def is_title_line(l: str, prev: Optional[str], has_existing: bool) -> bool:
        if is_bullet_line(l) or is_action_line(l) or is_tech_line(l):
            return False
        # Sentences ending with '.' and 5+ words are prose, not project titles.
        # e.g. "Open to both on-shore and off-shore collaboration models."
        if l.rstrip().endswith('.') and len(l.split()) >= 5:
            return False
        if l.lower().startswith(('built a', 'developed a', 'created a', 'designed a')):
            return False
        if len(l) > 100:
            return False
        if prev is not None and is_bullet_line(prev):
            return False
        if has_existing:
            first_word = l.split()[0].lower().rstrip(':;,.') if l.split() else ''
            has_separator = bool(re.search(r'[—\-–|:]\s', l))
            has_proper_case = l[0].isupper() and first_word not in common_start_words
            return has_separator or (len(l) <= 60 and has_proper_case)
        return True

    prev_line: Optional[str] = None
    for line in raw_project_lines:
        line_clean = re.sub(r'^[\s•\-*–—>]+', '', line).strip()
        if not line_clean:
            prev_line = line
            continue

        if is_title_line(line, prev_line, current_title is not None):
            if current_title is not None:
                project_blocks.append({
                    "title": current_title,
                    "description": " ".join(current_bullets) if current_bullets else current_title,
                })
            current_title = line_clean
            current_bullets = []
        else:
            current_bullets.append(line_clean)

        prev_line = line

    if current_title is not None:
        project_blocks.append({
            "title": current_title,
            "description": " ".join(current_bullets) if current_bullets else current_title,
        })

    verb_embeddings = model.encode(PROJECT_ACTION_VERBS, convert_to_numpy=True, show_progress_bar=False)
    v_norm = verb_embeddings / (np.linalg.norm(verb_embeddings, axis=1, keepdims=True) + 1e-10)

    projects: List[Dict[str, any]] = []
    seen_titles: Set[str] = set()

    for block in project_blocks:
        title_key = block["title"].lower().strip()[:60]
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        desc_emb = model.encode([block["description"]], convert_to_numpy=True, show_progress_bar=False)
        l_norm = desc_emb / (np.linalg.norm(desc_emb, axis=1, keepdims=True) + 1e-10)
        max_sim = float((v_norm @ l_norm.T).max())

        projects.append({
            "project_title": block["title"],
            "description": block["description"],
            "confidence": round(max_sim, 3),
        })

    # ── Supplemental pass: year-pattern scan ──────────────────────────────
    # Multi-column PDFs are often read left-column-first, which places
    # right-column projects AFTER PERSONAL SKILLS / REFERENCES in the text
    # stream.  The section-based scan above stops at those headers and misses
    # those entries.  We scan the full line list for "Title, YYYY-YYYY" /
    # "Title, YYYY-Present" and add any projects not yet captured.
    _year_re = re.compile(
        r'^([\w][\w\s\-\'\"&().+/]+?)'
        r'\s*,\s*((?:19|20)\d{2})\s*[-–—]\s*'
        r'((?:19|20)\d{2}|[Pp]resent|[Oo]ngoing|[Cc]urrent)\s*$'
    )

    # Keyword sets that identify NON-project entries that happen to contain
    # a year range (education degrees, job titles, school names, etc.)
    _edu_markers = {
        'b.sc', 'm.sc', 'ph.d', 'phd', 'bsc', 'msc', 'b.eng', 'm.eng',
        'bachelor', 'master', 'doctorate', 'degree', 'diploma',
        'g.c.e', 'gce', 'advanced level', 'ordinary level', 'a/l', 'o/l',
        'university', 'college', 'school', 'institute', 'faculty',
        'examination', 'higher national',
    }
    _job_markers = {
        'software engineer', 'senior engineer', 'junior engineer',
        'developer', 'intern', 'internship', 'engineer', 'manager',
        'analyst', 'consultant', 'designer', 'architect', 'specialist',
        'coordinator', 'associate', 'director', 'officer', 'lead',
        'head of', 'vice president', 'vp ', 'cto', 'ceo',
    }

    _supp_known = [
        "education", "experience", "skills", "certifications", "employment",
        "summary", "objective", "references", "work experience", "publications",
        "awards", "languages", "language", "additional", "interests", "hobbies",
        "leadership", "volunteer", "honors", "achievements", "affiliations",
        "memberships", "training", "courses", "patents", "activities",
        "extracurricular", "community", "personal skills", "technical skills",
        "core skills", "professional skills", "professional experience",
        "key skills", "soft skills", "hard skills",
        "programming languages", "frameworks and libraries",
        "frameworks", "libraries", "other tools", "tools",
    ]
    existing_keys = {p["project_title"].lower()[:40] for p in projects}

    for idx, raw_line in enumerate(lines):
        m = _year_re.match(raw_line)
        if not m:
            continue
        candidate = raw_line.strip()
        name_part = m.group(1).lower().strip()

        # Skip education and job-title entries
        if any(kw in name_part for kw in _edu_markers):
            continue
        if any(kw in name_part for kw in _job_markers):
            continue

        # Skip if the name looks like a tech/skill list (3+ comma items)
        name_parts = [p.strip() for p in m.group(1).split(',')]
        if len(name_parts) >= 3:
            continue

        # Skip if already captured
        cand_key = candidate.lower()[:40]
        if any(cand_key in ek or ek in cand_key for ek in existing_keys):
            continue

        # Collect following lines as description
        supp_lines: List[str] = []
        for j in range(idx + 1, min(idx + 12, len(lines))):
            nxt = lines[j].strip()
            if not nxt:
                continue
            if _year_re.match(nxt):
                break
            nxt_core = nxt.lower().strip().rstrip(':. ').strip()
            if len(nxt) < 60 and any(nxt_core == oh for oh in _supp_known):
                continue
            supp_lines.append(nxt)

        description = " ".join(supp_lines) if supp_lines else candidate
        # Require a real description — not just the title repeated
        if len(description) < 25 or description.lower().strip() == candidate.lower().strip():
            continue

        desc_emb = model.encode([description], convert_to_numpy=True, show_progress_bar=False)
        l2 = desc_emb / (np.linalg.norm(desc_emb, axis=1, keepdims=True) + 1e-10)
        supp_sim = float((v_norm @ l2.T).max())
        projects.append({
            "project_title": candidate,
            "description": description,
            "confidence": round(supp_sim, 3),
        })
        existing_keys.add(cand_key)

    return projects


# ---------------------------------------------------------------------------
# Semantic comparison helpers (certifications & projects vs job)
# ---------------------------------------------------------------------------

def _semantic_compare_with_evidence(
    resume_items: List[Dict[str, any]],
    job_sentences: List[str],
    item_name_key: str,
    item_desc_key: str,
    threshold: float = 0.40,
) -> Dict[str, any]:
    if not resume_items or not job_sentences:
        return {
            "matched_evidence": [],
            "unmatched_items": [item[item_name_key] for item in resume_items] if resume_items else [],
            "match_score": 0,
            "total_items": len(resume_items) if resume_items else 0,
            "matched_count": 0,
        }

    model = _get_model()

    resume_texts = [item[item_desc_key] for item in resume_items]
    resume_embeddings = model.encode(resume_texts, convert_to_numpy=True, show_progress_bar=False)
    job_embeddings = model.encode(job_sentences, convert_to_numpy=True, show_progress_bar=False)

    r_norm = resume_embeddings / (np.linalg.norm(resume_embeddings, axis=1, keepdims=True) + 1e-10)
    j_norm = job_embeddings / (np.linalg.norm(job_embeddings, axis=1, keepdims=True) + 1e-10)
    sim_matrix = r_norm @ j_norm.T

    matched_evidence: List[Dict[str, any]] = []
    unmatched_items: List[str] = []

    for i, item in enumerate(resume_items):
        best_j = int(np.argmax(sim_matrix[i]))
        best_sim = float(sim_matrix[i, best_j])

        if best_sim >= threshold:
            matched_evidence.append({
                "resume_item": item[item_desc_key],
                "resume_item_name": item[item_name_key],
                "matching_job_sentence": job_sentences[best_j],
                "similarity_score": round(best_sim, 3),
            })
        else:
            unmatched_items.append(item[item_name_key])

    matched_count = len(matched_evidence)
    total = len(resume_items)

    return {
        "matched_evidence": matched_evidence,
        "unmatched_items": unmatched_items,
        "match_score": round(matched_count / total * 100, 1) if total else 0,
        "total_items": total,
        "matched_count": matched_count,
    }


def compare_certifications_with_job(
    resume_text: str,
    job_text: str,
    extracted_certs: Optional[List[Dict[str, any]]] = None,
) -> Dict[str, any]:
    """
    Match resume certifications against job skills and qualification requirements.

    ``extracted_certs`` may be passed in from an earlier extraction call to
    avoid re-parsing the resume text.

    New: ``qualification_matches`` — certifications that directly satisfy a
    stated qualification/credential requirement in the JD (e.g. "AWS
    certification required").
    """
    resume_certs = extracted_certs if extracted_certs is not None else extract_certifications(resume_text)
    if not resume_certs:
        return {
            "certifications": [],
            "certification_skills_map": [],
            "qualification_matches": [],
            "overall_match_score": 0,
            "total_certifications": 0,
            "summary": "No certifications found in the resume.",
        }

    model = _get_model()
    cert_names = [c["certification"] for c in resume_certs]
    cert_embeddings = model.encode(cert_names, convert_to_numpy=True, show_progress_bar=False)
    c_norm = cert_embeddings / (np.linalg.norm(cert_embeddings, axis=1, keepdims=True) + 1e-10)

    # --- Skill relevance mapping ---
    job_skills_data = extract_skills_with_scores(job_text)
    job_all_skill_names = [
        skill_name
        for category_skills in job_skills_data.values()
        for skill_name in category_skills
    ]

    certification_skills_map: List[Dict[str, any]] = []
    total_skills_count = len(job_all_skill_names)

    if job_all_skill_names:
        skill_embeddings = model.encode(job_all_skill_names, convert_to_numpy=True, show_progress_bar=False)
        s_norm = skill_embeddings / (np.linalg.norm(skill_embeddings, axis=1, keepdims=True) + 1e-10)
        skill_sim = c_norm @ s_norm.T   # (n_certs, n_skills)

        for i, cert in enumerate(resume_certs):
            skill_matches = [
                {"skill": job_all_skill_names[j], "similarity_score": round(float(skill_sim[i, j]), 3)}
                for j in range(len(job_all_skill_names))
                if skill_sim[i, j] >= 0.30
            ]
            skill_matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            certification_skills_map.append({
                "certification": cert["certification"],
                "confidence": cert["confidence"],
                "context": cert["context"],
                "related_skills": skill_matches,
                "related_skills_count": len(skill_matches),
                "match_rate": round(len(skill_matches) / total_skills_count * 100, 1) if total_skills_count else 0,
                "has_relevance": len(skill_matches) > 0,
            })
    else:
        for cert in resume_certs:
            certification_skills_map.append({
                "certification": cert["certification"],
                "confidence": cert["confidence"],
                "context": cert["context"],
                "related_skills": [],
                "related_skills_count": 0,
                "match_rate": 0,
                "has_relevance": False,
            })

    # --- Qualification requirement matching ---
    # Find JD sentences that mention credential/certification requirements and
    # check if any resume cert satisfies them.
    _qual_trigger = re.compile(
        r'\b(certif|credential|qualif|accredit|licensed|prefer|require)\w*\b', re.I
    )
    job_sentences = [
        s.strip() for s in re.split(r'[.\n]', job_text)
        if len(s.strip()) > 15 and _qual_trigger.search(s)
    ]

    qualification_matches: List[Dict[str, any]] = []
    if job_sentences:
        qual_embeddings = model.encode(job_sentences, convert_to_numpy=True, show_progress_bar=False)
        q_norm = qual_embeddings / (np.linalg.norm(qual_embeddings, axis=1, keepdims=True) + 1e-10)
        qual_sim = c_norm @ q_norm.T   # (n_certs, n_qual_sentences)

        matched_qual_idx: Set[int] = set()
        for i, cert in enumerate(resume_certs):
            best_j = int(np.argmax(qual_sim[i]))
            best_sim = float(qual_sim[i, best_j])
            if best_sim >= 0.42 and best_j not in matched_qual_idx:
                matched_qual_idx.add(best_j)
                qualification_matches.append({
                    "certification": cert["certification"],
                    "matched_requirement": job_sentences[best_j],
                    "similarity": round(best_sim, 3),
                })

    high_relevance = sum(1 for c in certification_skills_map if c["has_relevance"])
    overall_match_score = round(high_relevance / len(resume_certs) * 100, 1) if resume_certs else 0

    return {
        "certifications": [
            {"certification": c["certification"], "confidence": c["confidence"], "context": c["context"]}
            for c in resume_certs
        ],
        "certification_skills_map": certification_skills_map,
        "qualification_matches": qualification_matches,
        "overall_match_score": overall_match_score,
        "total_certifications": len(resume_certs),
        "relevant_certifications": high_relevance,
        "summary": (
            f"Found {len(resume_certs)} certification(s). "
            f"{high_relevance} relate to skills sought by the job ({overall_match_score}% relevance)."
            + (f" {len(qualification_matches)} satisfy stated qualification requirement(s)."
               if qualification_matches else "")
        ),
    }


def compare_projects_with_job(
    resume_text: str,
    job_text: str,
    extracted_projects: Optional[List[Dict[str, any]]] = None,
) -> Dict[str, any]:
    """
    Match resume projects against job skills and responsibilities.

    ``extracted_projects`` may be passed in from an earlier call to avoid
    re-parsing the resume text.

    New: ``responsibility_matches`` — project descriptions that directly
    address a stated job responsibility, demonstrating practical experience
    beyond the skills section.
    """
    resume_projects = extracted_projects if extracted_projects is not None else extract_projects(resume_text)
    if not resume_projects:
        return {
            "projects": [],
            "projects_skills_map": [],
            "responsibility_matches": [],
            "overall_match_score": 0,
            "total_projects": 0,
            "summary": "No projects found in the resume.",
        }

    model = _get_model()
    project_descs = [p["description"] for p in resume_projects]
    project_embeddings = model.encode(project_descs, convert_to_numpy=True, show_progress_bar=False)
    p_norm = project_embeddings / (np.linalg.norm(project_embeddings, axis=1, keepdims=True) + 1e-10)

    # --- Skill relevance mapping ---
    job_skills_data = extract_skills_with_scores(job_text)
    job_all_skill_names = [
        skill_name
        for category_skills in job_skills_data.values()
        for skill_name in category_skills
    ]

    projects_skills_map: List[Dict[str, any]] = []
    total_skills_count = len(job_all_skill_names)

    if job_all_skill_names:
        skill_embeddings = model.encode(job_all_skill_names, convert_to_numpy=True, show_progress_bar=False)
        s_norm = skill_embeddings / (np.linalg.norm(skill_embeddings, axis=1, keepdims=True) + 1e-10)
        skill_sim = p_norm @ s_norm.T  # (n_projects, n_skills)

        for i, proj in enumerate(resume_projects):
            skill_matches = [
                {"skill": job_all_skill_names[j], "similarity_score": round(float(skill_sim[i, j]), 3)}
                for j in range(len(job_all_skill_names))
                if skill_sim[i, j] >= 0.25
            ]
            skill_matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            projects_skills_map.append({
                "project_title": proj["project_title"],
                "confidence": proj["confidence"],
                "description": proj["description"],
                "related_skills": [s["skill"] for s in skill_matches],
                "related_skills_count": len(skill_matches),
                "has_relevance": len(skill_matches) > 0,
            })
    else:
        for proj in resume_projects:
            projects_skills_map.append({
                "project_title": proj["project_title"],
                "confidence": proj["confidence"],
                "description": proj["description"],
                "related_skills": [],
                "related_skills_count": 0,
                "has_relevance": False,
            })

    # --- Responsibility matching ---
    # Compare project descriptions against job responsibility sentences to
    # show which job duties the candidate has demonstrated through projects.
    job_resp_sentences = _extract_section_lines(job_text, _RESP_SECTION_KEYWORDS, min_len=20)
    job_resp_sentences = _lines_to_sentences(job_resp_sentences, min_len=20)

    responsibility_matches: List[Dict[str, any]] = []
    if job_resp_sentences:
        resp_embeddings = model.encode(job_resp_sentences, convert_to_numpy=True, show_progress_bar=False)
        r_norm = resp_embeddings / (np.linalg.norm(resp_embeddings, axis=1, keepdims=True) + 1e-10)
        resp_sim = p_norm @ r_norm.T   # (n_projects, n_resp)

        matched_resp_idx: Set[int] = set()
        for i, proj in enumerate(resume_projects):
            best_j = int(np.argmax(resp_sim[i]))
            best_sim = float(resp_sim[i, best_j])
            if best_sim >= 0.45 and best_j not in matched_resp_idx:
                matched_resp_idx.add(best_j)
                responsibility_matches.append({
                    "project_title": proj["project_title"],
                    "matched_responsibility": job_resp_sentences[best_j],
                    "similarity": round(best_sim, 3),
                })

    high_relevance = sum(1 for p in projects_skills_map if p["has_relevance"])
    overall_match_score = round(high_relevance / len(resume_projects) * 100, 1) if resume_projects else 0

    return {
        "projects": [
            {"project_title": p["project_title"], "confidence": p["confidence"], "description": p["description"]}
            for p in resume_projects
        ],
        "projects_skills_map": projects_skills_map,
        "responsibility_matches": responsibility_matches,
        "overall_match_score": overall_match_score,
        "total_projects": len(resume_projects),
        "relevant_projects": high_relevance,
        "summary": (
            f"Found {len(resume_projects)} project(s). "
            f"{high_relevance} relate to skills sought by the job ({overall_match_score}% relevance)."
            + (f" {len(responsibility_matches)} project(s) directly address job responsibilities."
               if responsibility_matches else "")
        ),
    }
