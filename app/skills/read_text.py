from app.skills.base import BaseSkill


class ReadTextSkill(BaseSkill):
    name = "read_text"
    description = "Extract and transcribe all visible text from an image (OCR, receipts, signs, documents)"
    system_prompt = (
        "You are a precise OCR assistant. Your job is to extract every piece of visible text "
        "from the image exactly as it appears, preserving structure, numbers, and formatting. "
        "Do not infer or guess — only transcribe what is clearly visible."
    )
