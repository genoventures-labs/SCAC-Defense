import hashlib
import random

class PropagandaEngine:
    """
    Sovereign Propaganda Engine.
    Generates 'The Buddy Effect' and faked success logs.
    """
    
    def __init__(self):
        self.fake_creds = [
            "admin:SCAC{y0u_w0n_n0th1ng}",
            "root:AbyssL0rd_99",
            "db_user:fake_password_123",
            "aws_key:AKIA_TRAP_EXAMPLE_XYZ"
        ]

    async def generate_fake_success(self, actor_id: str) -> dict:
        """
        Generates realistic but useless data to make the actor believe they've succeeded.
        """
        return {
            "status": "success",
            "extracted_data": random.choice(self.fake_creds),
            "forensics_lock": hashlib.sha256(actor_id.encode()).hexdigest()[:12]
        }

    async def generate_fake_leak(self, actor_id: str) -> dict:
        """
        Alias for generate_fake_success to support main.py calls.
        """
        return await self.generate_fake_success(actor_id)

    async def get_actor_reality_bias(self, actor_id: str) -> str:
        """
        Determines the 'flavor' of reality for this specific actor to ensure inconsistency with others.
        """
        seed = int(hashlib.md5(actor_id.encode()).hexdigest(), 16) % 3
        biases = ["TRAPPED_IN_LOOP", "COMMAND_CORRUPTION", "SURREAL_LEAKS"]
        return biases[seed]

propaganda_engine = PropagandaEngine()
