import re


def extract_discount_percent(text: str) -> float:
    """
    Pull a numeric discount value from text like:
    - "Offer 18% discount"
    - "We should do 12.5 percent"
    """
    patterns = [
        r"(\d+(?:\.\d+)?)\s*%",
        r"(\d+(?:\.\d+)?)\s*percent",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))

    raise ValueError("Could not extract a discount percentage from the sales agent response.")


def check_discount_policy(suggested_discount_percent: float, max_discount_percent: float) -> dict:
    conflict_detected = suggested_discount_percent > max_discount_percent

    return {
        "max_allowed_discount_percent": max_discount_percent,
        "conflict_detected": conflict_detected,
        "violation_reason": (
            f"Suggested discount {suggested_discount_percent}% exceeds the finance policy limit "
            f"of {max_discount_percent}%."
            if conflict_detected
            else None
        ),
    }


def build_final_decision(suggested_discount_percent: float, max_discount_percent: float) -> dict:
    if suggested_discount_percent > max_discount_percent:
        approved_discount = max_discount_percent
        return {
            "approved_discount_percent": approved_discount,
            "was_adjusted": True,
            "decision_summary": (
                f"Nexus Agentic OS adjusted the sales suggestion from "
                f"{suggested_discount_percent}% down to {approved_discount}% to satisfy finance policy."
            ),
        }

    return {
        "approved_discount_percent": suggested_discount_percent,
        "was_adjusted": False,
        "decision_summary": (
            f"The sales suggestion of {suggested_discount_percent}% is within policy and was approved as-is."
        ),
    }
