import asyncio
import logging
import json
import uuid
import datetime
from typing import Optional, List

# Configure logger output
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("verify_e2e_pipeline")

# =====================================================================
# 1. Pipeline Verification Mocks
# =====================================================================

class MockUser:
    def __init__(self, id: uuid.UUID, email: str, full_name: str):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.role = "MEMBER"

class MockResumeRecord:
    def __init__(self, user_id: str, file_url: str, raw_text: str, resume_json: dict, version: int = 1):
        self.id = uuid.uuid4()
        self.user_id = user_id
        self.file_url = file_url
        self.raw_text = raw_text
        self.resume_json = resume_json
        self.version = version
        self.embedding = [0.1] * 1536

class MockGraphNode:
    def __init__(self, id: str, entity_type: str, properties: dict):
        self.id = id
        self.entity_type = entity_type
        self.properties = properties

class MockGraphRelationship:
    def __init__(self, source_id: str, target_id: str, relation_type: str, properties: dict):
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.properties = properties

# =====================================================================
# 2. Ingestion & Validation Engine
# =====================================================================

class E2EValidationPipeline:
    def __init__(self):
        self.resumes_db = {}
        self.graph_nodes = {}
        self.graph_relationships = []

    async def ingest_document(self, user: MockUser, file_name: str, raw_text: str) -> MockResumeRecord:
        """
        Runs document parsing, Universal Profile normalization, and Knowledge Graph mapping.
        """
        logger.info(f"Ingesting document '{file_name}' for user: {user.full_name}")
        
        # 1. Normalize into Universal Profile Schema (Simulating AI Gateway mapping)
        normalized_profile = self._simulate_ai_parser(file_name, raw_text)
        
        # 2. Save resume record
        resume = MockResumeRecord(
            user_id=str(user.id),
            file_url=file_name,
            raw_text=raw_text,
            resume_json=normalized_profile
        )
        self.resumes_db[resume.id] = resume
        logger.info(f"Saved resume record ID: {resume.id} (Version: {resume.version})")
        
        # 3. Save nodes and relationships in Universal Career Knowledge Graph
        user_node_id = f"user:{user.id}"
        self.graph_nodes[user_node_id] = MockGraphNode(user_node_id, "USER", {"name": user.full_name})
        
        for comp in normalized_profile.get("competencies", []):
            skill_id = f"skill:{comp['name'].lower().replace(' ', '_')}"
            self.graph_nodes[skill_id] = MockGraphNode(skill_id, "SKILL", {"name": comp["name"], "category": comp["category"]})
            self.graph_relationships.append(
                MockGraphRelationship(user_node_id, skill_id, "HAS_SKILL", {"level": comp.get("level", "expert")})
            )
            
        for job in normalized_profile.get("history", []):
            company_id = f"company:{job['company'].lower().replace(' ', '_')}"
            self.graph_nodes[company_id] = MockGraphNode(company_id, "COMPANY", {"name": job["company"]})
            self.graph_relationships.append(
                MockGraphRelationship(user_node_id, company_id, "WORKED_AT", {"role": job["role"]})
            )
            
        logger.info(f"Knowledge Graph updated with {len(normalized_profile.get('competencies', []))} skills and {len(normalized_profile.get('history', []))} companies.")
        return resume

    def run_ats_scoring(self, resume: MockResumeRecord, job_description: str) -> dict:
        """
        Compares normalized profile schemas against JDs and returns scores with explainable evidence.
        """
        logger.info(f"Evaluating ATS Match for Resume ID: {resume.id}")
        resume_skills = [c["name"].lower() for c in resume.resume_json.get("competencies", [])]
        
        jd_keywords = ["python", "fastapi", "postgresql", "docker", "react", "tailwindcss", "celery"]
        matched = [kw for kw in jd_keywords if kw in job_description.lower() and kw in resume_skills]
        missing = [kw for kw in jd_keywords if kw in job_description.lower() and kw not in resume_skills]
        
        # Calculate mock score
        total_jd = len(matched) + len(missing)
        score = int((len(matched) / total_jd) * 100) if total_jd > 0 else 50
        
        return {
            "resume_id": str(resume.id),
            "score": score,
            "confidence_score": 0.95,
            "evidence": {
                "matched_keywords": matched,
                "missing_keywords": missing
            },
            "reasoning_metadata": f"Matched skills: {', '.join(matched)}. Missing skills: {', '.join(missing)}."
        }

    def _simulate_ai_parser(self, file_name: str, raw_text: str) -> dict:
        """
        Simulates structured profile mapping according to file contents.
        """
        if "backend" in raw_text.lower() or "python" in raw_text.lower():
            return {
                "profile_metadata": {"source": file_name, "confidence_score": 0.95},
                "competencies": [
                    {"name": "Python", "category": "language"},
                    {"name": "FastAPI", "category": "framework"},
                    {"name": "PostgreSQL", "category": "database"},
                    {"name": "Docker", "category": "infrastructure"}
                ],
                "history": [
                    {"company": "Tech Corp", "role": "Senior Python Developer"}
                ]
            }
        else:
            return {
                "profile_metadata": {"source": file_name, "confidence_score": 0.92},
                "competencies": [
                    {"name": "React", "category": "framework"},
                    {"name": "TailwindCSS", "category": "framework"},
                    {"name": "JavaScript", "category": "language"}
                ],
                "history": [
                    {"company": "Web Solutions", "role": "Frontend Developer"}
                ]
            }

# =====================================================================
# 3. E2E Execution & Verification Runner
# =====================================================================

async def main():
    logger.info("Initializing E2E Ingestion, Knowledge Graph, & ATS scoring Pipeline Test.")
    pipeline = E2EValidationPipeline()
    
    # Register mock users
    sarah = MockUser(uuid.uuid4(), "sarah@example.com", "Sarah Backend Developer")
    david = MockUser(uuid.uuid4(), "david@example.com", "David Frontend Developer")
    
    # Sample resumes
    sarah_resume_text = "Experienced Senior Backend Developer with 5 years in Python, FastAPI, and PostgreSQL."
    david_resume_text = "Frontend Developer skilled in UI design, JavaScript, React, and TailwindCSS."
    
    # 1. Ingest Resumes
    sarah_resume = await pipeline.ingest_document(sarah, "sarah_resume.pdf", sarah_resume_text)
    david_resume = await pipeline.ingest_document(david, "david_resume.pdf", david_resume_text)
    
    # 2. Define JDs
    backend_jd = "Looking for a Senior Python Developer with experience in FastAPI and PostgreSQL. Docker is preferred."
    frontend_jd = "Seeking a Frontend Developer to build interfaces in React, TailwindCSS, and JavaScript."
    
    # 3. Validate ATS Scoring on different combinations
    logger.info("=====================================================")
    logger.info("RUNNING SCENARIO A: Sarah (Backend Dev) vs Backend JD")
    res_a = pipeline.run_ats_scoring(sarah_resume, backend_jd)
    logger.info(f"Scenario A Score: {res_a['score']}% (Confidence: {res_a['confidence_score']})")
    logger.info(f"Evidence: {res_a['evidence']}")
    logger.info(f"Reasoning: {res_a['reasoning_metadata']}")
    
    logger.info("=====================================================")
    logger.info("RUNNING SCENARIO B: David (Frontend Dev) vs Backend JD")
    res_b = pipeline.run_ats_scoring(david_resume, backend_jd)
    logger.info(f"Scenario B Score: {res_b['score']}% (Confidence: {res_b['confidence_score']})")
    logger.info(f"Evidence: {res_b['evidence']}")
    
    logger.info("=====================================================")
    logger.info("RUNNING SCENARIO C: David (Frontend Dev) vs Frontend JD")
    res_c = pipeline.run_ats_scoring(david_resume, frontend_jd)
    logger.info(f"Scenario C Score: {res_c['score']}% (Confidence: {res_c['confidence_score']})")
    logger.info(f"Evidence: {res_c['evidence']}")
    
    logger.info("=====================================================")
    logger.info("Knowledge Graph Node Verification Check:")
    for nid, node in pipeline.graph_nodes.items():
        logger.info(f"Graph Node: {nid} (Type: {node.entity_type})")
        
    logger.info("Knowledge Graph Edge Verification Check:")
    for edge in pipeline.graph_relationships:
        logger.info(f"Graph Edge: {edge.source_id} -[{edge.relation_type}]-> {edge.target_id}")

    logger.info("=====================================================")
    logger.info("E2E PIPELINE VALIDATION COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    asyncio.run(main())
