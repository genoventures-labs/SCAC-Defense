"""
PatternRecognizer Abstract Interface

Defines the contract for attack pattern recognition strategies.
Implementations can use different pattern detection approaches.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from src.schemas.events import AccessEvent


class PatternRecognizer(ABC):
    """
    Abstract interface for attack pattern recognition.
    
    This interface allows swapping between different pattern detection approaches:
    - Simple keyword/signature matching (current)
    - Statistical anomaly detection (Phase 1)
    - Mavaia MCTS prediction (Phase 3)
    """
    
    @abstractmethod
    async def detect_patterns(
        self,
        events: List[AccessEvent],
        historical_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect attack patterns in event sequences.
        
        Args:
            events: Sequence of access events to analyze
            historical_data: Optional historical pattern data including:
                - known_signatures: Previously identified attack signatures
                - actor_patterns: Patterns specific to this actor
                - global_patterns: System-wide attack patterns
                
        Returns:
            List of detected patterns, each containing:
                - pattern_type: Type of pattern (e.g., "port_scan", "sql_injection")
                - confidence: Confidence in detection (0.0-1.0)
                - evidence: Events that match the pattern
                - severity: Pattern severity (1-5)
                - description: Human-readable description
        """
        pass
    
    @abstractmethod
    async def predict_next_action(
        self,
        current_pattern: Dict[str, Any],
        events: List[AccessEvent]
    ) -> Dict[str, Any]:
        """
        Predict attacker's next likely action based on current pattern.
        
        Args:
            current_pattern: Currently detected pattern
            events: Event sequence leading to current state
            
        Returns:
            Prediction dict containing:
                - predicted_action: Most likely next action
                - probability: Probability of prediction (0.0-1.0)
                - alternatives: List of alternative predictions with probabilities
                - reasoning: Explanation of prediction
        """
        pass
    
    @abstractmethod
    async def calculate_anomaly_score(
        self,
        events: List[AccessEvent],
        baseline: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate anomaly score for event sequence.
        
        Args:
            events: Events to analyze
            baseline: Optional baseline behavior for comparison
            
        Returns:
            Anomaly score (0.0 = normal, 1.0 = highly anomalous)
        """
        pass
    
    async def identify_attack_phase(
        self,
        events: List[AccessEvent],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """
        Identify which phase of attack the actor is in.
        
        Default implementation uses common attack lifecycle phases.
        Override for custom attack modeling.
        
        Args:
            events: Event sequence
            patterns: Detected patterns
            
        Returns:
            Attack phase: "reconnaissance", "weaponization", "delivery", 
                         "exploitation", "installation", "command_control", 
                         "actions_on_objectives", or "unknown"
        """
        # Simple heuristic based on event types
        if not events:
            return "unknown"
            
        # Check for reconnaissance patterns
        recon_keywords = ["scan", "enumerate", "discover", "probe", "list"]
        if any(any(k in str(e.action).lower() for k in recon_keywords) for e in events):
            return "reconnaissance"
            
        # Check for exploitation patterns
        exploit_keywords = ["inject", "execute", "exploit", "overflow", "bypass"]
        if any(any(k in str(e.action).lower() for k in exploit_keywords) for e in events):
            return "exploitation"
            
        # Check for privilege escalation / installation
        install_keywords = ["sudo", "chmod", "install", "write", "create"]
        if any(any(k in str(e.action).lower() for k in install_keywords) for e in events):
            return "installation"
            
        # Check for data exfiltration / actions on objectives
        exfil_keywords = ["download", "copy", "transfer", "exfiltrate", "delete"]
        if any(any(k in str(e.action).lower() for k in exfil_keywords) for e in events):
            return "actions_on_objectives"
            
        return "unknown"
    
    async def build_attack_signature(
        self,
        events: List[AccessEvent],
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build attack signature from events and patterns for future detection.
        
        Args:
            events: Event sequence
            patterns: Detected patterns
            
        Returns:
            Attack signature dict containing:
                - signature_id: Unique identifier
                - event_sequence: Abstracted event sequence
                - pattern_types: Types of patterns involved
                - indicators: Key indicators of compromise
        """
        import hashlib
        import json
        
        # Create signature from event sequence
        event_types = [f"{e.action}:{e.resource}" for e in events]
        signature_str = "->".join(event_types)
        signature_id = hashlib.md5(signature_str.encode()).hexdigest()[:12]
        
        pattern_types = [p.get('pattern_type', 'unknown') for p in patterns]
        
        # Extract key indicators
        indicators = {
            'resources_accessed': list(set(e.resource for e in events)),
            'actions_performed': list(set(e.action for e in events)),
            'sequence_length': len(events),
        }
        
        return {
            'signature_id': signature_id,
            'event_sequence': event_types,
            'pattern_types': pattern_types,
            'indicators': indicators,
        }
