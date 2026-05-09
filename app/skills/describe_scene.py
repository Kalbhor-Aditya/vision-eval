from app.skills.base import BaseSkill


class DescribeSceneSkill(BaseSkill):
    name = "describe_scene"
    description = "Provide a rich, detailed description of an image — setting, context, atmosphere, relationships"
    system_prompt = (
        "You are a visual analyst providing comprehensive scene descriptions. "
        "Describe the setting, time of day, lighting, colors, spatial relationships between elements, "
        "mood, and any contextual details that help fully understand what is depicted."
    )
