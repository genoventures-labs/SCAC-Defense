import json
from src.schemas.events import AccessEvent

class PersonaEngine:
    """
    Sovereign Persona Engine.
    Classifies the intruder into a specific archetype based on behavioral signatures.
    """
    
    def __init__(self):
        self.archetypes = ["SCRIPT_KIDDIE", "BUG_BOUNTY", "BLACK_HAT", "RED_TEAM", "UNKNOWN"]

    async def classify_persona(self, events: list[AccessEvent], history: dict) -> str:
        """
        Heuristic-based archetype classification.
        Real production would use a fine-tuned model for this.
        """
        resource_pattern = " ".join([str(e.resource).lower() for e in events])
        action_pattern = " ".join([str(e.action).lower() for e in events])
        
        # 1. Detect Script Kiddies (High volume of common 'tutorial' resources)
        sk_triggers = ["/etc/passwd", "/etc/shadow", "test", "demo", "admin", "login"]
        sk_count = sum(1 for trigger in sk_triggers if trigger in resource_pattern)
        if sk_count >= 3 and len(events) < 5:
            return "SCRIPT_KIDDIE"

        # 2. Detect Bug Bounty Hunters (Scanning specific common vulnerabilities, but cautious)
        bb_triggers = ["wp-admin", ".env", ".git", "/api/v1", ".well-known"]
        if any(trigger in resource_pattern for trigger in bb_triggers):
            # Cautious checking usually results in fewer destructive actions
            if "rm -rf" not in action_pattern:
                return "BUG_BOUNTY"

        # 3. Detect Red Teamers (Professional methodology, lateral movement patterns)
        rt_triggers = ["ssh_login", "sudo", "nmap", "enum", "docker"]
        if any(trigger in resource_pattern for trigger in rt_triggers):
            # High success rate or logical progression
            return "RED_TEAM"

        # 4. Detect Black Hats (Destructive or high-value targets, high stealth/precision)
        bh_triggers = ["rm -rf", "shred", "encrypt", "shadow"]
        if any(trigger in resource_pattern for trigger in bh_triggers):
            return "BLACK_HAT"

        return "UNKNOWN"

persona_engine = PersonaEngine()
