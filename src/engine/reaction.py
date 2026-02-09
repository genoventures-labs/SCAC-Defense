from src.schemas.events import IntentClassification
from src.clients.pocketbase import pb_client

class ReactionEngine:
    """
    Sovereign Reaction Engine.
    Executes automated system responses based on intent classification.
    """
    
    async def process_intent(self, actor_id: str, classification: IntentClassification):
        """
        Determines and executes the appropriate reaction based on threat level.
        """
        threat_level = classification.threat_level
        intent_type = classification.intent_type
        
        print(f"⚡ Reaction Engine processing {intent_type} (Threat: {threat_level}) for actor {actor_id}")
        
        # 🟢 Level 1-2: Benign/Low - No Action required beyond logging
        if threat_level <= 2:
            return {"action": "monitor", "status": "no_change"}
            
        # 🟡 Level 3: Suspicious - Increase monitoring (Handled by core reasoning)
        if threat_level == 3:
            return {"action": "watchlist", "status": "profile_updated"}
            
        # 🔴 Level 4-5: Adversarial - ACTIVE DEFENSE
        if threat_level >= 4:
            return await self._block_actor(actor_id, classification.reasoning)
            
        return {"action": "unknown", "status": "no_change"}

    async def _block_actor(self, actor_id: str, reason: str):
        """
        Active Blocking: Blocks the actor profile in PocketBase.
        """
        print(f"🚫 BLOCKING ACTOR: {actor_id}")
        try:
            # 1. Try to fetch the profile
            try:
                profile = pb_client.get_collection("scac_actor_profiles").get_first_list_item(f'actor_id = "{actor_id}"')
                
                # 2. Update existing to BLOCKED status
                pb_client.get_collection("scac_actor_profiles").update(profile.id, {
                    "status": "BLOCKED",
                    "last_incident_reason": reason[:255]
                })
            except Exception as fe:
                # 3. Create NEW blocked profile if missing
                pb_client.get_collection("scac_actor_profiles").create({
                    "actor_id": actor_id,
                    "status": "BLOCKED",
                    "incident_count": 1,
                    "last_incident_reason": reason[:255]
                })
            
            print(f"✅ Actor {actor_id} has been BLOCKED in system of record.")
            return {"action": "block", "status": "actor_isolated"}
            
        except Exception as e:
            print(f"⚠️  Failed to lock actor {actor_id}: {str(e)}")
            # If profile doesn't exist, we might want to create a locked one, 
            # but usually reasoning happens after profile creation.
            return {"action": "lock", "status": "failed", "error": str(e)}

reaction_engine = ReactionEngine()
