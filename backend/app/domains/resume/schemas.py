import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ProfileMetadata(BaseModel):
    """
    Profile ingestion tracking details.
    """
    source: str = Field(..., description="Document source origin (e.g. PDF upload, LinkedIn export)")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    confidence_score: float = Field(default=1.0, description="Confidence rating of parsed entities extraction (0.0 - 1.0)")

class Competency(BaseModel):
    """
    Structured skill or domain expertise node.
    """
    name: str
    category: str = Field(default="general", description="Skill classification (e.g. languages, frameworks, cloud)")
    level: Optional[str] = Field(None, description="Experience level rating (e.g. Expert, Intermediate)")

class ExperienceSegment(BaseModel):
    """
    Relational timeline record capturing work history details.
    """
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)

class UniversalProfile(BaseModel):
    """
    Universal Career Profile Schema mapping all parsed documents into unified structures.
    """
    profile_metadata: ProfileMetadata
    competencies: List[Competency] = Field(default_factory=list)
    history: List[ExperienceSegment] = Field(default_factory=list)
    reasoning_metadata: Optional[str] = Field(None, description="Explainable details regarding entities extraction classifications")
