from langfuse import observe
from app.skills.base import BaseSkill, COT_SUFFIX, parse_cot
from app.langfuse_client import update_observation
from app.models import SkillResult
from app.logger import get_logger
import time

logger = get_logger(__name__)


class CompareImagesSkill(BaseSkill):
    name = "compare_images"
    description = "Compare two images: find similarities, differences, and changes between them"
    system_prompt = (
        "You are a visual comparison expert. You will be shown two images. "
        "Identify: what is the same, what has changed, what was added or removed, and the significance "
        "of those differences. Be specific about locations and elements."
    )

    @observe()
    async def invoke_compare(self, image_a_b64: str, image_b_b64: str, question: str) -> SkillResult:
        """Special invoke for two-image comparison — sends both images in one request."""
        from app.vlm_client import _groq
        from app.config import settings

        t0 = time.monotonic()
        logger.info("CompareImages invoked", extra={"question": question[:80]})
        update_observation(name="compare_images", input={"question": question})

        prompt = f"{question}{COT_SUFFIX}"
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Image A:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_a_b64}"}},
                    {"type": "text", "text": "Image B:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b_b64}"}},
                    {"type": "text", "text": prompt},
                ],
            },
        ]

        resp = await _groq().chat.completions.create(
            model=settings.groq_vision_model,
            messages=messages,
            max_tokens=1024,
        )
        raw = resp.choices[0].message.content or ""
        tokens = resp.usage.total_tokens if resp.usage else 0
        latency_ms = (time.monotonic() - t0) * 1000

        obs, reasoning, answer = parse_cot(raw)
        update_observation(output={"answer": answer}, metadata={"tokens": tokens, "latency_ms": latency_ms})

        logger.info("CompareImages completed", extra={"latency_ms": round(latency_ms, 1)})
        return SkillResult(
            skill_name=self.name,
            observations=obs,
            reasoning=reasoning,
            answer=answer,
            latency_ms=latency_ms,
            tokens_used=tokens,
        )
