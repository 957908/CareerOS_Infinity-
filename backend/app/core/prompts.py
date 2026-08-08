import logging
from typing import Dict, Optional

logger = logging.getLogger("app.core.prompts")

class PromptLibrary:
    """
    Prompt template catalog and version controls library.
    """
    _templates: Dict[str, Dict[str, str]] = {
        "resume_parser": {
            "v1": (
                "You are an elite parser. Parse the following resume text into a valid JSON object matching the "
                "defined JSON schema: {schema_json}. Do not include markdown code block syntax. Resume:\n{resume_text}"
            )
        },
        "ats_optimizer": {
            "v1": (
                "Compare the user resume: {resume_json} against the job description: {jd_text}. "
                "Produce a JSON match score (0-100), identify missing keywords, and suggest layout improvements."
            )
        },
        "interview_coach": {
            "v1": (
                "You are a mock interviewer. Ask a professional behavioral or technical question based on the user's "
                "resume: {resume_json} and target job description: {jd_text}. Evaluate their replies using the STAR framework."
            )
        }
    }

    @classmethod
    def get_template(cls, key: str, version: str = "v1") -> str:
        """
        Fetch requested prompt string template.
        """
        logger.info(f"PromptLibrary: fetching prompt key: {key} (version={version})")
        version_map = cls._templates.get(key)
        if not version_map:
            raise KeyError(f"Prompt template key: {key} not found.")
            
        template = version_map.get(version)
        if not template:
            raise KeyError(f"Prompt version {version} not found for key {key}.")
            
        return template

    @classmethod
    def format_prompt(cls, key: str, version: str = "v1", **kwargs) -> str:
        """
        Retrieves template and injects dynamic parameter arguments.
        """
        template = cls.get_template(key, version)
        return template.format(**kwargs)
