from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class AccessEvent(BaseModel):
    id: Optional[str] = None
    timestamp: datetime = datetime.now()
    actor_id: str
    action: str
    resource: str
    context: Dict[str, Any]
    trajectory_id: Optional[str] = None

class IntentClassification(BaseModel):
    intent_type: str = "unknown"
    confidence: float = 0.0
    reasoning: str = "No reasoning provided by engine."
    threat_level: int = 1
    suggested_action: str = "Monitor and log."
    persona_classification: str = "UNKNOWN"

class EscalationEvent(BaseModel):
    event_id: str
    reason: str
    severity: str
    metadata: Dict[str, Any]
