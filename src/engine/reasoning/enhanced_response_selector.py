"""
Enhanced Rule-Based Response Selector

Implements sophisticated response selection with:
- Multi-criteria decision matrix (threat level, actor history, system load)
- Escalation ladder (graduated responses)
- Effectiveness tracking and learning
- Cost/benefit analysis for each defense
"""

from typing import List, Dict, Any
from src.schemas.events import IntentClassification
from src.engine.abstractions.response_selector import ResponseSelector


class EnhancedResponseSelector(ResponseSelector):
    """
    Enhanced rule-based response selection with multi-criteria decision making.
    """
    
    def __init__(self):
        # Defense escalation ladder (ordered from least to most aggressive)
        self.escalation_ladder = [
            'block_ip',          # Level 1: Simple firewall block
            'deep_scan',         # Level 2: Detailed analysis
            'medusa',            # Level 3: Active prompt injection
            'psyops',            # Level 4: Psychological warfare
            'event_horizon',     # Level 5: Honeypot containment
            'hallucination',     # Level 6: Recursive mirror-world
        ]
        
        # Defense effectiveness history (actor_id -> defense -> effectiveness)
        self.effectiveness_history: Dict[str, Dict[str, List[float]]] = {}
        
        # Defense resource costs (relative)
        self.defense_costs = {
            'block_ip': 0.1,
            'deep_scan': 0.3,
            'medusa': 0.4,
            'psyops': 0.5,
            'event_horizon': 0.7,
            'hallucination': 0.9,
        }
        
        # Defense compatibility matrix (which defenses work well together)
        self.defense_compatibility = {
            'medusa': ['psyops', 'event_horizon'],
            'psyops': ['medusa', 'hallucination'],
            'event_horizon': ['medusa', 'hallucination'],
            'hallucination': ['psyops', 'event_horizon'],
        }
    
    async def select_response(
        self,
        threat_classification: IntentClassification,
        available_defenses: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select optimal defense response using multi-criteria decision matrix.
        """
        actor_id = context.get('actor_id', 'unknown')
        threat_level = threat_classification.threat_level
        intent_type = threat_classification.intent_type
        
        # Multi-criteria scoring for each defense
        defense_scores = {}
        for defense in available_defenses:
            score = await self._calculate_defense_score(
                defense,
                threat_classification,
                context
            )
            defense_scores[defense] = score
        
        # Select primary defense (highest score)
        if not defense_scores:
            primary_defense = 'block_ip'  # Fallback
        else:
            primary_defense = max(defense_scores, key=defense_scores.get)
        
        # Select secondary defenses (compatible and high-scoring)
        secondary_defenses = await self._select_secondary_defenses(
            primary_defense,
            defense_scores,
            threat_level
        )
        
        # Build escalation plan
        escalation_plan = await self.get_escalation_path(
            {'primary_defense': primary_defense},
            threat_level
        )
        
        # Defense-specific parameters
        parameters = await self._get_defense_parameters(
            primary_defense,
            threat_classification,
            context
        )
        
        return {
            'primary_defense': primary_defense,
            'secondary_defenses': secondary_defenses,
            'escalation_plan': escalation_plan,
            'parameters': parameters,
            'confidence': defense_scores.get(primary_defense, 0.5),
            'reasoning': f"Selected {primary_defense} based on threat level {threat_level} and actor history",
        }
    
    async def _calculate_defense_score(
        self,
        defense: str,
        threat_classification: IntentClassification,
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate multi-criteria score for a defense option.
        """
        threat_level = threat_classification.threat_level
        actor_id = context.get('actor_id', 'unknown')
        system_load = context.get('system_load', 0.5)
        
        # Criteria weights
        weights = {
            'threat_match': 0.35,      # How well defense matches threat level
            'effectiveness': 0.25,     # Historical effectiveness for this actor
            'cost_benefit': 0.20,      # Cost vs benefit ratio
            'system_load': 0.10,       # Current system resource usage
            'novelty': 0.10,           # Prefer defenses not recently used
        }
        
        scores = {}
        
        # 1. Threat match score
        defense_index = self.escalation_ladder.index(defense) if defense in self.escalation_ladder else 0
        ideal_index = min(threat_level - 1, len(self.escalation_ladder) - 1)
        threat_match = 1.0 - abs(defense_index - ideal_index) / len(self.escalation_ladder)
        scores['threat_match'] = threat_match
        
        # 2. Historical effectiveness
        if actor_id in self.effectiveness_history and defense in self.effectiveness_history[actor_id]:
            effectiveness_scores = self.effectiveness_history[actor_id][defense]
            scores['effectiveness'] = sum(effectiveness_scores) / len(effectiveness_scores)
        else:
            scores['effectiveness'] = 0.5  # Neutral if no history
        
        # 3. Cost/benefit
        cost = self.defense_costs.get(defense, 0.5)
        benefit = threat_level / 5.0
        cost_benefit = benefit / (cost + 0.1)  # Avoid division by zero
        scores['cost_benefit'] = min(1.0, cost_benefit)
        
        # 4. System load consideration
        # Prefer lighter defenses when system is under load
        load_penalty = system_load * self.defense_costs.get(defense, 0.5)
        scores['system_load'] = 1.0 - load_penalty
        
        # 5. Novelty (prefer defenses not recently used)
        active_defenses = context.get('active_defenses', [])
        scores['novelty'] = 0.3 if defense in active_defenses else 1.0
        
        # Weighted combination
        total_score = sum(scores[k] * weights[k] for k in scores)
        
        return total_score
    
    async def _select_secondary_defenses(
        self,
        primary_defense: str,
        defense_scores: Dict[str, float],
        threat_level: int
    ) -> List[str]:
        """
        Select compatible secondary defenses for high threat levels.
        """
        if threat_level < 4:
            return []  # No secondary defenses for low threats
        
        compatible = self.defense_compatibility.get(primary_defense, [])
        
        # Sort compatible defenses by score
        secondary = [
            d for d in compatible 
            if d in defense_scores and d != primary_defense
        ]
        secondary.sort(key=lambda d: defense_scores[d], reverse=True)
        
        # Return top 1-2 secondary defenses
        max_secondary = 2 if threat_level == 5 else 1
        return secondary[:max_secondary]
    
    async def _get_defense_parameters(
        self,
        defense: str,
        threat_classification: IntentClassification,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get defense-specific configuration parameters.
        """
        persona = threat_classification.persona_classification
        threat_level = threat_classification.threat_level
        
        parameters = {}
        
        if defense == 'medusa':
            # Medusa: prompt injection intensity
            parameters['injection_intensity'] = 'aggressive' if threat_level >= 4 else 'moderate'
            parameters['rotation_enabled'] = threat_level >= 4
            
        elif defense == 'psyops':
            # PsyOps: taunt level and persona targeting
            parameters['sass_level'] = threat_level
            parameters['persona'] = persona
            parameters['dynamic_generation'] = threat_level >= 4
            
        elif defense == 'event_horizon':
            # Event Horizon: containment depth
            parameters['containment_depth'] = 'deep' if threat_level >= 4 else 'shallow'
            parameters['breadcrumb_density'] = 'high' if threat_level >= 4 else 'medium'
            
        elif defense == 'hallucination':
            # Hallucination: mirror-world complexity
            parameters['initial_depth'] = threat_level
            parameters['consistency_tracking'] = True
            parameters['glitch_detection'] = threat_level >= 4
        
        return parameters
    
    async def get_escalation_path(
        self,
        current_response: Dict[str, Any],
        threat_level: int
    ) -> List[Dict[str, Any]]:
        """
        Get graduated escalation path.
        """
        current_defense = current_response.get('primary_defense', 'block_ip')
        
        # Find current position in escalation ladder
        try:
            current_index = self.escalation_ladder.index(current_defense)
        except ValueError:
            current_index = 0
        
        # Build escalation path from current position
        escalation_path = []
        for i in range(current_index + 1, len(self.escalation_ladder)):
            defense = self.escalation_ladder[i]
            escalation_path.append({
                'defense': defense,
                'trigger_condition': f"If threat persists or escalates to level {i + 2}",
                'estimated_cost': self.defense_costs.get(defense, 0.5),
            })
        
        return escalation_path
    
    async def evaluate_effectiveness(
        self,
        response: Dict[str, Any],
        outcome: Dict[str, Any]
    ) -> float:
        """
        Evaluate defense effectiveness and update history.
        """
        actor_id = outcome.get('actor_id', 'unknown')
        defense = response.get('primary_defense', 'unknown')
        
        # Calculate effectiveness score
        effectiveness = 0.0
        
        # Did actor abort?
        if outcome.get('actor_aborted', False):
            effectiveness += 0.5
            
            # How quickly?
            time_to_abort = outcome.get('time_to_abort', float('inf'))
            if time_to_abort < 60:  # Less than 1 minute
                effectiveness += 0.3
            elif time_to_abort < 300:  # Less than 5 minutes
                effectiveness += 0.2
        
        # Damage prevented
        damage_prevented = outcome.get('damage_prevented', 0.0)
        effectiveness += damage_prevented * 0.3
        
        # Penalty for false positives
        if outcome.get('false_positive', False):
            effectiveness -= 0.5
        
        effectiveness = max(0.0, min(1.0, effectiveness))
        
        # Update effectiveness history
        if actor_id not in self.effectiveness_history:
            self.effectiveness_history[actor_id] = {}
        if defense not in self.effectiveness_history[actor_id]:
            self.effectiveness_history[actor_id][defense] = []
        
        self.effectiveness_history[actor_id][defense].append(effectiveness)
        
        # Keep only last 10 effectiveness scores
        if len(self.effectiveness_history[actor_id][defense]) > 10:
            self.effectiveness_history[actor_id][defense] = \
                self.effectiveness_history[actor_id][defense][-10:]
        
        return effectiveness


# Singleton instance
enhanced_response_selector = EnhancedResponseSelector()
