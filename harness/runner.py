"""Eval harness runner. Usage: python -m harness.runner [--suite SUITE] [--push]"""
from __future__ import annotations
import asyncio
import base64
import time
import argparse
import httpx
from pathlib import Path

from harness.suite_definitions import SUITES
from harness.thresholds import THRESHOLDS, DEFAULT_THRESHOLD
from harness.report import print_report, save_to_log
from app.logger import get_logger
from app.langfuse_client import save_to_dataset

logger = get_logger(__name__)


async def _fetch_image_b64(url: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return base64.b64encode(resp.content).decode()


async def run_suite(suite_name: str, push_to_langfuse: bool = False) -> dict:
    from app.skill_registry import get_skill
    from app.evals.llm_judge import judge

    suite = SUITES.get(suite_name)
    if not suite:
        logger.error("Unknown suite", extra={"suite": suite_name, "available": list(SUITES)})
        raise ValueError(f"Unknown suite: {suite_name}")

    threshold = THRESHOLDS.get(suite_name, {}).get("judge_score", DEFAULT_THRESHOLD)
    skill = get_skill(suite_name)

    logger.info("Harness suite starting", extra={"suite": suite_name, "cases": len(suite), "threshold": threshold})

    results = []
    t0 = time.monotonic()

    for i, case in enumerate(suite):
        logger.info(f"Running case {i+1}/{len(suite)}", extra={"suite": suite_name, "question": case["question"][:60]})
        try:
            image_b64 = await _fetch_image_b64(case["image_url"])
            result = await skill.invoke(image_b64=image_b64, question=case["question"])
            score, reason = await judge(question=case["question"], answer=result.answer)

            # Keyword check
            kw_match = all(kw.lower() in result.answer.lower() for kw in case.get("keywords", []))
            passed = score >= threshold and (not case.get("keywords") or kw_match)

            row = {
                "question": case["question"],
                "answer": result.answer,
                "judge_score": score,
                "judge_reason": reason,
                "keyword_match": kw_match,
                "passed": passed,
                "latency_ms": result.latency_ms,
            }
            results.append(row)
            logger.info(
                "Case result",
                extra={"suite": suite_name, "case": i+1, "score": score, "passed": passed},
            )

            if push_to_langfuse:
                save_to_dataset(
                    dataset_name=f"harness_{suite_name}",
                    input={"question": case["question"], "image_url": case["image_url"]},
                    expected_output=case.get("keywords", []),
                    metadata={"judge_score": score, "passed": passed},
                )

        except Exception as exc:
            logger.error("Case failed", extra={"suite": suite_name, "case": i+1, "error": str(exc)})
            results.append({
                "question": case["question"],
                "answer": f"ERROR: {exc}",
                "judge_score": 0.0,
                "judge_reason": "exception",
                "keyword_match": False,
                "passed": False,
                "latency_ms": 0,
            })

    duration = time.monotonic() - t0
    print_report(suite_name, results, duration)
    save_to_log(suite_name, results, duration)

    return {
        "suite": suite_name,
        "total": len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "avg_score": sum(r["judge_score"] for r in results) / len(results) if results else 0,
        "duration_s": duration,
        "results": results,
    }


async def run_all(push: bool = False) -> list[dict]:
    summaries = []
    for suite_name in SUITES:
        summary = await run_suite(suite_name, push_to_langfuse=push)
        summaries.append(summary)
    return summaries


def main():
    parser = argparse.ArgumentParser(description="VisionEval harness runner")
    parser.add_argument("--suite", default="all", help="Suite name or 'all'")
    parser.add_argument("--push", action="store_true", help="Push results to Langfuse datasets")
    args = parser.parse_args()

    if args.suite == "all":
        asyncio.run(run_all(push=args.push))
    else:
        asyncio.run(run_suite(args.suite, push_to_langfuse=args.push))


if __name__ == "__main__":
    main()
