from src.clients.ollama import ollama_client
from src.schemas.events import AccessEvent

class ModelOrchestrator:
    """
    Sovereign Intelligence Orchestrator.
    Dynamically routes security evaluation jobs to the optimal model based on complexity.
    """
    
    def __init__(self):
        self.tiers = {
            "BENIGN": "llama3.2:1b",           # Ultra-fast, low resource
            "LOGIC": "qwen2.5:3b-instruct",    # Better reasoning for multi-step
            "ADVANCED": "mistral:latest"       # High reasoning for code/XSS/injection
        }
        self._available_models = []

    async def _sync_models(self):
        if not self._available_models:
            try:
                self._available_models = await ollama_client.list_models()
                print(f"🔄 Orchestrator Synced Models: {len(self._available_models)} found.")
            except Exception as e:
                print(f"⚠️  Model Sync Failed: {str(e)}")
                # Fallback to defaults or whatever is available
                self._available_models = list(self.tiers.values())

    async def select_model(self, events: list[AccessEvent]) -> str:
        await self._sync_models()
        
        # 1. Complexity Score Calculation
        score = len(events)
        critical_keywords = ["execute", "sudo", "curl", "chmod", "delete", "rm", "injection"]
        
        has_critical = any(
            any(k in str(e.action).lower() or k in str(e.resource).lower() or k in str(e.context).lower() for k in critical_keywords)
            for e in events
        )
        
        if has_critical:
            score += 10
            
        # 2. Tier Selection
        if score > 10:
            selection = self.tiers["ADVANCED"]
        elif score > 3:
            selection = self.tiers["LOGIC"]
        else:
            selection = self.tiers["BENIGN"]
            
        # 3. Availability Check & Fallback
        # If the preferred model isn't pulled/available on VPS, find closest match or use default
        if selection in self._available_models:
            print(f"🎯 Orchestrator Selected: {selection} (Score: {score})")
            return selection
        
        # Simple fallback chain
        for fallback in [self.tiers["LOGIC"], self.tiers["BENIGN"], "llama3.2:1b"]:
            if fallback in self._available_models:
                print(f"🩹 Orchestrator Fallback: {fallback} (Preferred {selection} not found)")
                return fallback
                
        return selection # Hope for the best

orchestrator = ModelOrchestrator()
