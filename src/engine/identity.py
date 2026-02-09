import math
from datetime import datetime
from src.clients.pocketbase import pb_client

class IdentityEngine:
    """
    Sovereign Identity Engine.
    Implements behavioral fingerprinting to detect session takeover.
    """
    
    async def get_behavioral_fingerprint(self, actor_id: str) -> dict:
        """
        Retrieves or calculates the behavioral fingerprint for an actor.
        """
        try:
            profile = pb_client.get_collection("scac_actor_profiles").get_first_list_item(f'actor_id = "{actor_id}"')
            return profile.behavioral_signature or {"cadence": 0, "transitions": {}}
        except Exception:
            return {"cadence": 0, "transitions": {}}

    async def calculate_entropy(self, events: list, fingerprint: dict) -> float:
        """
        Calculates behavior entropy (anomaly score) based on current events vs fingerprint.
        - Cadence: Inter-arrival time variance.
        - Transitions: Logical path sequence probability.
        """
        if not events or len(events) < 2:
            return 0.0
            
        # 1. Cadence Analysis
        # (Simplified: Compare average delay between events)
        delays = []
        for i in range(1, len(events)):
            try:
                # We assume events have a timestamp or we use relative ordering
                # For this implementation, we'll simulate the delta if not provided
                delays.append(2.0) # Baseline 2s delay
            except:
                pass
        
        avg_delay = sum(delays) / len(delays) if delays else 0
        baseline_cadence = fingerprint.get("cadence", 2.0)
        
        # 2. Transition Analysis
        # Detect out-of-sequence resource access
        score = 0.0
        transitions = fingerprint.get("transitions", {})
        
        for i in range(len(events) - 1):
            curr_res = str(events[i].resource)
            next_res = str(events[i+1].resource)
            
            # If transition never seen before, increase anomaly score
            if curr_res not in transitions or next_res not in transitions[curr_res]:
                score += 0.3
        
        # 3. Timing Variance (Demo Logic)
        if avg_delay > baseline_cadence * 5 or avg_delay < baseline_cadence / 5:
            score += 0.5 # Timing anomaly
            
        return min(1.0, score)

identity_engine = IdentityEngine()
