"""
MockJobSource — Deterministic mock job source adapter for offline testing & simulation runs.
"""
import logging
from typing import Optional, List
from app.services.job_sources.base import JobSourceBase, RawJobData

logger = logging.getLogger("app.services.job_sources.mock")


class MockJobSource(JobSourceBase):
    """
    Deterministic mock provider for testing 100-job discovery simulations and E2E flows.
    """

    @property
    def source_name(self) -> str:
        return "mock"

    async def discover(self, query: str, **kwargs) -> List[RawJobData]:
        count = kwargs.get("count", 10)
        jobs = []

        indian_tech_companies = [
            ("Flipkart", "Bengaluru, India"),
            ("Razorpay", "Bengaluru, India"),
            ("Swiggy", "Bengaluru, India"),
            ("Zomato", "Gurgaon, India"),
            ("PhonePe", "Bengaluru, India"),
            ("Paytm", "Noida, India"),
            ("Cred", "Bengaluru, India"),
            ("Meesho", "Bengaluru, India"),
            ("BrowserStack", "Mumbai, India"),
            ("Freshworks", "Chennai, India"),
            ("Zoho Corporation", "Chennai, India"),
            ("TCS", "Mumbai, India"),
            ("Infosys", "Bengaluru, India"),
            ("Wipro", "Hyderabad, India"),
            ("HCLTech", "Noida, India"),
            ("Tech Mahindra", "Pune, India"),
            ("Reliance Jio", "Mumbai, India"),
            ("Airtel Digital", "Gurgaon, India"),
            ("Google India", "Bengaluru, India"),
            ("Microsoft India", "Hyderabad, India"),
        ]

        roles = [
            ("Backend Engineer", ["Python", "FastAPI", "PostgreSQL", "Docker", "Kafka", "AWS"]),
            ("Senior Python Developer", ["Python", "Django", "PostgreSQL", "Redis", "AWS"]),
            ("Full Stack Engineer", ["Python", "FastAPI", "React", "PostgreSQL", "Docker"]),
            ("Data Engineer", ["Python", "Spark", "Kafka", "Airflow", "Snowflake", "PostgreSQL"]),
            ("DevOps Lead", ["Docker", "Kubernetes", "AWS", "Terraform", "Python"]),
        ]

        q_clean = query.strip().title() if query and query.strip() else ""

        for i in range(count):
            role_idx = i % len(roles)
            comp_idx = i % len(indian_tech_companies)
            comp, loc = indian_tech_companies[comp_idx]
            
            title_base, skills = roles[role_idx]
            title = f"{q_clean} / {title_base}" if q_clean else title_base
            j_id = f"IND-{i+1:03d}"

            desc = (
                f"We are hiring a {title} at {comp} in {loc}. "
                f"Requirements: {', '.join(skills)}. "
                "Build scalable cloud applications across Indian tech ecosystem."
            )

            jobs.append(
                RawJobData(
                    source="mock",
                    source_job_id=j_id,
                    source_url=f"https://jobsearch.india.example.com/view/{j_id}",
                    title=title,
                    company=comp,
                    description=desc,
                    location=loc,
                    employment_type="FULL_TIME",
                    work_mode="HYBRID",
                    salary_raw="₹15,00,000 - ₹35,00,000 CTC",
                    posted_at_raw="2026-08-14",
                    extra_metadata={"required_skills": skills[:4], "preferred_skills": skills[4:]}
                )
            )

        return jobs

    async def fetch(self, source_job_id: str, source_url: Optional[str] = None) -> RawJobData:
        return RawJobData(
            source="mock",
            source_job_id=source_job_id,
            source_url=source_url or f"https://mockjobs.example.com/view/{source_job_id}",
            title="Senior Python Backend Engineer",
            company="Acme Corp",
            description="Seeking Python, FastAPI, PostgreSQL, Docker, Kafka, AWS engineer.",
            location="Remote",
            employment_type="FULL_TIME",
            work_mode="REMOTE",
            salary_raw="$140,000",
            posted_at_raw="2026-08-12",
            extra_metadata={"required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kafka"], "preferred_skills": ["AWS"]}
        )

    def normalize(self, raw: dict) -> RawJobData:
        return RawJobData(
            source="mock",
            source_job_id=raw.get("id", "MOCK-001"),
            source_url=raw.get("url"),
            title=raw.get("title", "Software Engineer"),
            company=raw.get("company", "Tech Company"),
            description=raw.get("description", ""),
            location=raw.get("location"),
            employment_type=raw.get("employment_type"),
            work_mode=raw.get("work_mode"),
            salary_raw=raw.get("salary"),
        )
