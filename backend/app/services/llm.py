import json
import re

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

from backend.app.config import settings


def _parse_json_from_model_output(content: str) -> dict:
    cleaned = content.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def get_sales_agent_recommendation(customer_name: str, deal_size: float, sales_context: str) -> dict:
    if not settings.openai_api_key:
        if settings.allow_mock_fallback:
            return _build_mock_sales_recommendation(customer_name, deal_size, sales_context, "OPENAI_API_KEY is not set.")
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=settings.openai_api_key)

    prompt = f"""
You are the Sales Agent inside Nexus Agentic OS.

Your job is to recommend a discount for a deal.
Return ONLY valid JSON with this exact shape:
{{
  "raw_text": "one short sales recommendation sentence that includes a numeric percentage like 18%",
  "reasoning": "one or two short sentences explaining why"
}}

Customer: {customer_name}
Deal size: ${deal_size:,.2f}
Context: {sales_context}
""".strip()

    try:
        response = client.responses.create(
            model=settings.openai_model,
            input=prompt,
        )

        content = response.output_text
        parsed = _parse_json_from_model_output(content)
    except (APIConnectionError, APIStatusError, RateLimitError, json.JSONDecodeError, ValueError) as exc:
        if settings.allow_mock_fallback:
            return _build_mock_sales_recommendation(customer_name, deal_size, sales_context, str(exc))
        raise

    if "raw_text" not in parsed or "reasoning" not in parsed:
        raise ValueError("Model response did not include the required keys: raw_text and reasoning.")

    return parsed


def _build_mock_sales_recommendation(
    customer_name: str,
    deal_size: float,
    sales_context: str,
    fallback_reason: str,
) -> dict:
    context_lower = sales_context.lower()

    suggested_discount = 18
    if "renewal" in context_lower or "existing customer" in context_lower:
        suggested_discount = 12
    elif "strategic" in context_lower or "enterprise" in context_lower:
        suggested_discount = 15
    elif deal_size >= 50000:
        suggested_discount = 10

    return {
        "raw_text": (
            f"I recommend offering {suggested_discount}% to {customer_name} to improve the chance of closing this deal."
        ),
        "reasoning": (
            "This response used the built-in fallback sales simulator because the live OpenAI call was unavailable. "
            f"Reason: {fallback_reason}"
        ),
    }
