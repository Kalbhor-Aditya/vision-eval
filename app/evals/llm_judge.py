"""LLM-as-judge eval: scores a model response 0-10 on helpfulness and accuracy."""
from __future__ import annotations
from app.logger import get_logger

logger = get_logger(__name__)

_JUDGE_SYSTEM = """You are an impartial judge evaluating an AI assistant's response to a visual question.
Score the response on a scale of 0-10 based on:
- Accuracy: Does it correctly describe/analyze what's in the image?
- Helpfulness: Does it fully answer the user's question?
- Reasoning quality: Is the reasoning clear and logical?

Respond ONLY with: SCORE: <number>\nREASON: <one sentence>"""


async def judge(question: str, answer: str, image_b64: str | None = None) -> tuple[float, str]:
    """Returns (score 0-10, reason string)."""
    from app.vlm_client import text_query

    prompt = f"Question: {question}\n\nAnswer to evaluate:\n{answer}"
    raw, _ = await text_query(prompt=prompt, system_prompt=_JUDGE_SYSTEM)

    score = 5.0
    reason = ""
    for line in raw.splitlines():
        if line.startswith("SCORE:"):
            try:
                score = float(line.split(":")[1].strip())
                score = max(0.0, min(10.0, score))
            except ValueError:
                pass
        elif line.startswith("REASON:"):
            reason = line[len("REASON:"):].strip()

    logger.info("LLM judge scored", extra={"score": score, "reason": reason[:80]})
    return score, reason
