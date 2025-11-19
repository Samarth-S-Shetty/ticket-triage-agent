from pydantic import BaseModel
from typing import List, Optional

class KBMatch(BaseModel):
    id: str
    title: str
    score: float
    recommended_action: Optional[str] = None

class TicketRequest(BaseModel):
    description: str

class TicketResponse(BaseModel):
    summary: str
    category: str
    severity: str
    match_type: str                    # "known_issue" or "new_issue"
    kb_matches: List[KBMatch]
    next_action: str
    notes: Optional[str] = None
