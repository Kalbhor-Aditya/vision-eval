"""Base class for all skills — uses @observe for Langfuse v4 tracing."""
from __future__ import annotations
import time
from abc import ABC

from langfuse import observe

from app.models import SkillResult
from app.langfuse_client import update_observation
from app.logger import get_logger

logger = get_logger(__name__)

COT_SUFFIX = (
    "\n\nRespond in exactly this format:\n"
    "OBSERVATIONS: <what you see in the image>\n"
    "REASONING: <step-by-step thinking>\n"
    "ANSWER: <final answer>"
)


def parse_cot(raw: str) -> tuple[str, str, str]:
    obs, reasoning, answer = "", "", ""
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("OBSERVATIONS:"):
            obs = line[len("OBSERVATIONS:"):].strip()
        elif line.startswith("REASONING:"):
            reasoning = line[len("REASONING:"):].strip()
        elif line.startswith("ANSWER:"):
            answer = line[len("ANSWER:"):].strip()
    if not answer:
        answer = raw.strip()
    return obs, reasoning, answer


class BaseSkill(ABC):
    name: str = ""
    description: str = ""
    system_prompt: str = ""

    @observe()
    async def invoke(self, image_b64: str, question: str) -> SkillResult:
        from app.vlm_client import vision_query

        t0 = time.monotonic()
        logger.info("Skill invoked", extra={"skill": self.name, "question": question[:80]})

        update_observation(name=self.name, input={"question": question})

        prompt = f"{question}{COT_SUFFIX}"
        try:
            raw, meta = await vision_query(
                image_b64=image_b64,
                prompt=prompt,
                system_prompt=self.system_prompt,
            )
            obs, reasoning, answer = parse_cot(raw)
            latency_ms = (time.monotonic() - t0) * 1000

            update_observation(
                output={"answer": answer, "reasoning": reasoning},
                metadata={"model": meta["model"], "tokens": meta.get("tokens", 0), "latency_ms": latency_ms},
            )

            result = SkillResult(
                skill_name=self.name,
                observations=obs,
                reasoning=reasoning,
                answer=answer,
                latency_ms=latency_ms,
                tokens_used=meta.get("tokens", 0),
            )
            logger.info(
                "Skill completed",
                extra={"skill": self.name, "latency_ms": round(latency_ms, 1), "answer_preview": answer[:80]},
            )
            return result

        except Exception as exc:
            logger.error("Skill failed", extra={"skill": self.name, "error": str(exc)})
            raise
