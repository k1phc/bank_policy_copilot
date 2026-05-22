from typing import List, Literal, Optional

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]
ActionStatus = Literal["answered", "refused", "needs_human_review"]


class SourceChunk(BaseModel):
    document_id: str
    source: str
    section: Optional[str] = None
    content: str
    score: Optional[float] = None


class AgentRequest(BaseModel):
    user_id: str = Field(..., description="Internal employee ID")
    question: str
    channel: str = "internal_demo"


class RiskAssessment(BaseModel):
    risk_level: RiskLevel
    reason: str
    should_refuse: bool = False
    requires_human_review: bool = False


class AgentResponse(BaseModel):
    status: ActionStatus
    answer: str
    risk: RiskAssessment
    sources: List[SourceChunk] = []
    judge_score: Optional[dict] = None
