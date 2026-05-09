"""Pass/fail thresholds per skill suite."""

THRESHOLDS: dict[str, dict[str, float]] = {
    "read_text":          {"judge_score": 7.0},
    "detect_objects":     {"judge_score": 6.5},
    "analyze_chart":      {"judge_score": 6.0},
    "describe_scene":     {"judge_score": 6.0},
    "verify_claim":       {"judge_score": 7.0},
    "extract_structured": {"judge_score": 7.0},
    "compare_images":     {"judge_score": 6.0},
}

DEFAULT_THRESHOLD = 6.0
