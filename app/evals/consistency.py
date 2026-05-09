"""Consistency eval: rephrase question 3 ways, check if answers diverge."""
from __future__ import annotations
from app.evals.semantic_sim import similarity
from app.logger import get_logger

logger = get_logger(__name__)

_REPHRASE_SYSTEM = (
    "Rephrase the following question in 2 different ways, keeping the same meaning. "
    "Output ONLY the 2 rephrased versions, one per line, no numbering."
)


async def check_consistency(image_b64: str, original_question: str, skill_name: str = "auto") -> dict:
    """
    Run the same question 3 ways (original + 2 rephrases) and measure answer consistency.
    Returns {"score": float, "answers": list[str], "min_similarity": float}
    """
    from app.vlm_client import text_query
    from app.skill_registry import route, get_skill

    # Generate 2 rephrases
    raw, _ = await text_query(prompt=original_question, system_prompt=_REPHRASE_SYSTEM)
    rephrases = [line.strip() for line in raw.strip().splitlines() if line.strip()][:2]
    all_questions = [original_question] + rephrases

    logger.info("Consistency check", extra={"original": original_question[:60], "rephrases": len(rephrases)})

    # Get skill to use
    if skill_name == "auto":
        skills = await route(original_question)
        skill = get_skill(skills[0])
    else:
        skill = get_skill(skill_name)

    answers = []
    for q in all_questions:
        result = await skill.invoke(image_b64=image_b64, question=q)
        answers.append(result.answer)

    # Compute pairwise similarities
    pairs = []
    for i in range(len(answers)):
        for j in range(i + 1, len(answers)):
            pairs.append(similarity(answers[i], answers[j]))

    min_sim = min(pairs) if pairs else 1.0
    avg_sim = sum(pairs) / len(pairs) if pairs else 1.0

    logger.info("Consistency result", extra={"avg_sim": round(avg_sim, 3), "min_sim": round(min_sim, 3)})
    return {"score": avg_sim, "min_similarity": min_sim, "answers": answers, "questions": all_questions}
