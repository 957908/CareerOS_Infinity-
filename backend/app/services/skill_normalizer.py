"""
SkillNormalizerService — Canonical skill identity resolution.

Normalizes skill names from job descriptions and user input into
canonical lowercase identifiers. Job-level normalization only —
NEVER modifies the user's canonical profile or UserSkill records.
"""
import logging
import re
from typing import Optional

logger = logging.getLogger("app.services.skill_normalizer")

# Canonical skill aliases map: alias → canonical
# Extend this dictionary as needed.
_SKILL_ALIASES: dict[str, str] = {
    # Python ecosystem
    "python": "python",
    "python3": "python",
    "python 3": "python",
    "python3.x": "python",
    "py": "python",

    # FastAPI / Django / Flask
    "fastapi": "fastapi",
    "fast api": "fastapi",
    "django": "django",
    "flask": "flask",

    # JavaScript / TypeScript
    "javascript": "javascript",
    "js": "javascript",
    "typescript": "typescript",
    "ts": "typescript",

    # React
    "react": "react",
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",

    # Next.js
    "next.js": "nextjs",
    "nextjs": "nextjs",
    "next js": "nextjs",

    # Node.js
    "node.js": "nodejs",
    "nodejs": "nodejs",
    "node js": "nodejs",
    "node": "nodejs",

    # Vue
    "vue.js": "vue",
    "vuejs": "vue",

    # Databases
    "postgresql": "postgresql",
    "postgres": "postgresql",
    "postgresdb": "postgresql",
    "pg": "postgresql",
    "mysql": "mysql",
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "redis": "redis",
    "elasticsearch": "elasticsearch",
    "elastic search": "elasticsearch",
    "cassandra": "cassandra",
    "dynamodb": "dynamodb",
    "firebase": "firebase",
    "sqlite": "sqlite",

    # Java ecosystem
    "java": "java",
    "spring": "spring",
    "spring boot": "spring boot",
    "springboot": "spring boot",
    "hibernate": "hibernate",

    # Kotlin / Scala
    "kotlin": "kotlin",
    "scala": "scala",

    # Go
    "go": "go",
    "golang": "go",

    # Rust
    "rust": "rust",

    # C/C++
    "c++": "c++",
    "cpp": "c++",
    "c": "c",

    # Cloud
    "aws": "aws",
    "amazon web services": "aws",
    "gcp": "gcp",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "azure": "azure",
    "microsoft azure": "azure",

    # DevOps / Infra
    "docker": "docker",
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "helm": "helm",
    "terraform": "terraform",
    "ansible": "ansible",
    "jenkins": "jenkins",
    "github actions": "github actions",
    "gitlab ci": "gitlab ci",
    "ci/cd": "ci/cd",
    "nginx": "nginx",
    "apache": "apache",
    "linux": "linux",
    "ubuntu": "ubuntu",

    # Data / ML
    "spark": "spark",
    "apache spark": "spark",
    "pyspark": "spark",
    "kafka": "kafka",
    "apache kafka": "kafka",
    "airflow": "airflow",
    "apache airflow": "airflow",
    "hadoop": "hadoop",
    "hive": "hive",
    "flink": "flink",
    "dbt": "dbt",
    "databricks": "databricks",
    "snowflake": "snowflake",
    "pandas": "pandas",
    "numpy": "numpy",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "torch": "pytorch",
    "keras": "keras",
    "langchain": "langchain",
    "openai": "openai",

    # SQL
    "sql": "sql",
    "nosql": "nosql",
    "plsql": "pl/sql",
    "pl/sql": "pl/sql",
    "t-sql": "t-sql",

    # Celery
    "celery": "celery",

    # RabbitMQ
    "rabbitmq": "rabbitmq",

    # GraphQL
    "graphql": "graphql",
    "graph ql": "graphql",

    # REST
    "rest": "rest api",
    "rest api": "rest api",
    "restful": "rest api",
    "restful api": "rest api",

    # Microservices
    "microservices": "microservices",
    "micro services": "microservices",

    # Git
    "git": "git",
    "github": "github",
    "gitlab": "gitlab",
    "bitbucket": "bitbucket",

    # Testing
    "pytest": "pytest",
    "jest": "jest",
    "junit": "junit",
    "selenium": "selenium",
    "cypress": "cypress",

    # Communication / soft skills (normalized for consistent output)
    "communication": "communication",
    "teamwork": "teamwork",
    "leadership": "leadership",
    "problem solving": "problem solving",
    "problem-solving": "problem solving",
    "agile": "agile",
    "scrum": "scrum",
}

# Skills that must NOT be confused
_DO_NOT_EQUATE = [
    ("python", "pytorch"),
    ("java", "javascript"),
    ("sql", "postgresql"),
    ("sql", "mysql"),
    ("sql", "nosql"),
    ("react", "reactnative"),
]


class SkillNormalizerService:
    """
    Normalizes skill names to canonical lowercase identifiers.
    Used for JD skill extraction — NEVER for modifying user profiles.
    """

    @staticmethod
    def normalize(skill: str) -> str:
        """
        Normalize a single skill string to its canonical form.
        Returns the canonical identifier or the lowercased input if no mapping found.
        """
        if not skill or not skill.strip():
            return ""
        cleaned = skill.strip().lower()
        cleaned = re.sub(r"\s+", " ", cleaned)
        canonical = _SKILL_ALIASES.get(cleaned, cleaned)
        return canonical

    @staticmethod
    def normalize_list(skills: list[str]) -> list[str]:
        """Normalize and deduplicate a list of skill strings."""
        normalized = []
        seen = set()
        for s in skills:
            n = SkillNormalizerService.normalize(s)
            if n and n not in seen:
                normalized.append(n)
                seen.add(n)
        return normalized

    @staticmethod
    def match_skills(
        user_skills: list[str],
        job_required: list[str],
        job_preferred: list[str]
    ) -> dict:
        """
        Compare normalized user skills against job requirements.
        Returns matched/missing split — NEVER modifies user_skills.

        Args:
            user_skills: List of normalized canonical skill names from user profile
            job_required: List of normalized required skills from JD
            job_preferred: List of normalized preferred skills from JD

        Returns:
            {
                matched_required: [...],
                missing_required: [...],
                matched_preferred: [...],
                missing_preferred: [...],
                skill_match_score: float (0.0 - 100.0)
            }
        """
        user_set = set(SkillNormalizerService.normalize_list(user_skills))
        req_set = set(SkillNormalizerService.normalize_list(job_required))
        pref_set = set(SkillNormalizerService.normalize_list(job_preferred))

        matched_req = sorted(user_set & req_set)
        missing_req = sorted(req_set - user_set)
        matched_pref = sorted(user_set & pref_set)
        missing_pref = sorted(pref_set - user_set)

        # Score: weighted towards required skills
        req_count = len(req_set)
        pref_count = len(pref_set)
        total_weight = (req_count * 1.0) + (pref_count * 0.5)

        if total_weight == 0:
            skill_score = 50.0  # neutral when no requirements specified
        else:
            matched_weight = (len(matched_req) * 1.0) + (len(matched_pref) * 0.5)
            skill_score = min(100.0, (matched_weight / total_weight) * 100.0)

        return {
            "matched_required": matched_req,
            "missing_required": missing_req,
            "matched_preferred": matched_pref,
            "missing_preferred": missing_pref,
            "skill_match_score": round(skill_score, 2),
        }
