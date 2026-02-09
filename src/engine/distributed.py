from src.clients.pocketbase import pb_client
from datetime import datetime

class SignatureEngine:
    """
    Sovereign Distributed Intelligence.
    Synchronizes adversarial signatures across the SCAC network.
    """
    
    def __init__(self, node_id: str = "node-alpha"):
        self.node_id = node_id
        self._local_cache = set() # Failover if collection missing

    async def broadcast_signature(self, actor_id: str, confidence: float, reason: str):
        """
        Broadcasts a high-confidence adversarial signature to the global registry.
        """
        print(f"📡 BROADCASTING SIGNATURE: {actor_id} from {self.node_id}")
        self._local_cache.add(actor_id) # Always keep locally for this node's session
        try:
            # Check if exists
            try:
                existing = pb_client.get_collection("scac_global_signatures").get_first_list_item(f'actor_id = "{actor_id}"')
                pb_client.get_collection("scac_global_signatures").update(existing.id, {
                    "confidence_score": confidence,
                    "last_seen": datetime.utcnow().isoformat()
                })
            except Exception:
                pb_client.get_collection("scac_global_signatures").create({
                    "actor_id": actor_id,
                    "confidence_score": confidence,
                    "origin_node": self.node_id,
                    "signature_type": "BEHAVIOR",
                    "reason": reason[:255],
                    "last_seen": datetime.utcnow().isoformat()
                })
            return True
        except Exception as e:
            print(f"⚠️ Global Broadcast Failed: {str(e)}")
            return False

    async def check_global_status(self, actor_id: str) -> bool:
        """
        Checks if the actor is flagged in the global registry.
        """
        if actor_id in self._local_cache:
            return True
            
        try:
            pb_client.get_collection("scac_global_signatures").get_first_list_item(f'actor_id = "{actor_id}"')
            return True
        except Exception:
            return False

signature_engine = SignatureEngine()
