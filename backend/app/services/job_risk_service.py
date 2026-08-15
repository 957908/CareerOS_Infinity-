"""
JobRiskService — Detects suspicious signals and job scam indicators.

Risk Flags:
- Payment requests (crypto, gift cards, wire transfer, registration fees)
- Suspicious domains or unverified emails
- Unrealistic salary claims ($5000/day for entry level)
- Premature requests for financial info / passport before interview stage
"""
import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger("app.services.job_risk")

_SCAM_PATTERNS = [
    re.compile(r"(crypto|bitcoin|usdt|wire\s+transfer|gift\s+card|western\s+union|moneygram)", re.IGNORECASE),
    re.compile(r"(registration\s+fee|application\s+fee|processing\s+fee|deposit|buy\s+equipment)", re.IGNORECASE),
    re.compile(r"(credit\s+card|bank\s+account|routing\s+number|social\s+security|ssn|passport\s+scan)", re.IGNORECASE),
    re.compile(r"(make\s+\$\d{4,}\s+per\s+(day|week)|earn\s+easy\s+money|no\s+experience\s+\$\d{5,})", re.IGNORECASE),
]


class JobRiskService:
    """
    Evaluates job postings for risk signals.
    """

    @staticmethod
    def evaluate_risk(
        title: str,
        company: str,
        description: str,
        source_url: str = None
    ) -> Dict[str, Any]:
        flags: List[str] = []
        full_text = f"{title} {company} {description} {source_url or ''}"

        for pattern in _SCAM_PATTERNS:
            match = pattern.search(full_text)
            if match:
                flags.append(f"Suspicious pattern detected: '{match.group(0)}'")

        if not description or len(description.strip()) < 50:
            flags.append("Incomplete or suspicious job description length.")

        if flags:
            logger.warning(f"JobRiskService: {len(flags)} risk flags detected for {title} at {company}")
            return {
                "risk_status": "RISK_REVIEW_REQUIRED" if len(flags) <= 2 else "HIGH_RISK",
                "risk_flags": flags,
                "is_safe_to_apply": False,
            }

        return {
            "risk_status": "LOW_RISK",
            "risk_flags": [],
            "is_safe_to_apply": True,
        }
