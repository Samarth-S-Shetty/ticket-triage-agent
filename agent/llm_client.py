import os
import json
import time
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# -------------------- JSON MODE --------------------

def extract_json(content: str) -> Dict[str, Any]:
    """
    Extract strict JSON from the model output.
    This version only returns a dict or raises ValueError.
    """
    try:
        return json.loads(content)
    except Exception:
        # Fallback: try to find the json inside code fences or extra text
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Model did not return JSON")
        try:
            return json.loads(content[start:end + 1])
        except Exception:
            raise ValueError("Failed to parse JSON after trimming")


# -------------------- MOCK FALLBACK --------------------

def mock_extract(description: str) -> Dict[str, Any]:
    d = description.lower()

    if "500" in d or "checkout" in d or "payment" in d:
        return {
            "summary": "Checkout/payment issue",
            "category": "Bug",
            "severity": "High",
            "raw_model_output": {"mock": True}
        }

    if "password" in d or "reset" in d or "email" in d:
        return {
            "summary": "Password reset issue",
            "category": "Bug",
            "severity": "Medium",
            "raw_model_output": {"mock": True}
        }

    return {
        "summary": description[:80],
        "category": "General",
        "severity": "Low",
        "raw_model_output": {"mock": True}
    }


# -------------------- MAIN EXTRACT FUNCTION --------------------

def extract_ticket_info(description: str) -> Dict[str, Any]:
    """
    Extract structured ticket info:
    - summary
    - category
    - severity
    Uses JSON mode, deterministic output, and retry logic.
    Falls back to mock_extract() if API fails.
    """

    # No real client → use mock
    if client is None:
        return mock_extract(description)

    prompt = {
        "role": "user",
        "content": f"""
Extract structured information from this support ticket.

Return STRICT JSON ONLY, in the following schema:

{{
    "summary": "<1-2 lines concise summary, capturing the core issue and context>",

  
  "category": "<Bug | Billing | Login | Performance | Security | Support | Other>",
  "severity": "<Low | Medium | High | Critical>"
}}

Ticket:
\"\"\"{description}\"\"\"
"""
    }

    # Retry strategy
    max_retries = 3
    delay = 1.2  # seconds

    for attempt in range(max_retries):
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",      # more stable than gpt-4o-mini
                input=[prompt],
                response_format={"type": "json_object"},  # JSON MODE 🤯
                temperature=0,            # fully deterministic
                max_output_tokens=200
            )

            content = response.output[0].content[0].text
            parsed = extract_json(content)
            parsed["raw_model_output"] = content
            return parsed
        
        except (RateLimitError, APIError) as e:
            # Exponential backoff
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            else:
                fallback = mock_extract(description)
                fallback["raw_model_output"] = {"error": str(e), "fallback": "mock"}
                return fallback

        except Exception as e:
            # JSON parsing or unexpected model reply
            fallback = mock_extract(description)
            fallback["raw_model_output"] = {"error": str(e), "fallback": "json_parse"}
            return fallback

    # Should never happen, but safety fallback
    return mock_extract(description)
#NEW ISSUE SUGGESTION FUNCTION
def suggest_next_action_for_unknown(description: str) -> str:
    """
    Uses LLM to generate suggested next steps for unknown issues.
    """

    if client is None:
        # simple fallback if no API key
        return "Ask user for steps to reproduce the issue, relevant screenshots, and error codes."

    prompt = {
        "role": "user",
        "content": f"""
You are a support engineer.

Given the following ticket:

\"\"\"{description}\"\"\"

Provide a clear, actionable next step for the support agent to follow.
Not a summary, not a classification — just the next action.

Format: a short 1–2 sentence actionable recommendation.

Examples:
- Ask the user to check X and collect Y logs.
- Suggest verifying their account settings.
- Request steps to reproduce and any screenshots.
- Guide the user through checking device settings.

Return ONLY plain text, no JSON.
"""
    }

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[prompt],
            temperature=0.2,
            max_output_tokens=120,
        )
        
        return response.output[0].content[0].text.strip()

    except Exception:
        return "Ask the user for reproduction steps, environment details, and screenshots."
