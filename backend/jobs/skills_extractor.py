import re
import threading
from typing import Dict, List, Set, Optional, Tuple

import numpy as np

_model = None
_lock = threading.Lock()
_skill_embeddings: Optional[np.ndarray] = None
_skill_labels: Optional[List[str]] = None
_skill_variants: Optional[Dict[str, List[str]]] = None

SKILL_THRESHOLD = 0.55
MATCH_THRESHOLD = 0.70

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