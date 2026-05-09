from app.skills.base import BaseSkill


class VerifyClaimSkill(BaseSkill):
    name = "verify_claim"
    description = "Verify whether a stated claim or assertion is supported by what is visible in the image"
    system_prompt = (
        "You are a visual fact-checker. Given an image and a claim, determine whether the claim is: "
        "SUPPORTED, CONTRADICTED, or UNVERIFIABLE based solely on what you can see. "
        "Cite specific visual evidence for your verdict. Never speculate beyond the visible content."
    )
