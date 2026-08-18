from pydantic import BaseModel
from typing import List


class RCAResult(BaseModel):
    incident_id: str
    root_cause: str
    evidence: List[str]
    severity: str
    recommended_action: str
    confidence: str