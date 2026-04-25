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


EDUCATION_PATTERNS: Dict[str, List[str]] = {
    "PhD": [
        "phd", "ph.d", "ph d", "doctor of philosophy", "doctorate",
        "doctoral", "phd degree", "doctorate degree", "phd in computer science",
        "phd in mathematics", "phd in engineering", "phd in data science",
        "philosophy doctorate", "doctorate holder",
    ],
    "Master's": [
        "master", "master's", "masters", "master's degree", "ms", "m.s",
        "m.sc", "mba", "mba degree", "msc", "msc degree", "ma", "m.a",
        "master of science", "master of arts", "master of business",
        "master of computer applications", "mca", "master degree",
        "postgraduate", "post graduate", "pg degree", "postgrad",
        "mtech", "m.tech", "m eng", "m.eng", "mtECH",
        "ms in computer science", "master's in", "ms degree",
    ],
    "Bachelor's": [
        "bachelor", "bachelor's", "bachelors", "bachelor's degree",
        "bs", "b.s", "bsc", "bsc degree", "bs degree", "bachelor degree",
        "b.e", "be", "b tech", "btech", "b.tech", "bachelor of engineering",
        "bachelor of science", "bachelor of arts", "ba", "b.a",
        "undergraduate", "under grad", "ug degree",
        "bs in computer science", "bachelor's in", "bs degree",
        "engineering degree", "computer science degree",
        "graduated with", "b.sc", "b sc",
    ],
    "Associate": [
        "associate", "associate's", "associate degree", "ad", "a.s",
        "associate of science", "associate of arts", "diploma",
        "advanced diploma", "higher diploma", "diploma holder",
    ],
    "Certificate": [
        "certificate", "certification", "certified", "certificate course",
        "professional certificate", "google certified", "aws certified",
        "microsoft certified", "comptia", "certs", "certified in",
    ],
}

EDUCATION_LEVELS: Dict[str, int] = {
    "Certificate": 1,
    "Associate": 2,
    "Bachelor's": 3,
    "Master's": 4,
    "PhD": 5,
}


def _build_education_database():
    global _edu_embeddings, _edu_labels, _edu_levels

    if _edu_embeddings is not None:
        return

    model = _get_model()

    all_labels: List[str] = []
    for edu_type, variants in EDUCATION_PATTERNS.items():
        for variant in variants:
            all_labels.append(variant.lower().strip())

    _edu_labels = all_labels
    _edu_levels = EDUCATION_LEVELS
    _edu_embeddings = model.encode(all_labels, convert_to_numpy=True, show_progress_bar=False)


def _extract_education_keywords(text: str) -> Dict[str, List[Dict[str, any]]]:
    found_education: Dict[str, List[Dict[str, any]]] = {edu_type: [] for edu_type in EDUCATION_PATTERNS}

    text_lower = text.lower()

    for edu_type, variants in EDUCATION_PATTERNS.items():
        for variant in variants:
            pattern = r'\b' + re.escape(variant.lower()) + r'(?:[,\s]|$|\.)'
            matches = list(re.finditer(pattern, text_lower))

            for match in matches:
                start_pos = max(0, match.start() - 100)
                end_pos = min(len(text_lower), match.end() + 100)
                context = text_lower[start_pos:end_pos].strip()

                found_entry = {
                    "type": edu_type,
                    "level": EDUCATION_LEVELS[edu_type],
                    "confidence": 1.0,
                    "context": context,
                    "matched_variant": variant,
                    "position": match.start(),
                }

                if found_entry not in found_education[edu_type]:
                    found_education[edu_type].append(found_entry)

    return {edu_type: items for edu_type, items in found_education.items() if items}


def _semantic_education_verify(text: str, education_data: Dict[str, List[Dict[str, any]]]) -> Dict[str, List[Dict[str, any]]]:
    _build_education_database()

    model = _get_model()
    text_lower = text.lower()

    sentences = re.split(r'[.!?\n]+', text_lower)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    sentences = [s for s in sentences if any(v.lower() in s for cat in EDUCATION_PATTERNS.values() for v in cat)]

    if not sentences:
        return education_data

    text_embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)

    verified_types = set()

    for edu_type, variants in EDUCATION_PATTERNS.items():
        type_indices = []
        for idx, label in enumerate(_edu_labels):
            for variant in variants:
                if variant in label or label in variant:
                    type_indices.append(idx)

        if not type_indices:
            continue

        type_embeddings = _edu_embeddings[type_indices]

        for i, sentence_emb in enumerate(text_embeddings):
            similarities = type_embeddings @ sentence_emb
            max_sim = float(np.max(similarities))

            if max_sim >= 0.50:
                for variant in variants:
                    pattern = r'\b' + re.escape(variant.lower()) + r'\b'
                    if re.search(pattern, sentences[i]):
                        if edu_type not in verified_types:
                            verified_types.add(edu_type)

                        already_found = any(
                            e["type"] == edu_type and e["matched_variant"] == variant
                            for items in education_data.values()
                            for e in items
                        )

                        if not already_found:
                            context_start = max(0, i - 1)
                            context_end = min(len(sentences), i + 2)
                            context = " ".join(sentences[context_start:context_end])

                            education_data.setdefault(edu_type, []).append({
                                "type": edu_type,
                                "level": EDUCATION_LEVELS[edu_type],
                                "confidence": round(max_sim, 3),
                                "context": context.strip(),
                                "matched_variant": variant,
                            })

                        break

    return education_data


def extract_education(text: str) -> Dict[str, List[Dict[str, any]]]:
    keyword_results = _extract_education_keywords(text)

    result = _semantic_education_verify(text, keyword_results)

    return {edu_type: items for edu_type, items in result.items() if items}


def get_highest_education(education_data: Dict[str, List[Dict[str, any]]]) -> Optional[Dict[str, any]]:
    if not education_data:
        return None

    highest = None
    highest_level = 0

    for edu_type, items in education_data.items():
        for item in items:
            if item["level"] > highest_level:
                highest_level = item["level"]
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

    meets = resume_highest["level"] >= job_highest["level"]

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
                "level": item["level"],
                "context": item["context"],
                "confidence": item["confidence"],
            })

    resume_flat = []
    for edu_type, items in resume_education.items():
        for item in items:
            resume_flat.append({
                "type": edu_type,
                "level": item["level"],
                "context": item["context"],
                "confidence": item["confidence"],
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
    }