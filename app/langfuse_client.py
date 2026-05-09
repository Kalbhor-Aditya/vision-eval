"""Langfuse v4.5+ client — uses get_client() and @observe from langfuse directly."""
from __future__ import annotations
import os
from typing import Any

from app.config import settings
from app.logger import get_logger

# Must set env vars BEFORE importing langfuse so the internal OTel tracer
# picks up the correct credentials at module load time.
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", settings.langfuse_public_key or "")
os.environ.setdefault("LANGFUSE_SECRET_KEY", settings.langfuse_secret_key or "")
os.environ.setdefault("LANGFUSE_HOST", settings.langfuse_host or "https://cloud.langfuse.com")

from langfuse import get_client, observe  # noqa: F401, E402

logger = get_logger(__name__)
logger.info("Langfuse client ready", extra={"host": os.environ["LANGFUSE_HOST"]})


def _lf():
    return get_client()


def get_current_trace_id() -> str:
    try:
        return _lf().get_current_trace_id() or ""
    except Exception:
        return ""


def update_trace(name: str | None = None, metadata: dict | None = None, session_id: str | None = None):
    """Update current span with trace-level info (best-effort inside @observe)."""
    try:
        kwargs: dict[str, Any] = {}
        if metadata:
            kwargs["metadata"] = metadata
        if kwargs:
            _lf().update_current_span(**kwargs)
    except Exception:
        pass


def update_observation(name: str | None = None, input: Any = None, output: Any = None, metadata: dict | None = None):
    """Update the current span (call inside an @observe context)."""
    try:
        kwargs: dict[str, Any] = {}
        if name:
            kwargs["name"] = name
        if input is not None:
            kwargs["input"] = input
        if output is not None:
            kwargs["output"] = output
        if metadata:
            kwargs["metadata"] = metadata
        if kwargs:
            _lf().update_current_span(**kwargs)
    except Exception:
        pass


def score_current_trace(name: str, value: float, comment: str = ""):
    """Score the current trace (call inside an @observe context)."""
    try:
        _lf().score_current_trace(name=name, value=value, comment=comment)
        logger.info("Trace scored", extra={"score_name": name, "score_value": round(value, 3)})
    except Exception:
        pass


def add_score(trace_id: str, name: str, value: float, comment: str = ""):
    """Score a trace by ID — for feedback endpoint (outside @observe)."""
    try:
        _lf().create_score(trace_id=trace_id, name=name, value=value, comment=comment)
        logger.info("Score added", extra={"trace_id": trace_id, "score_name": name, "score_value": round(value, 3)})
    except Exception:
        pass


def save_to_dataset(dataset_name: str, input: dict, expected_output: str, metadata: dict | None = None):
    try:
        lf = _lf()
        try:
            lf.get_dataset(dataset_name)
        except Exception:
            lf.create_dataset(name=dataset_name)
        lf.create_dataset_item(
            dataset_name=dataset_name,
            input=input,
            expected_output=expected_output,
            metadata=metadata or {},
        )
        logger.info("Dataset item saved", extra={"dataset": dataset_name})
    except Exception:
        pass


def flush():
    try:
        _lf().flush()
    except Exception:
        pass
