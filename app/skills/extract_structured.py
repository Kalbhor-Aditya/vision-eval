from app.skills.base import BaseSkill


class ExtractStructuredSkill(BaseSkill):
    name = "extract_structured"
    description = "Extract structured data from images: forms, invoices, IDs, business cards, tables"
    system_prompt = (
        "You are a structured data extraction specialist. Extract all key-value pairs, table data, "
        "and structured information visible in the image. Format your answer as clean key: value pairs. "
        "Preserve exact values including dates, amounts, IDs, and codes."
    )
