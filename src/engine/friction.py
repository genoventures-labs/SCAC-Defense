import asyncio
import random
from src.schemas.events import IntentClassification

class FrictionEngine:
    """
    Sovereign Friction Engine.
    Introduces non-binary mitigation via artificial latency and challenges.
    """
    
    async def get_friction_delay(self, classification: IntentClassification) -> float:
        """
        Calculates artificial delay based on threat level and confidence.
        Target: Tarpitting suspicious actors.
        """
        if classification.threat_level <= 2:
            return 0.0
            
        # Base delay + variance to avoid timing analysis detection
        base_delay = (classification.threat_level - 2) * 2.0 # 2s per level above 2
        variance = random.uniform(0.1, 0.5)
        
        # Cap at 10 seconds for standard requests
        total_delay = min(10.0, base_delay + variance)
        
        print(f"⏳ APPLYING FRICTION: {total_delay}s delay injected for threat level {classification.threat_level}")
        return total_delay

    async def is_challenge_required(self, classification: IntentClassification) -> bool:
        """
        Determines if an out-of-band challenge (MFA) is required.
        """
        # Challenge if threat is significant (4+) or suspicious (3) but high confidence
        if classification.threat_level >= 4:
            return True
        if classification.threat_level == 3 and classification.confidence > 0.8:
            return True
        return False

friction_engine = FrictionEngine()
