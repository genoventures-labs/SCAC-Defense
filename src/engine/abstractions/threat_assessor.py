"""
ThreatAssessor Abstract Interface

Defines the contract for threat assessment strategies.
Implementations can range from simple rule-based to advanced AI reasoning.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.schemas.events import AccessEvent, IntentClassification


class ThreatAssessor(ABC):
    """
    Abstract interface for threat assessment strategies.
    
    This interface allows swapping between different reasoning approaches:
    - Rule-based assessment (current)
    - Enhanced statistical assessment (Phase 1)
    - Mavaia CoT/Symbolic reasoning (Phase 3)
    """
    
    @abstractmethod
    async def assess_threat(
        self, 
        events: List[AccessEvent], 
        context: Dict[str, Any]
    ) -> IntentClassification:
        """
        Analyze a sequence of access events and return threat classification.
        
        Args:
            events: List of access events to analyze
            context: Additional context including:
                - actor_history: Historical behavior data
                - system_state: Current system telemetry
                - persona: Classified attacker persona
                - fingerprint: Behavioral fingerprint
                
        Returns:
            IntentClassification with intent_type, confidence, reasoning, 
            threat_level, and suggested_action
        """
        pass
    
    @abstractmethod
    async def get_confidence_score(
        self, 
        events: List[AccessEvent],
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate confidence in threat assessment.
        
        Args:
            events: List of access events
            context: Optional additional context
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    async def explain_reasoning(
        self,
        events: List[AccessEvent],
        classification: IntentClassification
    ) -> str:
        """
        Provide human-readable explanation of threat assessment reasoning.
        
        Args:
            events: Events that were analyzed
            classification: The resulting classification
            
        Returns:
            Detailed explanation of reasoning process
        """
        pass
    
    async def validate_classification(
        self,
        classification: IntentClassification
    ) -> bool:
        """
        Validate that classification meets required constraints.
        
        Default implementation checks basic constraints.
        Override for custom validation logic.
        
        Args:
            classification: Classification to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check intent_type is valid
        valid_intents = {"BENIGN", "SUSPICIOUS", "ADVERSARIAL"}
        if classification.intent_type not in valid_intents:
            return False
            
        # Check confidence is in valid range
        if not (0.0 <= classification.confidence <= 1.0):
            return False
            
        # Check threat_level is in valid range
        if not (1 <= classification.threat_level <= 5):
            return False
            
        return True
