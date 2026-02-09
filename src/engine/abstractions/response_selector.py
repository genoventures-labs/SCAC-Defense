"""
ResponseSelector Abstract Interface

Defines the contract for defense response selection strategies.
Implementations can use different decision-making approaches.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.schemas.events import AccessEvent, IntentClassification


class ResponseSelector(ABC):
    """
    Abstract interface for defense response selection.
    
    This interface allows swapping between different response strategies:
    - Simple threshold-based selection (current)
    - Multi-criteria decision matrix (Phase 1)
    - Mavaia ToT/MCTS exploration (Phase 3)
    """
    
    @abstractmethod
    async def select_response(
        self,
        threat_classification: IntentClassification,
        available_defenses: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select optimal defense response strategy.
        
        Args:
            threat_classification: The threat assessment result
            available_defenses: List of available defense protocols
                e.g., ["medusa", "event_horizon", "hallucination", "psyops"]
            context: Additional context including:
                - actor_id: Identifier of the actor
                - actor_history: Historical response effectiveness
                - system_load: Current system resource usage
                - active_defenses: Currently active defense protocols
                
        Returns:
            Response strategy dict with:
                - primary_defense: Main defense to activate
                - secondary_defenses: Supporting defenses (optional)
                - escalation_plan: Next steps if primary fails
                - parameters: Defense-specific configuration
        """
        pass
    
    @abstractmethod
    async def evaluate_effectiveness(
        self,
        response: Dict[str, Any],
        outcome: Dict[str, Any]
    ) -> float:
        """
        Evaluate how effective a response was.
        
        Args:
            response: The response that was executed
            outcome: The observed outcome including:
                - actor_aborted: Whether actor stopped attack
                - time_to_abort: How long until actor stopped
                - damage_prevented: Estimated damage prevented
                - false_positive: Whether this was a false alarm
                
        Returns:
            Effectiveness score between 0.0 (ineffective) and 1.0 (highly effective)
        """
        pass
    
    @abstractmethod
    async def get_escalation_path(
        self,
        current_response: Dict[str, Any],
        threat_level: int
    ) -> List[Dict[str, Any]]:
        """
        Get escalation path for graduated response.
        
        Args:
            current_response: Currently active response
            threat_level: Current threat level (1-5)
            
        Returns:
            List of responses in escalation order, from least to most aggressive
        """
        pass
    
    async def calculate_cost_benefit(
        self,
        response: Dict[str, Any],
        threat_classification: IntentClassification
    ) -> Dict[str, float]:
        """
        Calculate cost/benefit analysis for a response.
        
        Default implementation provides basic analysis.
        Override for sophisticated cost modeling.
        
        Args:
            response: Response to analyze
            threat_classification: The threat being responded to
            
        Returns:
            Dict with 'cost' and 'benefit' scores (0.0-1.0)
        """
        # Default: higher threat = higher benefit, more aggressive = higher cost
        benefit = threat_classification.threat_level / 5.0
        
        # Estimate cost based on defense type
        defense = response.get('primary_defense', '')
        cost_map = {
            'block_ip': 0.2,
            'deep_scan': 0.4,
            'medusa': 0.5,
            'event_horizon': 0.7,
            'hallucination': 0.8,
            'psyops': 0.6,
        }
        cost = cost_map.get(defense, 0.5)
        
        return {'cost': cost, 'benefit': benefit}
