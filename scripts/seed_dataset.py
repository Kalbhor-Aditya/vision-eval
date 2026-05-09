"""Seed Langfuse with example dataset items from harness suites."""
import asyncio
import base64
import httpx
from app.langfuse_client import save_to_dataset
from harness.suite_definitions import SUITES
from app.logger import get_logger

logger = get_logger(__name__)


async def seed():
    async with httpx.AsyncClient(timeout=30) as client:
        for suite_name, cases in SUITES.items():
            for case in cases:
                logger.info("Seeding", extra={"suite": suite_name, "question": case["question"][:60]})
                save_to_dataset(
                    dataset_name=f"harness_{suite_name}",
                    input={"question": case["question"], "image_url": case["image_url"]},
                    expected_output=str(case.get("keywords", [])),
                    metadata={"suite": suite_name},
                )
    logger.info("Dataset seeding complete")


if __name__ == "__main__":
    asyncio.run(seed())
