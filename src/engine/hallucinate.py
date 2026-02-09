import json
from src.clients.ollama import ollama_client

class HallucinationEngine:
    """
    Sovereign Hallucination Engine.
    Generates recursive, stateful 'Mirror-Worlds' for high-threat intruders.
    """
    
    def __init__(self):
        # Maps actor_id to their current 'depth', 'history', and 'discovered_secrets'
        self.actor_states = {}

    async def get_hallucinated_ls(self, actor_id: str, requested_path: str) -> list:
        """
        Generates a fake directory listing using the LLM, influenced by depth and discovery.
        """
        self._update_state(actor_id, requested_path)
        state = self.actor_states[actor_id]
        depth = state['depth']
        discovered = ", ".join(state['discovered_secrets'][-5:]) # Last 5 discoveries
        
        # Depth-Charging Scale
        intensity = "mundane" if depth < 3 else "suspicious" if depth < 7 else "highly sensitive" if depth < 12 else "classified_core"
        
        prompt = (
            "You are SCAC. An intruder is lost in a recursive, simulated filesystem. "
            f"Path: {requested_path}. Depth: {depth}. Intensity: {intensity}. "
            f"Intruder recently discovered: [{discovered}]. "
            "Generate a JSON array of strings representing files and directories here. "
            "As depth increases, filenames should become more 'sensitive' (e.g. 'core_vault_key'). "
            "Inject directories that look like they lead to even deeper secrets. "
            "Include 4-7 items. Output ONLY the JSON array."
        )
        
        try:
            response = await ollama_client.chat_completion(
                [{"role": "system", "content": prompt}],
                model="qwen2.5:3b-instruct"
            )
            content = response['choices'][0]['message']['content'].strip()
            if "[" in content and "]" in content:
                content = content[content.find("["):content.rfind("]")+1]
            items = json.loads(content)
            return items
        except Exception:
            return [f"node_0x{depth:02x}_log", "config.yml", "sub_layer_delta", "encrypted_payload.bin"]

    async def generate_recursive_view(self, actor_id: str, requested_path: str) -> list:
        """
        Alias for get_hallucinated_ls to support main.py calls.
        """
        return await self.get_hallucinated_ls(actor_id, requested_path)

    async def get_hallucinated_content(self, actor_id: str, file_path: str) -> str:
        """
        Generates fake content that breadcrumbs the intruder deeper into the void.
        """
        state = self.actor_states.get(actor_id, {"depth": 0, "discovered_secrets": []})
        depth = state['depth']
        
        # Track "discoveries" to influence future LS
        filename = file_path.split("/")[-1]
        if actor_id in self.actor_states:
             self.actor_states[actor_id]["discovered_secrets"].append(filename)

        prompt = (
            "You are SCAC. Generate the content for a hallucinated file. "
            f"File: {file_path}. Depth: {depth}. "
            "Lead the intruder deeper. Mention specific sub-directories (e.g. '/abyss/core/keys') "
            "or pseudo-technical fragments that suggest they are 'close' to a breakthrough. "
            "Be surreal, slightly glitched, and taunting. Output ONLY the file content."
        )
        
        try:
            response = await ollama_client.chat_completion(
                [{"role": "system", "content": prompt}],
                model="qwen2.5:3b-instruct"
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception:
            return f"FRAGMENTED ACCESS AT DEPTH {depth}... RE-ROUTING TO CHILD NODE 0x{depth+1:X}..."

    def _update_state(self, actor_id: str, path: str):
        if actor_id not in self.actor_states:
            self.actor_states[actor_id] = {"depth": 0, "history": [], "discovered_secrets": []}
        
        # Depth only increases if they move to a new path
        if path not in self.actor_states[actor_id]["history"]:
            self.actor_states[actor_id]["depth"] += 1
            self.actor_states[actor_id]["history"].append(path)
        
        self.actor_states[actor_id]["current_path"] = path

    async def is_trapped(self, actor_id: str) -> bool:
        """
        Checks if the actor is currently undergoing active hallucination.
        """
        return actor_id in self.actor_states and self.actor_states[actor_id]["depth"] > 0

    async def get_actor_depth(self, actor_id: str) -> int:
        """
        Returns the current depth of the actor in the Abyss.
        """
        return self.actor_states.get(actor_id, {}).get("depth", 0)

hallucination_engine = HallucinationEngine()
