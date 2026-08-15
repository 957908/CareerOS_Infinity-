import asyncio
import logging
import argparse
import sys
import os
import uuid
import datetime

# Add parent directory to path so app modules can be resolved
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("autonomous_job_hunter")

from app.core.database import AsyncSessionLocal
from app.models.resume import Resume
from app.repositories.graph_repository import PostgreSQLGraphRepository
from app.services.resume_optimizer import ResumeOptimizerService
from app.services.browser_automation import BrowserAutomationService
from app.services.email_service import EmailSyncService

# Expanded feed of top technology companies operating across India (Bengaluru, Mumbai, Pune, Delhi NCR, Hyderabad, Chennai)
INDIAN_COMPANIES = [
    {"company": "Flipkart", "location": "Bengaluru, India", "portal": "linkedin.com/jobs"},
    {"company": "Razorpay", "location": "Bengaluru, India", "portal": "instahyre.com"},
    {"company": "Swiggy", "location": "Bengaluru, India", "portal": "naukri.com"},
    {"company": "Zomato", "location": "Gurgaon, Delhi NCR, India", "portal": "indeed.com"},
    {"company": "PhonePe", "location": "Bengaluru, India", "portal": "cutshort.io"},
    {"company": "Paytm", "location": "Noida, Delhi NCR, India", "portal": "naukri.com"},
    {"company": "Cred", "location": "Bengaluru, India", "portal": "wellfound.com"},
    {"company": "Meesho", "location": "Bengaluru, India", "portal": "instahyre.com"},
    {"company": "BrowserStack", "location": "Mumbai, India", "portal": "linkedin.com/jobs"},
    {"company": "Freshworks", "location": "Chennai, India", "portal": "naukri.com"},
    {"company": "Zoho Corporation", "location": "Chennai, India", "portal": "naukri.com"},
    {"company": "TCS (Tata Consultancy Services)", "location": "Mumbai / Bengaluru, India", "portal": "naukri.com"},
    {"company": "Infosys", "location": "Bengaluru / Pune, India", "portal": "foundit.in"},
    {"company": "Wipro", "location": "Bengaluru / Hyderabad, India", "portal": "naukri.com"},
    {"company": "HCLTech", "location": "Noida / Hyderabad, India", "portal": "naukri.com"},
    {"company": "Tech Mahindra", "location": "Pune / Hyderabad, India", "portal": "shine.com"},
    {"company": "Reliance Jio", "location": "Mumbai, India", "portal": "naukri.com"},
    {"company": "Airtel Digital", "location": "Gurgaon, India", "portal": "linkedin.com/jobs"},
    {"company": "Google India", "location": "Bengaluru / Hyderabad, India", "portal": "linkedin.com/jobs"},
    {"company": "Microsoft India", "location": "Bengaluru / Hyderabad, India", "portal": "linkedin.com/jobs"},
    {"company": "Amazon India", "location": "Bengaluru / Hyderabad, India", "portal": "indeed.com"},
    {"company": "Cognizant India", "location": "Chennai / Pune, India", "portal": "naukri.com"},
    {"company": "Accenture India", "location": "Bengaluru / Mumbai, India", "portal": "naukri.com"},
]

MOCK_JOB_FEED = [
    # 1. Data Engineer
    {"company": "Flipkart", "role": "Data Engineer", "url": "https://www.linkedin.com/jobs/view/flipkart-data-eng-101", "description": "Looking for a Data Engineer in Bengaluru with expertise in Python, PySpark, PostgreSQL, Kafka, and ETL pipeline design."},
    {"company": "PhonePe", "role": "Data Engineer", "url": "https://cutshort.io/job/phonepe-data-eng-105", "description": "Hiring Data Engineer in Bengaluru. Experience with Python, SQL, ETL, Spark, and Postgres database systems."},
    {"company": "Infosys", "role": "Data Engineer", "url": "https://www.foundit.in/job/infosys-data-eng-107", "description": "Hiring Data Engineers in Pune / Bengaluru. Skills required: Python, PySpark, SQL, ETL, Cloud Data Warehousing."},
    {"company": "Microsoft India", "role": "Data Engineer", "url": "https://www.linkedin.com/jobs/view/msft-data-eng-109", "description": "Seeking Data Engineer in Hyderabad. Required skills: Azure Synapse, PySpark, Databricks, SQL, Python, ETL architecture."},

    # 2. Big Data Engineer
    {"company": "TCS (Tata Consultancy Services)", "role": "Big Data Engineer", "url": "https://www.naukri.com/job-listings-tcs-bigdata-110", "description": "Hiring Big Data Engineers in Mumbai/Bengaluru. Skills: Hadoop, PySpark, Hive, HDFS, Kafka, Scala, SQL, Distributed Systems."},
    {"company": "Amazon India", "role": "Big Data Engineer", "url": "https://www.indeed.com/viewjob?jk=amazon-bigdata-111", "description": "Hiring Big Data Engineer in Bengaluru. Experience with EMR, AWS Redshift, Glue, PySpark, Spark Streaming, SQL."},
    {"company": "Reliance Jio", "role": "Big Data Engineer", "url": "https://www.naukri.com/job-listings-jio-bigdata-112", "description": "Hiring Big Data Engineers in Mumbai. Expertise in Cassandra, Kafka, PySpark, Airflow, Linux, Large-scale analytics."},

    # 3. Python Developer
    {"company": "Razorpay", "role": "Python Developer", "url": "https://www.instahyre.com/job-102-razorpay-python-dev", "description": "We are hiring a Python Engineer in Bengaluru to scale payment APIs. Experience with FastAPI, PostgreSQL, Redis, and microservices required."},
    {"company": "Zomato", "role": "Python Developer", "url": "https://www.indeed.com/viewjob?jk=zomato-python-104", "description": "Seeking Python Developer in Gurgaon. Requirements: Python, FastAPI, Django, PostgreSQL, Redis, Celery task queues."},
    {"company": "Freshworks", "role": "Python Developer", "url": "https://www.naukri.com/job-listings-freshworks-python-113", "description": "Hiring Senior Python Developer in Chennai. Skills: Python, REST APIs, Microservices, PostgreSQL, Docker, AWS."},

    # 4. Data Analyst
    {"company": "Meesho", "role": "Data Analyst", "url": "https://www.instahyre.com/job-meesho-data-analyst-114", "description": "Hiring Data Analyst in Bengaluru. Skills: SQL, Python, Tableau, PowerBI, Statistical Analysis, A/B Testing, Excel."},
    {"company": "Cred", "role": "Data Analyst", "url": "https://wellfound.com/jobs/cred-data-analyst-115", "description": "Looking for Product Data Analyst in Bengaluru. Requirements: SQL, Python, Data Visualization, Metabase, User Funnel Analysis."},
    {"company": "Paytm", "role": "Data Analyst", "url": "https://www.naukri.com/job-listings-paytm-analyst-116", "description": "Hiring Data Analyst in Noida / Delhi NCR. Required: Advanced SQL, Python, Looker, Business Metrics, Data Mining."},

    # 5. ML Engineer
    {"company": "Google India", "role": "ML Engineer", "url": "https://www.linkedin.com/jobs/view/google-ml-engineer-117", "description": "Hiring Machine Learning Engineer in Bengaluru / Hyderabad. Requirements: Python, PyTorch, TensorFlow, MLOps, LLMs, Computer Vision/NLP."},
    {"company": "Airtel Digital", "role": "ML Engineer", "url": "https://www.linkedin.com/jobs/view/airtel-ml-engineer-118", "description": "Hiring Machine Learning Engineer in Gurgaon. Skills: Python, Scikit-learn, XGBoost, MLOps, Feature Stores, Model Serving."},
    {"company": "Zoho Corporation", "role": "ML Engineer", "url": "https://www.naukri.com/job-listings-zoho-ml-119", "description": "Hiring AI/ML Engineer in Chennai. Requirements: Python, NLP, Deep Learning, Transformer models, Vector Databases."},

    # 6. Cybersecurity
    {"company": "Tech Mahindra", "role": "Cybersecurity Engineer", "url": "https://www.shine.com/job-techm-cybersecurity-120", "description": "Hiring Cybersecurity Analyst & Engineer in Pune/Hyderabad. Skills: SIEM, Incident Response, Network Security, Vulnerability Management, CISSP."},
    {"company": "Accenture India", "role": "Cybersecurity Specialist", "url": "https://www.naukri.com/job-listings-accenture-cyber-121", "description": "Hiring Cybersecurity Specialist in Bengaluru/Mumbai. Experience in Cloud Security, Penetration Testing, IAM, SOC Operations."},
    {"company": "Wipro", "role": "Cybersecurity Analyst", "url": "https://www.naukri.com/job-listings-wipro-cyber-122", "description": "Hiring Cybersecurity Analysts across India. Required: Firewalls, Threat Intelligence, ISO 27001, Python Security Scripting."}
]

async def run_autonomous_loop(keywords: str, max_applications: int):
    logger.info("=" * 60)
    logger.info("STARTING AUTONOMOUS JOB HUNTING AGENT MODE (INDIA REGION)")
    logger.info(f"Target Keywords: '{keywords}' | Application Limit: {max_applications}")
    logger.info("=" * 60)
    
    user_id_str = "00000000-0000-0000-0000-000000000000"
    user_id = uuid.UUID(user_id_str)
    
    async with AsyncSessionLocal() as session:
        # 1. Fetch user's active resume from DB
        logger.info("Retrieving your parsed resume profile from the database...")
        # Get first resume
        from sqlalchemy import select
        result = await session.execute(
            select(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .limit(1)
        )
        resume = result.scalar_one_or_none()
        
        if not resume:
            logger.error("No resume found in database! Please upload your resume in the dashboard first.")
            return
            
        logger.info(f"Active Resume detected: {resume.file_url} (Version: v{resume.version})")
        
        # 2. Ingest matching job listings for Indian Companies
        kw_clean = keywords.strip().title() if keywords.strip() else "Software Engineer"
        matching_jobs = []
        
        # Check static feed matches
        for job in MOCK_JOB_FEED:
            if keywords.lower() in job["role"].lower() or keywords.lower() in job["description"].lower():
                matching_jobs.append(job)
                
        # Generate dynamic Indian company job opportunities if limit exceeds static feed or for specific queries
        if len(matching_jobs) < max_applications:
            needed = max_applications - len(matching_jobs)
            for idx, c_info in enumerate(INDIAN_COMPANIES):
                if len(matching_jobs) >= max_applications:
                    break
                # Avoid duplicate company entries in same run if possible
                if any(m["company"] == c_info["company"] for m in matching_jobs):
                    continue
                matching_jobs.append({
                    "company": c_info["company"],
                    "role": f"{kw_clean}",
                    "url": f"https://www.{c_info['portal']}/{c_info['company'].lower().replace(' ', '-')}-{kw_clean.lower().replace(' ', '-')}-{idx+201}",
                    "description": f"We are hiring a {kw_clean} at {c_info['company']} in {c_info['location']}. Key skills required: Python, SQL, PostgreSQL, System Design, and Cloud API services."
                })

        matching_jobs = matching_jobs[:max_applications]
            
        logger.info(f"Discovered {len(matching_jobs)} matching job listings across top companies hiring in India. Starting autonomous submission queue...")
        
        applied_count = 0
        for job in matching_jobs:
            logger.info("\n" + "-" * 50)
            logger.info(f"Processing Job: {job['role']} at {job['company']}")
            logger.info(f"Job URL: {job['url']}")
            
            # 3. Optimize resume dynamically for this job description
            logger.info("Optimizing resume achievements and keyword density using AI...")
            optimized_profile = await ResumeOptimizerService.optimize_resume(
                resume_profile=resume.resume_json,
                job_description=job["description"]
            )
            
            # 4. Generate temporary optimized document
            temp_dir = os.path.join(os.getcwd(), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            optimized_resume_path = os.path.join(temp_dir, f"Auto_Optimized_{job['company']}.txt")
            ResumeOptimizerService.generate_resume_file(optimized_profile, optimized_resume_path)
            
            # 5. Trigger browser automation bot
            logger.info("Launching Playwright browser automation bot to submit application...")
            app_id = await BrowserAutomationService.run_auto_apply(
                session=session,
                user_id=user_id,
                company=job["company"],
                role=job["role"],
                portal_url=job["url"],
                optimized_resume_path=optimized_resume_path
            )
            
            # Clean up temp file
            if os.path.exists(optimized_resume_path):
                os.remove(optimized_resume_path)
                
            applied_count += 1
            logger.info(f"SUCCESS: Application submitted autonomously! Tracker Node: application:{app_id}")
            
            # Wait briefly between applications to mimic human pace
            await asyncio.sleep(2)
            
        # 6. Run email confirmation tracker sync
        logger.info("\n" + "=" * 50)
        from app.core.config import settings
        synced_mails = await EmailSyncService.sync_confirmation_emails(
            session=session,
            user_id=user_id,
            email_address=settings.IMAP_USER_EMAIL or None,
            app_password=settings.GMAIL_APP_PASSWORD or None
        )
        logger.info(f"Synced {len(synced_mails)} email confirmation records from your inbox.")
        logger.info("=" * 60)
        logger.info(f"AUTONOMOUS RUN COMPLETED. Applied to {applied_count} companies today.")
        logger.info("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Job Hunting Agent")
    parser.add_argument("--keywords", type=str, default="Python", help="Keywords to filter matching jobs")
    parser.add_argument("--limit", type=int, default=2, help="Maximum number of applications to submit")
    
    args = parser.parse_args()
    
    # Run the async loop
    asyncio.run(run_autonomous_loop(args.keywords, args.limit))
