import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.ai_gateway import AIGateway
from app.core.prompts import PromptLibrary
from app.models.resume import Resume
from app.core.exceptions import NotFoundError

logger = logging.getLogger("app.services.ats_service")

class ATSService:
    """
    ATS score analytics engine executing semantic alignment calculations.
    Returns explainable matches featuring evidence and reasoning metadata.
    """
    @staticmethod
    async def analyze_job_match(
        session: AsyncSession,
        resume_id: str,
        job_description: str
    ) -> dict:
        logger.info(f"ATSService: evaluating match for resume ID: {resume_id}")
        
        # Load resume record
        resume = await session.get(Resume, resume_id)
        if not resume:
            logger.warning(f"Resume ID not found: {resume_id}")
            raise NotFoundError("The specified resume record could not be found.")
            
        # Parse resume JSON data structure
        resume_data_str = json.dumps(resume.resume_json)
        
        # Structure the prompt
        prompt = PromptLibrary.format_prompt(
            key="ats_optimizer",
            resume_json=resume_data_str,
            jd_text=job_description
        )
        
        # Query Gateway
        logger.info("ATSService: executing AI gateway completion request.")
        ai_response = await AIGateway.generate_response(
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            parsed_analysis = json.loads(ai_response)
            logger.info("ATSService: match scoring completed successfully.")
            return {
                "score": parsed_analysis.get("score", 0),
                "confidence_score": 0.95,
                "evidence": {
                    "matched_keywords": parsed_analysis.get("matched_keywords", []),
                    "missing_keywords": parsed_analysis.get("missing_keywords", [])
                },
                "reasoning_metadata": parsed_analysis.get("recommendations", "Check keyword alignments.")
            }
        except Exception as e:
            logger.error(f"ATSService: parsing AI analysis output failed: {e}")
            return {
                "score": 50,
                "confidence_score": 0.50,
                "evidence": {
                    "matched_keywords": [],
                    "missing_keywords": []
                },
                "reasoning_metadata": "Failed to parse detailed explainability reports."
            }
