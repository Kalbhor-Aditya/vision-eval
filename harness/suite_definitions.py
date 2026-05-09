"""Test suite definitions. Each case: image URL, question, keywords that should appear in answer."""

# Using stable public image URLs (Wikipedia commons, etc.)
SUITES: dict[str, list[dict]] = {
    "read_text": [
        {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/400px-Camponotus_flavomarginatus_ant.jpg",
            "question": "What text is visible in this image, if any?",
            "keywords": [],
        },
        {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png",
            "question": "Extract all visible text from this image.",
            "keywords": [],
        },
    ],
    "detect_objects": [
        {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/400px-Camponotus_flavomarginatus_ant.jpg",
            "question": "What objects or creatures are visible in this image?",
            "keywords": ["ant"],
        },
        {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Biharwe_market.jpg/640px-Biharwe_market.jpg",
            "question": "Identify all people and objects visible in this market scene.",
            "keywords": ["people", "market"],
        },
    ],
    "describe_scene": [
        {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Biharwe_market.jpg/640px-Biharwe_market.jpg",
            "question": "Provide a detailed description of this scene.",
            "keywords": ["market", "outdoor"],
        },
        {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/400px-Camponotus_flavomarginatus_ant.jpg",
            "question": "Describe what you see in this image.",
            "keywords": ["ant", "macro"],
        },
    ],
    "verify_claim": [
        {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/400px-Camponotus_flavomarginatus_ant.jpg",
            "question": "Is the claim 'This image shows an insect' supported, contradicted, or unverifiable?",
            "keywords": ["supported"],
        },
    ],
    "analyze_chart": [
        {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Fy_vs_sigmax_on_billet.png/400px-Fy_vs_sigmax_on_billet.png",
            "question": "What does this chart show? Describe the axes, trend, and key insight.",
            "keywords": ["chart", "axis"],
        },
    ],
    "extract_structured": [
        {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Biharwe_market.jpg/640px-Biharwe_market.jpg",
            "question": "Extract any structured information visible in this image (labels, signs, numbers).",
            "keywords": [],
        },
    ],
}
