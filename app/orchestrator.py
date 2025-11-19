# app/orchestrator.py
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# config
MATCH_THRESHOLD = float(os.getenv("MATCH_THRESHOLD", 0.6))

# imports from your modules
from agent.llm_client import extract_ticket_info, suggest_next_action_for_unknown
from kb.search import search_kb

def triage_ticket(description: str) -> Dict[str, Any]:
    """
    Orchestrator for ticket triage.

    Returns a dict matching the TicketResponse Pydantic schema:
    {
      "summary": str,
      "category": str,
      "severity": str,
      "match_type": "known_issue" | "new_issue",
      "kb_matches": [ ... ]     # only included for known_issue (empty list for new_issue)
      "next_action": str,
      "notes": Optional[str]
    }
    """
    # 1) Extract structured info from the ticket via LLM or mock
    info = extract_ticket_info(description)

    # Ensure keys exist (defensive)
    summary = info.get("summary", description[:200])
    category = info.get("category", "Other")
    severity = info.get("severity", "Low")

    # 2) Search KB (returns up to top-3 matches with keys id,title,score,recommended_action)
    kb_matches_all = search_kb(description)

    # 3) Decide if it's a known issue
    is_known = False
    best_match = kb_matches_all[0] if kb_matches_all else None

    if best_match and best_match.get("score", 0.0) >= MATCH_THRESHOLD:
        # Optional: require category alignment as extra safety
        # If your KB entries include category field and you want to enforce alignment,
        # you can fetch the actual KB entry and compare categories here.
        is_known = True

    # 4) Prepare response: include KB matches only for known_issue
    if is_known:
        match_type = "known_issue"
        kb_matches = kb_matches_all  # include the top matches (already sorted)
        # prefer using recommended_action from the top match
        next_action = kb_matches[0].get("recommended_action") if kb_matches else "Investigate further."
    else:
        match_type = "new_issue"
        kb_matches = []  # hide KB matches for new issues as requested

        # Use LLM to suggest next action for unknown issues (fallback to generic text)
        try:
            next_action = suggest_next_action_for_unknown(description)
        except Exception:
            next_action = "Collect reproduction steps, environment details, and screenshots; escalate to engineering."

    response = {
        "summary": summary,
        "category": category,
        "severity": severity,
        "match_type": match_type,
        "kb_matches": kb_matches,
        "next_action": next_action,
        "notes": info.get("notes") if isinstance(info.get("notes"), str) else None
    }

    return response
