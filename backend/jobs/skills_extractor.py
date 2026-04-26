import re
import threading
from typing import Dict, List, Set, Optional, Tuple

import numpy as np

_model = None
_lock = threading.Lock()
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

SKILL_THRESHOLD = 0.55
MATCH_THRESHOLD = 0.70
EDU_THRESHOLD = 0.60

PROGRAMMING_LANGUAGES: Dict[str, List[str]] = {
    "Python": ["python", "py", "python3"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript", "ts"],
    "Java": ["java", "java ee", "java se"],
    "C++": ["c++", "cpp", "c plus plus"],
    "C#": ["c#", "csharp", "dot net", ".net"],
    "Go": ["go", "golang"],
    "Rust": ["rust"],
    "Ruby": ["ruby", "ruby language"],
    "PHP": ["php", "php laravel"],
    "Swift": ["swift", "swift ios"],
    "Kotlin": ["kotlin", "kotlin android"],
    "Scala": ["scala"],
    "R": ["r", "r programming", "r language"],
    "Dart": ["dart", "dart flutter"],
    "SQL": ["sql", "mysql", "postgresql", "plsql", "tsql", "sql query"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3", "stylesheet"],
    "Bash": ["bash", "shell", "sh", "zsh", "bash script"],
    "PowerShell": ["powershell", "ps1"],
    "YAML": ["yaml", "yml"],
    "JSON": ["json"],
    "XML": ["xml"],
    "GraphQL": ["graphql", "gql"],
}

FRONTEND_FRAMEWORKS: Dict[str, List[str]] = {
    "React": ["react", "reactjs", "react.js", "react library"],
    "Vue": ["vue", "vuejs", "vue.js", "vue3"],
    "Angular": ["angular", "angularjs", "angular 2", "ngular"],
    "Next.js": ["nextjs", "next.js", "nextjs react", "next"],
    "Svelte": ["svelte", "sveltejs"],
    "Nuxt": ["nuxt", "nuxtjs", "nuxt.js", "nuxt vue"],
    "Gatsby": ["gatsby", "gatsbyjs"],
    "Remix": ["remix", "remix.run"],
    "SvelteKit": ["sveltekit", "svelte kit"],
    "Solid": ["solid", "solidjs", "solid.js"],
    "Qwik": ["qwik", "qwikjs"],
    "React Native": ["react native", "rn", "reactnative"],
    "Flutter": ["flutter"],
    "Electron": ["electron", "electronjs"],
    "Expo": ["expo"],
}

BACKEND_FRAMEWORKS: Dict[str, List[str]] = {
    "Django": ["django", "django rest", "django rest framework", "drf"],
    "Flask": ["flask", "flask python"],
    "FastAPI": ["fastapi", "fast api"],
    "Pyramid": ["pyramid", "pyramid framework"],
    "Bottle": ["bottle", "bottle python"],
    "Express": ["express", "expressjs", "express.js", "node express"],
    "NestJS": ["nestjs", "nest.js", "nest framework"],
    "Koa": ["koa", "koajs", "koa.js"],
    "Hapi": ["hapi", "hapijs", "hapi.js"],
    "Sails": ["sails", "sailsjs", "sails.js"],
    "Rails": ["rails", "ruby on rails", "ror"],
    "Sinatra": ["sinatra", "sinatra ruby"],
    "Spring": ["spring", "spring framework", "spring java"],
    "Spring Boot": ["spring boot", "springboot", "spring-boot"],
    "Micronaut": ["micronaut"],
    "Quarkus": ["quarkus"],
    "Laravel": ["laravel", "laravel php"],
    "Symfony": ["symfony"],
    "Phoenix": ["phoenix", "phoenix elixir"],
    "Gin": ["gin", "gin go", "gin framework"],
    "Echo": ["echo", "echo go"],
    "Fiber": ["fiber", "fiber go", "gofiber"],
    "Fastify": ["fastify", "fastify js"],
    "Play": ["play framework", "play scala"],
    "Akka": ["akka"],
    "DotNet": ["asp.net", "asp.net core", ".net core", ".net", "dotnet", "dotnet core"],
}

CSS_FRAMEWORKS: Dict[str, List[str]] = {
    "Tailwind": ["tailwind", "tailwindcss", "tailwind css"],
    "Bootstrap": ["bootstrap", "bs5"],
    "Material UI": ["material ui", "mui", "@mui"],
    "Ant Design": ["ant design", "antd", "ant design react"],
    "Chakra UI": ["chakra", "chakra ui"],
    "Styled Components": ["styled-components", "styled components", "css-in-js"],
    "Sass": ["sass", "scss", "sass css", "syntactically awesome"],
    "Less": ["less", "less css"],
    "Bulma": ["bulma", "bulma css"],
    "Foundation": ["foundation", "zurb foundation"],
    "Vuetify": ["vuetify", "vuetifyjs"],
    "Quasar": ["quasar", "quasar framework"],
    "UIKit": ["uikit", "ui kit"],
}

DATABASES: Dict[str, List[str]] = {
    "PostgreSQL": ["postgresql", "postgres", "psql", "postgresql database"],
    "MySQL": ["mysql", "mysql database"],
    "MongoDB": ["mongodb", "mongo", "mongo db"],
    "Redis": ["redis", "redis cache"],
    "Elasticsearch": ["elasticsearch", "elastic", "elastic search", "elk"],
    "DynamoDB": ["dynamodb", "dynamo db", "aws dynamodb"],
    "SQLite": ["sqlite", "sqlite3", "sqlite database"],
    "Oracle": ["oracle", "oracle db", "oracle database"],
    "SQL Server": ["sql server", "mssql", "ms sql"],
    "Cassandra": ["cassandra", "apache cassandra"],
    "CouchDB": ["couchdb", "couch db"],
    "Neo4j": ["neo4j", "neo4j graph"],
    "Firebase": ["firebase", "firebase realtime"],
    "Supabase": ["supabase"],
    "PlanetScale": ["planetscale", "planet scale"],
    "InfluxDB": ["influxdb", "influx db", "influx"],
    "TimescaleDB": ["timescaledb", "timescale db"],
    "ClickHouse": ["clickhouse", "click house"],
}

DEVOPS_CLOUD: Dict[str, List[str]] = {
    "Docker": ["docker", "docker container", "docker-compose", "docker compose"],
    "Kubernetes": ["kubernetes", "k8s", "k8", "kubernetes container"],
    "Helm": ["helm", "helm chart"],
    "Terraform": ["terraform", "terraform iac", "tf"],
    "Ansible": ["ansible", "ansible automation"],
    "Jenkins": ["jenkins", "jenkins ci", "jenkins cd"],
    "GitLab CI": ["gitlab ci", "gitlabcicd", "gitlab-runner"],
    "GitHub Actions": ["github actions", "gha", "github workflow"],
    "CircleCI": ["circleci", "circle ci"],
    "AWS": ["aws", "amazon web services", "amazon aws", "ec2", "s3", "lambda aws"],
    "Azure": ["azure", "microsoft azure", "az"],
    "GCP": ["gcp", "google cloud", "google cloud platform"],
    "Vercel": ["vercel", "vercel deploy"],
    "Netlify": ["netlify"],
    "Heroku": ["heroku"],
    "Nginx": ["nginx", "nginx server"],
    "Apache": ["apache", "apache server", "httpd"],
    "Traefik": ["traefik", "traefik proxy"],
    "Prometheus": ["prometheus", "prometheus monitoring"],
    "Grafana": ["grafana", "grafana dashboard"],
    "Datadog": ["datadog", "datadog monitoring"],
    "Sentry": ["sentry", "sentry error"],
    "Git": ["git", "github", "gitlab", "bitbucket", "version control"],
}

TESTING: Dict[str, List[str]] = {
    "Pytest": ["pytest", "python test", "unittest", "nose"],
    "Jest": ["jest", "jestjs", "jest testing"],
    "Mocha": ["mocha", "mochajs"],
    "Cypress": ["cypress", "cypress.io", "cypress e2e"],
    "Playwright": ["playwright", "playwright test"],
    "Selenium": ["selenium", "selenium webdriver"],
    "Puppeteer": ["puppeteer", "puppeteer test"],
    "JUnit": ["junit", "junit test", "testng"],
    "RSpec": ["rspec", "ruby test"],
    "Cucumber": ["cucumber", "gherkin", "bdd cucumber"],
}

ALL_SKILL_CATEGORIES: Dict[str, Dict[str, List[str]]] = {
    "Programming Languages": PROGRAMMING_LANGUAGES,
    "Frontend Frameworks": FRONTEND_FRAMEWORKS,
    "Backend Frameworks": BACKEND_FRAMEWORKS,
    "CSS Frameworks": CSS_FRAMEWORKS,
    "Databases": DATABASES,
    "DevOps & Cloud": DEVOPS_CLOUD,
    "Testing": TESTING,
}


def _get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer("all-mpnet-base-v2")
    return _model


def _build_skill_database():
    global _skill_embeddings, _skill_labels, _skill_variants

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


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
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

    similarity_matrix = job_embeddings @ resume_embeddings.T

    matched = []
    missing = []
    variations: Dict[str, str] = {}

    matched_indices = set()
    for i, job_skill in enumerate(job_skill_list):
        best_j = -1
        best_sim = 0
        for j, resume_skill in enumerate(resume_skill_list):
            if j in matched_indices:
                continue
            sim = similarity_matrix[i, j]
            if sim > best_sim:
                best_sim = sim
                best_j = j

        if best_j >= 0 and best_sim >= MATCH_THRESHOLD:
            matched.append(resume_skill_list[best_j])
            matched_indices.add(best_j)
            if resume_skill_list[best_j] != job_skill:
                variations[job_skill] = resume_skill_list[best_j]
        else:
            missing.append(job_skill)

    return matched, missing, variations


def extract_skills_with_scores(text: str) -> Dict[str, Dict[str, float]]:
    text_lower = text.lower()
    text_normalized = re.sub(r'[^a-z0-9\s\.\-\+\#]', ' ', text_lower)
    text_normalized = re.sub(r'\s+', ' ', text_normalized)

    keyword_skills = _find_skills_in_text(text_normalized)

    result: Dict[str, Dict[str, float]] = {}
    for category in ALL_SKILL_CATEGORIES:
        result[category] = {}

    for category, skills in ALL_SKILL_CATEGORIES.items():
        for skill_name, variants in skills.items():
            for variant in variants:
                pattern = r'\b' + re.escape(variant.lower()) + r'\b'
                if re.search(pattern, text_normalized):
                    score = keyword_skills.get(skill_name, 0.85)
                    result[category][skill_name] = score
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


def compare_skills(job_text: str, resume_text: str) -> Dict[str, any]:
    job_skills = extract_skills_with_scores(job_text)
    resume_skills = extract_skills_with_scores(resume_text)

    job_flat = {name: score for cat_scores in job_skills.values() for name, score in cat_scores.items()}
    resume_flat = {name: score for cat_scores in resume_skills.values() for name, score in cat_scores.items()}

    exact_match = set(job_flat.keys()) & set(resume_flat.keys())
    semantic_match, still_missing, variations = _semantic_skill_match(job_flat, resume_flat)

    all_matched = sorted(set(exact_match) | set(semantic_match))
    all_missing = sorted(set(still_missing) - set(semantic_match))

    return {
        "matching_skills": all_matched,
        "missing_skills": all_missing,
        "skill_variations": variations,
        "job_skills_count": len(job_flat),
        "resume_skills_count": len(resume_flat),
        "match_rate": round(len(all_matched) / len(job_flat) * 100, 1) if job_flat else 0,
    }


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
        "philosophy doctorate", "doctorate holder", "d.phil",
        "doctor of science", "d.sc", "d.litt",
    ],
    "Master's": [
        "master", "master's", "masters", "master's degree", "ms", "m.s",
        "m.sc", "mba", "mba degree", "msc", "msc degree", "ma", "m.a",
        "master of science", "master of arts", "master of business",
        "master of computer applications", "mca", "master degree",
        "postgraduate", "post graduate", "pg degree", "postgrad",
        "mtech", "m.tech", "m eng", "m.eng", "mtECH", "m.sc.",
        "ms in", "master's in", "ms degree", "post graduate degree",
        " postgraduate degree",
    ],
    "Bachelor's": [
        "bachelor", "bachelor's", "bachelors", "bachelor's degree",
        "bs", "b.s", "bsc", "bsc degree", "bs degree", "bachelor degree",
        "b.e", "be", "b tech", "btech", "b.tech", "bachelor of engineering",
        "bachelor of science", "bachelor of arts", "ba", "b.a",
        "undergraduate", "under grad", "ug degree",
        "bs in", "bachelor's in", "bs degree", "b.sc.", "b.sc",
        "engineering degree", "computer science degree",
        "graduated with", "graduate in", "graduated from",
        "bsc(hons)", "b.sc (hons)", "bachelor honours",
    ],
    "Associate": [
        "associate", "associate's", "associate degree", "ad", "a.s",
        "associate of science", "associate of arts", "associate degree in",
        "advanced diploma", "higher diploma", "diploma holder", "diploma in",
        "foundation degree",
    ],
    "Certificate": [
        "certificate", "certification", "certified", "certificate course",
        "professional certificate", "google certified", "aws certified",
        "microsoft certified", "comptia", "certs", "certified in",
        "certificate program", "nanodegree", "microdegree",
    ],
}

MAJOR_PATTERNS: Dict[str, List[str]] = {
    "Computer Science": [
        "computer science", "computer science", "cs", "computer sciences",
        "computing", "computational science", "computer science and engineering",
        "cs major", "computer science degree",
    ],
    "Software Engineering": [
        "software engineering", "software engineer", "se", "software development",
        "software technology", "software systems", "software design",
        "software engineering degree",
    ],
    "Information Technology": [
        "information technology", "it", "information systems", "is",
        "information technology management", "it management",
        "business it", "it solutions",
    ],
    "Data Science": [
        "data science", "data scientist", "ds", "data analytics", "analytics",
        "data engineering", "data analysis", "big data",
        "data science and analytics",
    ],
    "Artificial Intelligence": [
        "artificial intelligence", "ai", "machine learning", "ml",
        "deep learning", "neural networks", "ai ml", "intelligent systems",
        "natural language processing", "computer vision",
    ],
    "Electrical Engineering": [
        "electrical engineering", "ee", "electronics", "electronic engineering",
        "electronics and communication", "ece", "electrical and electronics",
        "power systems", "control systems",
    ],
    "Mechanical Engineering": [
        "mechanical engineering", "me", "mech", "mechanical",
        "automobile engineering", "automotive engineering", "manufacturing",
    ],
    "Civil Engineering": [
        "civil engineering", "structural engineering", "construction",
        "environmental engineering", "geotechnical",
    ],
    "Business Administration": [
        "business administration", "business management", "mba",
        "business analytics", "business studies", "commerce",
        "business", "management studies",
    ],
    "Mathematics": [
        "mathematics", "maths", "applied mathematics", "statistics",
        "math", "mathematical sciences",
    ],
    "Physics": [
        "physics", "applied physics", "theoretical physics", "astrophysics",
    ],
    "Cybersecurity": [
        "cyber security", "cybersecurity", "information security",
        "network security", "security", "cyber defense",
    ],
    "Cloud Computing": [
        "cloud computing", "cloud", "cloud architecture", "cloud services",
    ],
    "Web Development": [
        "web development", "web design", "web engineering",
        "frontend", "backend", "full stack", "fullstack",
    ],
    "Mobile Development": [
        "mobile development", "mobile computing", "ios development",
        "android development", "mobile apps",
    ],
    "Database": [
        "database", "database management", "db", "data management",
        "database systems", "dbms",
    ],
    "Networking": [
        "networking", "computer networks", "network engineering",
        "telecommunications", "communication",
    ],
}

QUALIFICATION_TYPE_PATTERNS: Dict[str, List[str]] = {
    "Bachelor of Science": [
        "bachelor of science", "b.sc", "bsc", "bs", "b.s", "bachelor science",
        "bsci", "bachelor of scientific studies",
    ],
    "Bachelor of Engineering": [
        "bachelor of engineering", "b.e", "be", "bachelor engineering",
        "bachelor of technology", "b.tech", "btech", "btECH",
        "bachelor of applied sciences",
    ],
    "Bachelor of Arts": [
        "bachelor of arts", "b.a", "ba", "bachelor arts",
        "ba hon", "ba(hons)", "bachelor of humanities",
    ],
    "Master of Science": [
        "master of science", "m.sc", "msc", "ms", "m.s", "master science",
        "msci", "master of scientific studies", "msc.",
    ],
    "Master of Engineering": [
        "master of engineering", "m.e", "me", "m.eng", "meng",
        "master of technology", "m.tech", "mtECH",
    ],
    "Master of Arts": [
        "master of arts", "m.a", "ma", "master arts",
    ],
    "Master of Business Administration": [
        "master of business administration", "mba", "executive mba",
        "international mba", "mba degree",
    ],
    "Doctor of Philosophy": [
        "doctor of philosophy", "phd", "ph.d", "ph d", "doctorate",
        "doctoral degree", "doctor of science",
    ],
}


def _build_education_semantic_db():
    global _edu_embeddings, _edu_labels, _edu_levels
    global _major_embeddings, _major_labels
    global _qual_embeddings, _qual_labels

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


def _semantic_extract_component(
    text: str,
    patterns: Dict[str, List[str]],
    embeddings: np.ndarray,
    all_labels: List[str],
    threshold: float = 0.55
) -> List[Dict[str, any]]:
    model = _get_model()
    text_lower = text.lower()

    sentences = re.split(r'[.!?\n]+', text_lower)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 8]

    if not sentences:
        return []

    text_embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)

    found = []

    for pattern_type, variants in patterns.items():
        type_indices = []
        for idx, label in enumerate(all_labels):
            for variant in variants:
                if variant in label or label in variant:
                    type_indices.append(idx)
                    break

        if not type_indices:
            continue

        type_embs = embeddings[type_indices]

        for i, sent_emb in enumerate(text_embeddings):
            similarities = type_embs @ sent_emb
            max_sim = float(np.max(similarities))

            if max_sim >= threshold:
                for variant in variants:
                    pattern = r'\b' + re.escape(variant.lower()) + r'(?:[,\s]|$|\.)'
                    if re.search(pattern, sentences[i]):
                        found.append({
                            "type": pattern_type,
                            "variant": variant,
                            "sentence": sentences[i].strip(),
                            "confidence": round(max_sim, 3),
                        })
                        break

    return found


def _keyword_extract(text: str, patterns: Dict[str, List[str]]) -> List[Dict[str, any]]:
    text_lower = text.lower()
    found = []

    for pattern_type, variants in patterns.items():
        for variant in variants:
            pattern = r'\b' + re.escape(variant.lower()) + r'(?:[,\s]|$|\.)'
            matches = list(re.finditer(pattern, text_lower))

            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(text_lower), match.end() + 50)
                context = text_lower[start:end].strip()

                found.append({
                    "type": pattern_type,
                    "variant": variant,
                    "context": context,
                    "position": match.start(),
                    "confidence": 1.0,
                })

    return found


def _build_education_entry(level: str, major: str, qual_type: str, context: str) -> Dict[str, any]:
    return {
        "level": level,
        "level_value": EDUCATION_LEVELS.get(level, 0),
        "major": major,
        "qualification_type": qual_type,
        "full_qualification": f"{qual_type} in {major}" if major and qual_type else (qual_type or level),
        "context": context,
    }


def extract_education(text: str) -> Dict[str, List[Dict[str, any]]]:
    _build_education_semantic_db()

    text_lower = text.lower()

    keyword_levels = _keyword_extract(text_lower, EDUCATION_LEVEL_PATTERNS)
    keyword_majors = _keyword_extract(text_lower, MAJOR_PATTERNS)
    keyword_quals = _keyword_extract(text_lower, QUALIFICATION_TYPE_PATTERNS)

    semantic_levels = _semantic_extract_component(
        text_lower, EDUCATION_LEVEL_PATTERNS, _edu_embeddings, _edu_labels, 0.50
    )
    semantic_majors = _semantic_extract_component(
        text_lower, MAJOR_PATTERNS, _major_embeddings, _major_labels, 0.55
    )
    semantic_quals = _semantic_extract_component(
        text_lower, QUALIFICATION_TYPE_PATTERNS, _qual_embeddings, _qual_labels, 0.55
    )

    all_levels = {item["type"]: item for item in keyword_levels}
    for item in semantic_levels:
        if item["type"] not in all_levels or item["confidence"] > all_levels[item["type"]]["confidence"]:
            all_levels[item["type"]] = {"type": item["type"], "variant": item["variant"], "confidence": item["confidence"]}

    all_majors = {item["type"]: item for item in keyword_majors}
    for item in semantic_majors:
        if item["type"] not in all_majors or item["confidence"] > all_majors[item["type"]]["confidence"]:
            all_majors[item["type"]] = {"type": item["type"], "variant": item["variant"], "confidence": item["confidence"]}

    all_quals = {item["type"]: item for item in keyword_quals}
    for item in semantic_quals:
        if item["type"] not in all_quals or item["confidence"] > all_quals[item["type"]]["confidence"]:
            all_quals[item["type"]] = {"type": item["type"], "variant": item["variant"], "confidence": item["confidence"]}

    result: Dict[str, List[Dict[str, any]]] = {edu_type: [] for edu_type in EDUCATION_LEVEL_PATTERNS}

    for level_name, level_data in all_levels.items():
        major = None
        if all_majors:
            major_data = next(iter(all_majors.values()))
            major = major_data["type"]

        qual_type = None
        if all_quals:
            qual_data = next(iter(all_quals.values()))
            qual_type = qual_data["type"]

        context = level_data.get("variant", level_name)
        if all_majors:
            major_data = next((m for m in all_majors.values() if m["confidence"] >= 0.8), None)
            if major_data:
                context += f" - {major_data['variant']}"
                major = major_data["type"]

        entry = {
            "type": level_name,
            "level": level_name,
            "level_value": EDUCATION_LEVELS.get(level_name, 0),
            "major": major,
            "qualification_type": qual_type,
            "confidence": level_data["confidence"],
            "context": context,
        }

        result[level_name].append(entry)

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

    job_flat = []
    for edu_type, items in job_education.items():
        for item in items:
            job_flat.append({
                "type": edu_type,
                "level": item.get("level"),
                "level_value": item.get("level_value"),
                "major": item.get("major"),
                "qualification_type": item.get("qualification_type"),
                "context": item.get("context"),
                "confidence": item.get("confidence"),
            })

    resume_flat = []
    for edu_type, items in resume_education.items():
        for item in items:
            resume_flat.append({
                "type": edu_type,
                "level": item.get("level"),
                "level_value": item.get("level_value"),
                "major": item.get("major"),
                "qualification_type": item.get("qualification_type"),
                "context": item.get("context"),
                "confidence": item.get("confidence"),
            })

    requirement_check = meets_requirement(job_education, resume_education)

    job_highest = get_highest_education(job_education)
    resume_highest = get_highest_education(resume_education)

    return {
        "job_education": job_flat,
        "resume_education": resume_flat,
        "job_highest": job_highest,
        "resume_highest": resume_highest,
        "meets_requirement": requirement_check["meets_requirement"],
        "meets_requirement_message": requirement_check["message"],
        "job_majors": list(set(item.get("major") for item in job_flat if item.get("major"))),
        "resume_majors": list(set(item.get("major") for item in resume_flat if item.get("major"))),
        "matching_majors": list(set(
            m for m in (set(item.get("major") for item in job_flat if item.get("major")))
            if m in set(item.get("major") for item in resume_flat if item.get("major"))
        )),
    }


EXPERIENCE_PATTERNS: Dict[str, List[str]] = {
    "Entry Level (0-1 years)": [
        "0-1 years", "0 to 1 year", "1 year", "0 years", "fresh graduate", "fresh graduate",
        "new graduate", "no experience required", "entry level", "junior", "fresher",
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
        "expert", "expert level", "senior expert", "staff", "staff engineer",
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


def _extract_experience_years(text: str) -> Dict[str, List[Dict[str, any]]]:
    text_lower = text.lower()

    title_words = {'senior', 'junior', 'lead', 'principal', 'staff', 'manager', 'director', 'head', 'chief', 'intern', 'associate'}
    context_exclude_patterns = [
        r'\bsenior\s+(software|software engineer|software developer|engineer|developer|analyst|designer|architect|consultant|manager|lead|director)',
        r'\bjunior\s+(software|software engineer|software developer|engineer|developer|analyst|designer)',
        r'\blead\s+(software|software engineer|software developer|engineer|developer|analyst|designer|manager)',
        r'\bprincipal\s+(software|software engineer|software developer|engineer|developer|architect|analyst)',
        r'\bstaff\s+(software|software engineer|software developer|engineer|developer|analyst)',
        r'\bsenior\s+(lecturer|professor|teacher|academic|faculty|researcher|research associate)',
        r'\bjunior\s+(lecturer|professor|teacher|academic|faculty|researcher)',
        r'\bsenior\s+(advisor|counselor|consultant|specialist|coordinator)',
        r'\breferences?\s*[:|-]',
        r'\breference\s+(name|contact|person)',
    ]

    found: Dict[str, List[Dict[str, any]]] = {exp_type: [] for exp_type in EXPERIENCE_PATTERNS}

    for exp_type, variants in EXPERIENCE_PATTERNS.items():
        for variant in variants:
            pattern = r'\b' + re.escape(variant.lower()) + r'\b'
            matches = list(re.finditer(pattern, text_lower))

            for match in matches:
                start_pos = match.start()
                end_pos = match.end()
                context_start = max(0, start_pos - 80)
                context_end = min(len(text_lower), end_pos + 80)
                context = text_lower[context_start:context_end].strip()

                is_title_context = any(re.search(exclude_pat, context, re.IGNORECASE) for exclude_pat in context_exclude_patterns)

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
    seen_years = set()

    for pattern, match_type in years_patterns:
        matches = list(re.finditer(pattern, text_lower))
        for match in matches:
            if match_type == 'range_years':
                years = int(match.group(2))
            else:
                years = int(match.group(1))

            if years in seen_years:
                continue
            seen_years.add(years)

            type_name = "Entry Level (0-1 years)"
            if years >= 10:
                type_name = "Expert (10+ years)"
            elif years >= 7:
                type_name = "Principal (7-10 years)"
            elif years >= 5:
                type_name = "Lead (5-7 years)"
            elif years >= 3:
                type_name = "Senior (3-5 years)"
            elif years >= 2:
                type_name = "Mid-Level (2-3 years)"
            elif years >= 1:
                type_name = "Junior (1-2 years)"
            else:
                type_name = "Entry Level (0-1 years)"

            start = max(0, match.start() - 50)
            end = min(len(text_lower), match.end() + 50)
            context = text_lower[start:end].strip()

            found.append({
                "type": type_name,
                "years": years,
                "level": EXPERIENCE_LEVELS[type_name],
                "variant": match.group(0),
                "context": context,
                "confidence": 0.98,
            })

    return found


def extract_experience_requirement(text: str) -> Dict[str, any]:
    pattern_results = _extract_experience_years(text)
    number_results = _extract_years_numbers(text)

    all_results = {exp_type: [] for exp_type in EXPERIENCE_PATTERNS}

    for exp_type, items in pattern_results.items():
        for item in items:
            all_results[exp_type].append(item)

    for item in number_results:
        exp_type = item["type"]
        if item not in all_results[exp_type]:
            all_results[exp_type].append(item)

    numeric_years = 0
    numeric_result = None

    for item in number_results:
        years_val = item.get("years")
        try:
            years = int(years_val) if years_val else 0
        except (ValueError, TypeError):
            years = 0
        if years > numeric_years:
            numeric_years = years
            numeric_result = item

    if numeric_result:
        return {
            "required_years": numeric_result.get("years"),
            "years_text": numeric_result.get("type"),
            "level": numeric_result.get("type"),
            "level_value": numeric_result.get("level"),
            "context": numeric_result.get("context"),
        }

    highest = None
    highest_level = 0
    highest_years = 0

    for exp_type, items in all_results.items():
        for item in items:
            level = item.get("level", 0)
            years_val = item.get("years")

            try:
                years = int(years_val) if years_val else 0
            except (ValueError, TypeError):
                years = 0

            if years > highest_years:
                highest_years = years
                highest_level = level
                highest = item
            elif years == highest_years and level > highest_level:
                highest_level = level
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


def compare_experience(job_text: str, resume_text: str) -> Dict[str, any]:
    job_exp = extract_experience_requirement(job_text)
    resume_exp = extract_experience_requirement(resume_text)

    job_years = job_exp.get("level_value") or 0
    resume_years = resume_exp.get("level_value") or 0

    meets = resume_years >= job_years if job_exp.get("level_value") else True

    return {
        "job_experience": job_exp,
        "resume_experience": resume_exp,
        "meets_requirement": meets,
        "meets_message": "Resume meets experience requirement" if meets else ("Resume experience is below requirement" if job_exp.get("level_value") else "No experience requirement found"),
    }