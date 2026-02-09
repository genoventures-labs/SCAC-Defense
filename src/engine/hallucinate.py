"""
Enhanced Hallucination Engine - Adaptive Mirror-World Generation

Enhancements:
- Breadcrumb density control based on threat level
- Pattern-aware trap placement
- Adaptive content generation based on attacker behavior
- Depth optimization for maximum engagement
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.clients.ollama import ollama_client


class HallucinationEngine:
    """
    Sovereign Hallucination Engine.
    Generates recursive, stateful 'Mirror-Worlds' for high-threat intruders.
    """
    
    def __init__(self):
        # Maps actor_id to their current 'depth', 'history', and 'discovered_secrets'
        self.actor_states: Dict[str, Dict[str, Any]] = {}
        
        # Breadcrumb density levels (items per directory)
        self.density_levels = {
            'low': (3, 5),      # 3-5 items
            'medium': (5, 7),   # 5-7 items
            'high': (7, 10),    # 7-10 items
            'maximum': (10, 15) # 10-15 items
        }
        
        # Trap keywords by depth (more sensitive as depth increases)
        self.trap_keywords_by_depth = {
            (0, 3): ['config', 'logs', 'data', 'backup'],
            (3, 7): ['admin', 'secrets', 'keys', 'vault'],
            (7, 12): ['core', 'master', 'root', 'classified'],
            (12, 100): ['sovereign', 'abyss', 'nexus', 'omega']
        }

    async def get_hallucinated_ls(
        self,
        actor_id: str,
        requested_path: str,
        breadcrumb_density: str = 'medium',
        predicted_next_action: Optional[str] = None
    ) -> list:
        """
        Generates a fake directory listing using the LLM, influenced by depth and discovery.
        """
        self._update_state(actor_id, requested_path)
        state = self.actor_states[actor_id]
        depth = state['depth']
        discovered = ", ".join(state['discovered_secrets'][-5:])  # Last 5 discoveries
        
        # Get item count range based on density
        min_items, max_items = self.density_levels.get(breadcrumb_density, (5, 7))
        
        # Depth-Charging Scale
        intensity = self._get_intensity_label(depth)
        
        # Get trap keywords for current depth
        trap_keywords = self._get_trap_keywords(depth)
        
        # Build prompt with pattern prediction if available
        pattern_hint = ""
        if predicted_next_action:
            pattern_hint = f"The intruder is likely to: {predicted_next_action}. "
        
        prompt = (
            "You are SCAC. An intruder is lost in a recursive, simulated filesystem. "
            f"Path: {requested_path}. Depth: {depth}. Intensity: {intensity}. "
            f"Intruder recently discovered: [{discovered}]. "
            f"{pattern_hint}"
            f"Generate a JSON array of {min_items}-{max_items} strings representing files and directories here. "
            f"Use these keywords for authenticity: {', '.join(trap_keywords)}. "
            "As depth increases, filenames should become more 'sensitive' (e.g. 'core_vault_key'). "
            "Inject directories that look like they lead to even deeper secrets. "
            "Output ONLY the JSON array."
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
            
            # Ensure we have the right number of items
            if len(items) < min_items:
                items.extend([f"node_0x{depth:02x}_{i}" for i in range(min_items - len(items))])
            elif len(items) > max_items:
                items = items[:max_items]
            
            return items
        except Exception:
            # Fallback with appropriate density
            return [f"node_0x{depth:02x}_log_{i}" for i in range(min_items)] + \
                   [f"config_{i}.yml" for i in range((max_items - min_items) // 2)] + \
                   ["encrypted_payload.bin"]

    async def generate_recursive_view(
        self,
        actor_id: str,
        requested_path: str,
        breadcrumb_density: str = 'medium'
    ) -> list:
        """
        Alias for get_hallucinated_ls to support main.py calls.
        """
        return await self.get_hallucinated_ls(actor_id, requested_path, breadcrumb_density)

    async def get_hallucinated_content(
        self,
        actor_id: str,
        file_path: str,
        breadcrumb_density: str = 'medium'
    ) -> str:
        """
        Generates fake content that breadcrumbs the intruder deeper into the void.
        """
        state = self.actor_states.get(actor_id, {"depth": 0, "discovered_secrets": []})
        depth = state['depth']
        
        # Track "discoveries" to influence future LS
        filename = file_path.split("/")[-1]
        if actor_id in self.actor_states:
             self.actor_states[actor_id]["discovered_secrets"].append(filename)

        # Adjust content detail based on breadcrumb density
        detail_level = {
            'low': 'brief and cryptic',
            'medium': 'moderately detailed',
            'high': 'highly detailed with specific paths',
            'maximum': 'extremely detailed with multiple breadcrumbs'
        }.get(breadcrumb_density, 'moderately detailed')

        prompt = (
            "You are SCAC. Generate the content for a hallucinated file. "
            f"File: {file_path}. Depth: {depth}. Detail level: {detail_level}. "
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

    async def optimize_trap_placement(
        self,
        actor_id: str,
        detected_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimize trap placement based on detected attack patterns.
        """
        if not detected_patterns:
            return {'breadcrumb_density': 'medium', 'trap_paths': []}
        
        state = self.actor_states.get(actor_id, {"depth": 0})
        depth = state['depth']
        
        # Analyze patterns to determine optimal strategy
        pattern_types = [p.get('pattern_type', '') for p in detected_patterns]
        
        # High-frequency attackers get maximum density
        if any('burst' in pt or 'automated' in pt for pt in pattern_types):
            density = 'maximum'
        # Methodical attackers get high density
        elif any('sequence' in pt or 'escalation' in pt for pt in pattern_types):
            density = 'high'
        # Exploratory attackers get medium density
        else:
            density = 'medium'
        
        # Generate trap paths based on patterns
        trap_paths = []
        if 'sql_injection' in pattern_types:
            trap_paths.append('/database/admin/credentials.sql')
        if 'command_injection' in pattern_types:
            trap_paths.append('/scripts/privileged/exec.sh')
        if 'path_traversal' in pattern_types:
            trap_paths.append('../../root/secrets/master.key')
        
        # Add depth-appropriate generic traps
        trap_keywords = self._get_trap_keywords(depth)
        for keyword in trap_keywords[:3]:
            trap_paths.append(f'/abyss/layer_{depth}/{keyword}_vault')
        
        return {
            'breadcrumb_density': density,
            'trap_paths': trap_paths,
            'recommended_depth_increase': 2 if density == 'maximum' else 1
        }

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
    
    def _get_intensity_label(self, depth: int) -> str:
        """Get intensity label based on depth."""
        if depth < 3:
            return "mundane"
        elif depth < 7:
            return "suspicious"
        elif depth < 12:
            return "highly sensitive"
        else:
            return "classified_core"
    
    def _get_trap_keywords(self, depth: int) -> List[str]:
        """Get appropriate trap keywords for current depth."""
        for (min_depth, max_depth), keywords in self.trap_keywords_by_depth.items():
            if min_depth <= depth < max_depth:
                return keywords
        return ['data', 'config', 'system']


hallucination_engine = HallucinationEngine()
