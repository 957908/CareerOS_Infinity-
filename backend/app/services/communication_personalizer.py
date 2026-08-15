"""
CommunicationPersonalizer — Formats tone and style without altering factual claims.

Supported Tones: Professional / Concise / Confident / Technical / Friendly / Formal
"""
import logging

logger = logging.getLogger("app.services.personalizer")


class CommunicationPersonalizer:
    """
    Validates and formats communication tone.
    """

    ALLOWED_TONES = [
        "Professional",
        "Concise",
        "Confident",
        "Technical",
        "Friendly",
        "Formal",
    ]

    @classmethod
    def sanitize_tone(cls, requested_tone: str) -> str:
        if not requested_tone:
            return "Professional"
        for t in cls.ALLOWED_TONES:
            if t.lower() == requested_tone.strip().lower():
                return t
        return "Professional"
