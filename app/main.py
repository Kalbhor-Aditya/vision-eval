"""FastAPI application — vision reasoning endpoints."""
from __future__ import annotations
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langfuse import observe

from app.config import settings
from app.logger import get_logger
from app.models import AnalyzeRequest, AnalyzeResponse, CompareRequest, CompareResponse, SkillResult
from app.skill_registry import route, get_skill, list_skills
from app.langfuse_client import (
    get_current_trace_id, update_trace, score_current_trace, add_score, flush
)

logger = get_logger(__name__)

app = FastAPI(title="VisionEval", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}


@app.get("/skills")
async def get_skills():
    return {"skills": list_skills()}


@observe(name="analyze")
async def _run_analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    t0 = time.monotonic()
    trace_id = get_current_trace_id()
    update_trace(
        name="analyze",
        metadata={"question": req.question, "skill": req.skill},
        session_id=req.session_id,
    )
    logger.info("Analyze started", extra={"trace_id": trace_id, "skill": req.skill, "question": req.question[:80]})

    # Route to skill(s)
    skill_names = await route(req.question) if req.skill == "auto" else [req.skill]

    # Invoke skills sequentially
    skill_results: list[SkillResult] = []
    for skill_name in skill_names:
        try:
            skill = get_skill(skill_name)
            result = await skill.invoke(image_b64=req.image_b64, question=req.question)
            skill_results.append(result)
        except Exception as exc:
            logger.error("Skill error", extra={"skill": skill_name, "error": str(exc)})
            raise HTTPException(status_code=500, detail=f"Skill {skill_name} failed: {exc}")

    # Synthesize final answer if multiple skills ran
    if len(skill_results) == 1:
        final_answer = skill_results[0].answer
    else:
        combined = "\n".join(f"[{r.skill_name}]: {r.answer}" for r in skill_results)
        from app.vlm_client import text_query
        final_answer, _ = await text_query(
            prompt=f"Combine these answers into one coherent response:\n{combined}\n\nOriginal question: {req.question}",
        )

    # Auto-eval: LLM judge
    from app.evals.llm_judge import judge
    judge_score, judge_reason = await judge(question=req.question, answer=final_answer)
    normalized = judge_score / 10.0

    score_current_trace(name="judge_score", value=normalized, comment=judge_reason)
    scores = {"judge_score": normalized}

    total_ms = (time.monotonic() - t0) * 1000
    logger.info(
        "Analyze complete",
        extra={"trace_id": trace_id, "skills": skill_names, "judge_score": judge_score, "latency_ms": round(total_ms, 1)},
    )

    return AnalyzeResponse(
        trace_id=trace_id,
        skills_used=skill_names,
        skill_results=skill_results,
        final_answer=final_answer,
        scores=scores,
        total_latency_ms=total_ms,
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    result = await _run_analyze(req)
    flush()
    return result


@observe(name="compare")
async def _run_compare(req: CompareRequest) -> CompareResponse:
    trace_id = get_current_trace_id()
    update_trace(name="compare", metadata={"question": req.question}, session_id=req.session_id)
    logger.info("Compare started", extra={"trace_id": trace_id, "question": req.question[:80]})

    from app.skills.compare_images import CompareImagesSkill
    skill = CompareImagesSkill()
    comparison = await skill.invoke_compare(
        image_a_b64=req.image_a_b64,
        image_b_b64=req.image_b_b64,
        question=req.question,
    )

    desc_skill = get_skill("describe_scene")
    result_a = await desc_skill.invoke(image_b64=req.image_a_b64, question="Describe this image.")
    result_b = await desc_skill.invoke(image_b64=req.image_b_b64, question="Describe this image.")

    return CompareResponse(
        trace_id=trace_id,
        model_a_result=result_a,
        model_b_result=result_b,
        comparison_summary=comparison.answer,
    )


@app.post("/compare", response_model=CompareResponse)
async def compare(req: CompareRequest):
    result = await _run_compare(req)
    flush()
    return result


@app.post("/feedback")
async def feedback(trace_id: str, score: float, comment: str = ""):
    """Human feedback — writes score to Langfuse by trace ID."""
    add_score(trace_id, "human_feedback", score, comment=comment)
    logger.info("Human feedback recorded", extra={"trace_id": trace_id, "score": score})
    return {"status": "ok"}
