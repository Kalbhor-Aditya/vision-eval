"""VLM client: Groq primary, HuggingFace fallback for vision."""
from __future__ import annotations
import base64
import time
from typing import Any

from groq import AsyncGroq
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

_groq_client: AsyncGroq | None = None


def _groq() -> AsyncGroq:
    global _groq_client
    if _groq_client is None:
        _groq_client = AsyncGroq(api_key=settings.groq_api_key)
    return _groq_client


async def vision_query(
    image_b64: str,
    prompt: str,
    system_prompt: str | None = None,
    model: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """Query a vision model. Returns (text_response, metadata)."""
    model = model or settings.groq_vision_model
    t0 = time.monotonic()

    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
            },
            {"type": "text", "text": prompt},
        ],
    })

    logger.info("VLM vision request", extra={"model": model, "prompt_preview": prompt[:80]})

    try:
        resp = await _groq().chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1024,
        )
        content = resp.choices[0].message.content or ""
        tokens = resp.usage.total_tokens if resp.usage else 0
        latency_ms = (time.monotonic() - t0) * 1000

        logger.info(
            "VLM vision response",
            extra={"model": model, "tokens": tokens, "latency_ms": round(latency_ms, 1)},
        )
        return content, {"model": model, "tokens": tokens, "latency_ms": latency_ms, "provider": "groq"}

    except Exception as exc:
        logger.warning("Groq vision failed, trying HuggingFace fallback", extra={"error": str(exc)})
        return await _hf_vision_query(image_b64, prompt, system_prompt)


async def _hf_vision_query(
    image_b64: str,
    prompt: str,
    system_prompt: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """HuggingFace Inference API fallback for vision."""
    from huggingface_hub import AsyncInferenceClient

    t0 = time.monotonic()
    model = settings.hf_vision_model
    client = AsyncInferenceClient(token=settings.hf_token)

    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

    logger.info("HF vision fallback request", extra={"model": model})
    try:
        result = await client.visual_question_answering(
            image=base64.b64decode(image_b64),
            question=full_prompt,
            model=model,
        )
        content = result[0].answer if result else ""
        latency_ms = (time.monotonic() - t0) * 1000
        logger.info("HF vision response", extra={"model": model, "latency_ms": round(latency_ms, 1)})
        return content, {"model": model, "tokens": 0, "latency_ms": latency_ms, "provider": "huggingface"}
    except Exception as exc:
        logger.error("HuggingFace vision also failed", extra={"error": str(exc)})
        raise


async def text_query(
    prompt: str,
    system_prompt: str | None = None,
    model: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """Query Groq text model. Returns (text_response, metadata)."""
    model = model or settings.groq_text_model
    t0 = time.monotonic()

    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    logger.debug("Text query", extra={"model": model, "prompt_preview": prompt[:80]})

    resp = await _groq().chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=512,
    )
    content = resp.choices[0].message.content or ""
    tokens = resp.usage.total_tokens if resp.usage else 0
    latency_ms = (time.monotonic() - t0) * 1000

    logger.debug("Text response", extra={"model": model, "tokens": tokens, "latency_ms": round(latency_ms, 1)})
    return content, {"model": model, "tokens": tokens, "latency_ms": latency_ms, "provider": "groq"}
