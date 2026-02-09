import random

class DeceptionEngine:
    """
    Sovereign Deception Engine.
    Generates context-aware honey-tokens and decoy responses.
    """
    
    def __init__(self):
        self.traps = {
            "secrets": [".env", "config.yml", "credentials.json", ".aws/credentials", "master.key"],
            "apis": ["/v1/admin/users", "/api/internal/test-vault", "/debug/vars", "/env"],
            "db": ["users_backup.sql", "db_dump.tar.gz", "migrations/internal.py"]
        }

    async def get_decoy_resource(self, observed_path: str) -> str:
        """
        Predicts what the actor is looking for and returns a relevant decoy path.
        """
        path = observed_path.lower()
        
        if any(x in path for x in ["env", "config", "key", "secret"]):
            return f"/api/deception/{random.choice(self.traps['secrets'])}"
            
        if any(x in path for x in ["admin", "debug", "internal", "vars"]):
            return f"/api/deception{random.choice(self.traps['apis'])}"
            
        if any(x in path for x in ["db", "sql", "dump", "backup"]):
            return f"/api/deception/{random.choice(self.traps['db'])}"
            
        return "/api/deception/general-resource.bak"

    async def generate_honey_content(self, decoy_path: str) -> dict:
        """
        Generates realistic but synthetic content for the decoy.
        """
        if ".env" in decoy_path:
            return {"DATABASE_URL": "postgres://fake_user:fake_pass@fake-db.internal:5432/prod", "AWS_SECRET_KEY": "SCAC-CANARY-TOKEN-XYZ"}
        
        if "admin" in decoy_path:
            return {"status": "success", "users": [{"id": 1, "role": "admin", "username": "root_trap"}]}
            
        return {"id": "resource_id", "data": "synthetic_access_granted", "canary": "true"}

deception_engine = DeceptionEngine()
