from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any


class SkillResult(BaseModel):
    skill_name: str
    observations: str
    reasoning: str
    answer: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    latency_ms: float = 0.0
    tokens_used: int = 0


class AnalyzeRequest(BaseModel):
    image_b64: str = Field(..., description="Base64-encoded image (no data URI prefix)")
    question: str
    skill: str = "auto"  # "auto" = router picks, or explicit skill name
    session_id: str | None = None


class AnalyzeResponse(BaseModel):
    trace_id: str
    skills_used: list[str]
    skill_results: list[SkillResult]
    final_answer: str
    scores: dict[str, float] = {}
    total_latency_ms: float = 0.0


class CompareRequest(BaseModel):
    image_a_b64: str
    image_b_b64: str
    question: str
    session_id: str | None = None


class CompareResponse(BaseModel):
    trace_id: str
    model_a_result: SkillResult
    model_b_result: SkillResult
    comparison_summary: str


class HarnessRunResult(BaseModel):
    suite: str
    total: int
    passed: int
    failed: int
    avg_score: float
    results: list[dict[str, Any]]
    duration_s: float
