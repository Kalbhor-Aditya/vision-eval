"""Skill registry and router — selects which skill(s) to invoke for a given query."""
from __future__ import annotations
import json
from app.skills import (
    ReadTextSkill, DetectObjectsSkill, AnalyzeChartSkill,
    DescribeSceneSkill, VerifyClaimSkill, CompareImagesSkill, ExtractStructuredSkill,
)
from app.skills.base import BaseSkill
from app.logger import get_logger

logger = get_logger(__name__)

_REGISTRY: dict[str, BaseSkill] = {
    s.name: s  # type: ignore[attr-defined]
    for s in [
        ReadTextSkill(),
        DetectObjectsSkill(),
        AnalyzeChartSkill(),
        DescribeSceneSkill(),
        VerifyClaimSkill(),
        CompareImagesSkill(),
        ExtractStructuredSkill(),
    ]
}

_ROUTER_SYSTEM = (
    "You are a routing assistant. Given a user question about an image, select the 1-2 most relevant skills.\n"
    "Available skills:\n"
    + "\n".join(f"- {name}: {s.description}" for name, s in _REGISTRY.items())  # type: ignore[attr-defined]
    + "\n\nRespond with ONLY a JSON array of skill names. Example: [\"read_text\", \"verify_claim\"]"
)


def get_skill(name: str) -> BaseSkill:
    if name not in _REGISTRY:
        raise ValueError(f"Unknown skill: {name}. Available: {list(_REGISTRY)}")
    return _REGISTRY[name]


def list_skills() -> list[dict]:
    return [{"name": s.name, "description": s.description} for s in _REGISTRY.values()]  # type: ignore


async def route(question: str) -> list[str]:
    """Use LLM to select best skill(s) for a question."""
    from app.vlm_client import text_query

    raw, _ = await text_query(prompt=question, system_prompt=_ROUTER_SYSTEM)
    logger.info("Router response", extra={"raw": raw[:200]})

    try:
        # Extract JSON array from response
        start = raw.find("[")
        end = raw.rfind("]") + 1
        skills = json.loads(raw[start:end])
        # Validate names
        valid = [s for s in skills if s in _REGISTRY]
        if not valid:
            valid = ["describe_scene"]
        logger.info("Skills routed", extra={"skills": valid, "question": question[:60]})
        return valid
    except Exception:
        logger.warning("Router parse failed, defaulting to describe_scene")
        return ["describe_scene"]
