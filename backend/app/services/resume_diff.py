"""
ResumeDiffService — Computes section-by-section diff between master and tailored resume.

Classifications:
- ADDED
- REMOVED
- MODIFIED
- REORDERED
- UNCHANGED
"""
import logging
from typing import Dict, Any

logger = logging.getLogger("app.services.resume_diff")


class ResumeDiffService:
    """
    Computes a transparent section-by-section comparison between Master Resume JSON
    and Tailored Resume JSON.
    """

    @staticmethod
    def compute_diff(master_json: Dict[str, Any], tailored_json: Dict[str, Any]) -> Dict[str, Any]:
        diff_report = {
            "summary": {"status": "UNCHANGED", "original": None, "tailored": None},
            "skills": {"status": "UNCHANGED", "added": [], "removed": [], "reordered": False},
            "experience": {"status": "UNCHANGED", "modified_bullets": []},
            "projects": {"status": "UNCHANGED", "reordered": False, "details": []},
        }

        # 1. Summary Diff
        master_summary = master_json.get("summary") or master_json.get("profile_summary") or ""
        tailored_summary = tailored_json.get("summary") or tailored_json.get("profile_summary") or ""

        if master_summary != tailored_summary:
            diff_report["summary"] = {
                "status": "MODIFIED" if master_summary else "ADDED",
                "original": master_summary,
                "tailored": tailored_summary,
            }

        # 2. Skills Diff
        master_skills = master_json.get("skills") or [s.get("name") for s in master_json.get("competencies", []) if isinstance(s, dict)]
        tailored_skills = tailored_json.get("skills") or [s.get("name") for s in tailored_json.get("competencies", []) if isinstance(s, dict)]

        master_set = set(master_skills)
        tailored_set = set(tailored_skills)

        added_skills = list(tailored_set - master_set)
        removed_skills = list(master_set - tailored_set)
        reordered = (master_skills != tailored_skills) and not added_skills and not removed_skills

        if added_skills or removed_skills or reordered:
            status = "MODIFIED" if (added_skills or removed_skills) else "REORDERED"
            diff_report["skills"] = {
                "status": status,
                "added": added_skills,
                "removed": removed_skills,
                "reordered": reordered,
                "original": master_skills,
                "tailored": tailored_skills,
            }

        # 3. Experience Diff
        master_exp = master_json.get("experience") or master_json.get("history") or []
        tailored_exp = tailored_json.get("experience") or tailored_json.get("history") or []

        modified_exp = []
        for i, t_e in enumerate(tailored_exp):
            if i < len(master_exp):
                m_e = master_exp[i]
                m_bullets = m_e.get("achievements") or m_e.get("bullets") or []
                t_bullets = t_e.get("achievements") or t_e.get("bullets") or []

                if m_bullets != t_bullets:
                    modified_exp.append({
                        "company": t_e.get("company"),
                        "role": t_e.get("role"),
                        "original_bullets": m_bullets,
                        "tailored_bullets": t_bullets,
                    })

        if modified_exp:
            diff_report["experience"] = {
                "status": "MODIFIED",
                "modified_bullets": modified_exp,
            }

        # 4. Projects Diff
        master_proj = master_json.get("projects") or []
        tailored_proj = tailored_json.get("projects") or []

        if master_proj != tailored_proj:
            diff_report["projects"] = {
                "status": "REORDERED" if len(master_proj) == len(tailored_proj) else "MODIFIED",
                "reordered": master_proj != tailored_proj,
                "original_order": [p.get("name") for p in master_proj if isinstance(p, dict)],
                "tailored_order": [p.get("name") for p in tailored_proj if isinstance(p, dict)],
            }

        return diff_report
