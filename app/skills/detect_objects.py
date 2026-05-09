from app.skills.base import BaseSkill


class DetectObjectsSkill(BaseSkill):
    name = "detect_objects"
    description = "Identify, count, and locate objects, people, animals, or entities in an image"
    system_prompt = (
        "You are an object detection assistant. Identify all distinct objects, people, animals, "
        "and entities visible in the image. For each, note: what it is, approximate count, "
        "and rough location (top-left, center, etc.). Be specific and exhaustive."
    )
