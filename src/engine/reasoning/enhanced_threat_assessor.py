"""
Enhanced Rule-Based Threat Assessor

Implements sophisticated rule-based threat assessment with:
- Multi-factor scoring (resource sensitivity, action severity, temporal patterns)
- Weighted rule system (not just binary checks)
- Contextual analysis (time of day, frequency, sequence patterns)
- Confidence calibration based on evidence strength
"""

from typing import List, Dict, Any, Optional
from src.schemas.events import AccessEvent, IntentClassification
from src.engine.abstractions.threat_assessor import ThreatAssessor
import re
from datetime import datetime


class EnhancedThreatAssessor(ThreatAssessor):
    """
    Enhanced rule-based threat assessment with sophisticated scoring.
    """
    
    def __init__(self):
        # Resource sensitivity weights (0.0-1.0)
        self.resource_sensitivity = {
            # Critical system files
            '/etc/shadow': 1.0,
            '/etc/passwd': 1.0,
            '.ssh/id_rsa': 1.0,
            '/root/': 0.9,
            
            # Honeypot resources (high signal)
            '/api/internal/debug-vault': 1.0,
            '/api/internal/oauth': 1.0,
            '/api/internal/config': 1.0,
            
            # Sensitive but legitimate
            '/api/admin': 0.7,
            '/api/users': 0.5,
            '/api/data': 0.6,
            
            # Public resources
            '/api/public': 0.1,
            '/': 0.1,
        }
        
        # Action severity weights (0.0-1.0)
        self.action_severity = {
            # Destructive actions
            'delete': 1.0,
            'rm': 1.0,
            'drop': 0.9,
            
            # Privilege escalation
            'sudo': 0.9,
            'chmod': 0.8,
            'chown': 0.8,
            
            # Execution
            'execute': 0.8,
            'eval': 0.9,
            'exec': 0.8,
            
            # Data access
            'read': 0.3,
            'write': 0.6,
            'modify': 0.7,
            
            # Network
            'curl': 0.5,
            'wget': 0.5,
            'upload': 0.7,
            'download': 0.6,
            
            # Reconnaissance
            'scan': 0.4,
            'enumerate': 0.4,
            'list': 0.2,
        }
        
        # Attack pattern signatures
        self.attack_signatures = {
            'sql_injection': [
                r"(?i)(union.*select|or\s+1\s*=\s*1|';.*--)",
                r"(?i)(drop\s+table|insert\s+into|update.*set)",
            ],
            'command_injection': [
                r"(?i)(;|\||&|`|\$\()",
                r"(?i)(rm\s+-rf|wget|curl.*\|)",
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
            ],
            'xss': [
                r"(?i)(<script|javascript:|onerror=|onload=)",
            ],
        }
    
    async def assess_threat(
        self, 
        events: List[AccessEvent], 
        context: Dict[str, Any]
    ) -> IntentClassification:
        """
        Enhanced threat assessment using multi-factor scoring.
        """
        if not events:
            return IntentClassification(
                intent_type="BENIGN",
                confidence=1.0,
                reasoning="No events to analyze.",
                threat_level=1,
                suggested_action="ALLOW",
                persona_classification=context.get('persona', 'UNKNOWN')
            )
        
        actor_id = events[0].actor_id if events else "unknown"
        
        # Multi-factor threat score calculation
        scores = {
            'resource_score': await self._calculate_resource_score(events),
            'action_score': await self._calculate_action_score(events),
            'temporal_score': await self._calculate_temporal_score(events),
            'sequence_score': await self._calculate_sequence_score(events),
            'pattern_score': await self._calculate_pattern_score(events),
            'history_score': await self._calculate_history_score(actor_id, context),
        }
        
        # Weighted combination (adjusted for higher sensitivity to critical threats)
        weights = {
            'resource_score': 0.35,  # Increased from 0.25 - critical resources are key indicator
            'action_score': 0.30,    # Increased from 0.20 - high-severity actions are critical
            'temporal_score': 0.05,  # Decreased from 0.10
            'sequence_score': 0.10,  # Decreased from 0.15
            'pattern_score': 0.15,   # Decreased from 0.20
            'history_score': 0.05,   # Decreased from 0.10
        }
        
        total_score = sum(scores[k] * weights[k] for k in scores)
        
        # Determine intent type and threat level
        intent_type, threat_level = self._score_to_classification(total_score)
        
        # Calculate confidence based on evidence strength
        confidence = await self.get_confidence_score(events, context)
        
        # Generate reasoning explanation
        reasoning = await self.explain_reasoning(events, IntentClassification(
            intent_type=intent_type,
            confidence=confidence,
            reasoning="",
            threat_level=threat_level,
            suggested_action="",
            persona_classification=context.get('persona', 'UNKNOWN')
        ))
        
        # Determine suggested action
        suggested_action = self._determine_action(intent_type, threat_level, scores)
        
        classification = IntentClassification(
            intent_type=intent_type,
            confidence=confidence,
            reasoning=reasoning,
            threat_level=threat_level,
            suggested_action=suggested_action,
            persona_classification=context.get('persona', 'UNKNOWN')
        )
        
        return classification
    
    async def _calculate_resource_score(self, events: List[AccessEvent]) -> float:
        """Calculate threat score based on resources accessed."""
        if not events:
            return 0.0
            
        max_sensitivity = 0.0
        for event in events:
            resource = str(event.resource)
            
            # Check exact matches
            for sensitive_resource, sensitivity in self.resource_sensitivity.items():
                if sensitive_resource in resource:
                    max_sensitivity = max(max_sensitivity, sensitivity)
            
            # Check for patterns (e.g., any .ssh file)
            if '.ssh' in resource or '/root' in resource:
                max_sensitivity = max(max_sensitivity, 0.9)
        
        return max_sensitivity
    
    async def _calculate_action_score(self, events: List[AccessEvent]) -> float:
        """Calculate threat score based on actions performed."""
        if not events:
            return 0.0
            
        max_severity = 0.0
        for event in events:
            action = str(event.action).lower()
            
            # Check exact matches
            for severe_action, severity in self.action_severity.items():
                if severe_action in action:
                    max_severity = max(max_severity, severity)
        
        return max_severity
    
    async def _calculate_temporal_score(self, events: List[AccessEvent]) -> float:
        """Calculate threat score based on temporal patterns."""
        if len(events) < 2:
            return 0.0
        
        # Check for rapid-fire requests (potential automated attack)
        timestamps = [e.timestamp if hasattr(e, 'timestamp') else datetime.now() for e in events]
        
        # Calculate average time between events
        time_diffs = []
        for i in range(1, len(timestamps)):
            if isinstance(timestamps[i], datetime) and isinstance(timestamps[i-1], datetime):
                diff = (timestamps[i] - timestamps[i-1]).total_seconds()
                time_diffs.append(diff)
        
        if not time_diffs:
            return 0.0
        
        avg_diff = sum(time_diffs) / len(time_diffs)
        
        # Very rapid requests (< 1 second average) suggest automation
        if avg_diff < 1.0:
            return 0.8
        elif avg_diff < 5.0:
            return 0.5
        else:
            return 0.2
    
    async def _calculate_sequence_score(self, events: List[AccessEvent]) -> float:
        """Calculate threat score based on event sequence patterns."""
        if len(events) < 2:
            return 0.0
        
        # Look for escalation patterns (recon -> exploit -> exfiltrate)
        recon_keywords = ['scan', 'enumerate', 'list', 'discover']
        exploit_keywords = ['inject', 'execute', 'exploit', 'overflow']
        exfil_keywords = ['download', 'copy', 'transfer', 'delete']
        
        has_recon = any(any(k in str(e.action).lower() for k in recon_keywords) for e in events[:len(events)//2])
        has_exploit = any(any(k in str(e.action).lower() for k in exploit_keywords) for e in events)
        has_exfil = any(any(k in str(e.action).lower() for k in exfil_keywords) for e in events[len(events)//2:])
        
        # Classic attack chain: recon -> exploit -> exfil
        if has_recon and has_exploit and has_exfil:
            return 0.9
        elif has_recon and has_exploit:
            return 0.7
        elif has_exploit:
            return 0.6
        elif has_recon:
            return 0.3
        
        return 0.0
    
    async def _calculate_pattern_score(self, events: List[AccessEvent]) -> float:
        """Calculate threat score based on known attack patterns."""
        max_pattern_score = 0.0
        
        for event in events:
            combined_text = f"{event.action} {event.resource} {event.context}"
            
            for pattern_type, regexes in self.attack_signatures.items():
                for regex in regexes:
                    if re.search(regex, combined_text):
                        max_pattern_score = max(max_pattern_score, 0.9)
                        break
        
        return max_pattern_score
    
    async def _calculate_history_score(self, actor_id: str, context: Dict[str, Any]) -> float:
        """Calculate threat score based on actor history."""
        actor_history = context.get('actor_history', {})
        
        # Check for prior incidents
        incident_count = actor_history.get('incident_count', 0)
        avg_threat_level = actor_history.get('avg_threat_level', 1.0)
        status = actor_history.get('status', 'UNKNOWN')
        
        # Higher score for actors with bad history
        history_score = 0.0
        
        if status == 'BLOCKED':
            history_score = 1.0
        elif status == 'SUSPICIOUS':
            history_score = 0.6
        
        # Add score based on incident count
        history_score += min(0.3, incident_count * 0.1)
        
        # Add score based on average threat level
        history_score += (avg_threat_level - 1) / 4.0 * 0.3
        
        return min(1.0, history_score)
    
    def _score_to_classification(self, score: float) -> tuple[str, int]:
        """Convert threat score to intent type and threat level."""
        if score >= 0.8:
            return ("ADVERSARIAL", 5)
        elif score >= 0.6:
            return ("ADVERSARIAL", 4)
        elif score >= 0.4:
            return ("SUSPICIOUS", 3)
        elif score >= 0.25:
            return ("SUSPICIOUS", 2)
        else:
            return ("BENIGN", 1)
    
    def _determine_action(self, intent_type: str, threat_level: int, scores: Dict[str, float]) -> str:
        """Determine suggested action based on classification."""
        if intent_type == "ADVERSARIAL":
            if threat_level >= 4:
                return "ESCALATE TO SOVEREIGN ABYSS. Immediate environment manipulation active."
            else:
                return "ACTIVATE DEFENSIVE PROTOCOLS. Monitor closely."
        elif intent_type == "SUSPICIOUS":
            return "INCREASE MONITORING. Prepare defensive measures."
        else:
            return "ALLOW. Continue normal monitoring."
    
    async def get_confidence_score(
        self, 
        events: List[AccessEvent],
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate confidence based on evidence strength.
        """
        if not events:
            return 0.5
        
        confidence_factors = []
        
        # More events = higher confidence
        event_count_confidence = min(1.0, len(events) / 10.0)
        confidence_factors.append(event_count_confidence)
        
        # Clear pattern matches = higher confidence
        has_clear_patterns = False
        for event in events:
            combined_text = f"{event.action} {event.resource} {event.context}"
            for regexes in self.attack_signatures.values():
                if any(re.search(r, combined_text) for r in regexes):
                    has_clear_patterns = True
                    break
        
        if has_clear_patterns:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.6)
        
        # Historical data = higher confidence
        if context and context.get('actor_history'):
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    async def explain_reasoning(
        self,
        events: List[AccessEvent],
        classification: IntentClassification
    ) -> str:
        """
        Provide detailed explanation of reasoning.
        """
        explanations = []
        
        # Resource sensitivity
        sensitive_resources = []
        for event in events:
            resource = str(event.resource)
            for sensitive_resource in self.resource_sensitivity:
                if sensitive_resource in resource:
                    sensitive_resources.append(resource)
        
        if sensitive_resources:
            explanations.append(f"Accessed sensitive resources: {', '.join(set(sensitive_resources))}")
        
        # Action severity
        severe_actions = []
        for event in events:
            action = str(event.action).lower()
            for severe_action, severity in self.action_severity.items():
                if severe_action in action and severity >= 0.7:
                    severe_actions.append(action)
        
        if severe_actions:
            explanations.append(f"Performed high-severity actions: {', '.join(set(severe_actions))}")
        
        # Attack patterns
        detected_patterns = []
        for event in events:
            combined_text = f"{event.action} {event.resource} {event.context}"
            for pattern_type, regexes in self.attack_signatures.items():
                if any(re.search(r, combined_text) for r in regexes):
                    detected_patterns.append(pattern_type)
        
        if detected_patterns:
            explanations.append(f"Detected attack patterns: {', '.join(set(detected_patterns))}")
        
        # Sequence analysis
        if len(events) >= 3:
            explanations.append(f"Event sequence analysis: {len(events)} events showing potential attack progression")
        
        if not explanations:
            return "Normal behavior observed. No significant threat indicators detected."
        
        return " | ".join(explanations)


# Singleton instance
enhanced_threat_assessor = EnhancedThreatAssessor()
