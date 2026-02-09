"""
Enhanced Rule-Based Pattern Recognizer

Implements sophisticated pattern recognition with:
- Sequence analysis (n-gram patterns in actions)
- Temporal clustering (burst detection, time-based patterns)
- Statistical anomaly detection (z-score, IQR methods)
- Attack signature library
"""

from typing import List, Dict, Any, Optional
from src.schemas.events import AccessEvent
from src.engine.abstractions.pattern_recognizer import PatternRecognizer
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import statistics


class EnhancedPatternRecognizer(PatternRecognizer):
    """
    Enhanced rule-based pattern recognition with statistical analysis.
    """
    
    def __init__(self):
        # Known attack signature patterns
        self.attack_signatures = {
            'port_scan': {
                'indicators': ['scan', 'probe', 'enumerate', 'discover'],
                'sequence_pattern': ['list', 'scan', 'probe'],
                'severity': 3,
            },
            'sql_injection': {
                'indicators': ['union', 'select', 'drop', 'insert', 'or 1=1'],
                'sequence_pattern': ['read', 'inject', 'execute'],
                'severity': 5,
            },
            'privilege_escalation': {
                'indicators': ['sudo', 'chmod', 'chown', 'setuid'],
                'sequence_pattern': ['read', 'sudo', 'execute'],
                'severity': 5,
            },
            'data_exfiltration': {
                'indicators': ['download', 'copy', 'transfer', 'curl', 'wget'],
                'sequence_pattern': ['read', 'copy', 'download'],
                'severity': 4,
            },
            'reconnaissance': {
                'indicators': ['list', 'enumerate', 'discover', 'scan'],
                'sequence_pattern': ['list', 'list', 'list'],
                'severity': 2,
            },
            'brute_force': {
                'indicators': ['login', 'auth', 'password'],
                'sequence_pattern': ['login', 'login', 'login'],
                'severity': 4,
            },
        }
        
        # Baseline statistics for anomaly detection
        self.baseline_stats: Dict[str, Dict[str, Any]] = {}
    
    async def detect_patterns(
        self,
        events: List[AccessEvent],
        historical_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect attack patterns using multiple techniques.
        """
        detected_patterns = []
        
        # 1. Signature-based detection
        signature_patterns = await self._detect_signature_patterns(events)
        detected_patterns.extend(signature_patterns)
        
        # 2. Sequence-based detection (n-grams)
        sequence_patterns = await self._detect_sequence_patterns(events)
        detected_patterns.extend(sequence_patterns)
        
        # 3. Temporal pattern detection
        temporal_patterns = await self._detect_temporal_patterns(events)
        detected_patterns.extend(temporal_patterns)
        
        # 4. Frequency-based anomalies
        frequency_patterns = await self._detect_frequency_anomalies(events)
        detected_patterns.extend(frequency_patterns)
        
        # Remove duplicates and sort by confidence
        unique_patterns = self._deduplicate_patterns(detected_patterns)
        unique_patterns.sort(key=lambda p: p['confidence'], reverse=True)
        
        return unique_patterns
    
    async def _detect_signature_patterns(self, events: List[AccessEvent]) -> List[Dict[str, Any]]:
        """Detect patterns matching known attack signatures."""
        detected = []
        
        for pattern_type, signature in self.attack_signatures.items():
            indicators = signature['indicators']
            
            # Count how many indicators are present
            matches = []
            for event in events:
                combined_text = f"{event.action} {event.resource} {event.context}".lower()
                for indicator in indicators:
                    if indicator.lower() in combined_text:
                        matches.append(event)
                        break
            
            # If significant portion of events match indicators
            if len(matches) >= 2 or (len(events) > 0 and len(matches) / len(events) >= 0.3):
                confidence = min(1.0, len(matches) / len(indicators))
                detected.append({
                    'pattern_type': pattern_type,
                    'confidence': confidence,
                    'evidence': matches[:5],  # First 5 matching events
                    'severity': signature['severity'],
                    'description': f"Detected {pattern_type} pattern with {len(matches)} matching indicators",
                })
        
        return detected
    
    async def _detect_sequence_patterns(self, events: List[AccessEvent]) -> List[Dict[str, Any]]:
        """Detect patterns in event sequences (n-grams)."""
        if len(events) < 3:
            return []
        
        detected = []
        
        # Extract action sequence
        actions = [e.action.lower() for e in events]
        
        # Check for known sequence patterns
        for pattern_type, signature in self.attack_signatures.items():
            sequence_pattern = signature['sequence_pattern']
            
            # Look for subsequence matches
            if self._contains_subsequence(actions, sequence_pattern):
                detected.append({
                    'pattern_type': f"{pattern_type}_sequence",
                    'confidence': 0.8,
                    'evidence': events,
                    'severity': signature['severity'],
                    'description': f"Detected {pattern_type} action sequence pattern",
                })
        
        # Detect repetitive patterns (e.g., brute force)
        action_counts = Counter(actions)
        most_common = action_counts.most_common(1)
        if most_common and most_common[0][1] >= 5:
            action, count = most_common[0]
            detected.append({
                'pattern_type': 'repetitive_action',
                'confidence': min(1.0, count / 10.0),
                'evidence': [e for e in events if e.action.lower() == action][:5],
                'severity': 3,
                'description': f"Detected repetitive action '{action}' ({count} times)",
            })
        
        return detected
    
    async def _detect_temporal_patterns(self, events: List[AccessEvent]) -> List[Dict[str, Any]]:
        """Detect temporal patterns (bursts, time-based anomalies)."""
        if len(events) < 3:
            return []
        
        detected = []
        
        # Get timestamps
        timestamps = [
            e.timestamp if hasattr(e, 'timestamp') else datetime.now() 
            for e in events
        ]
        
        # Calculate time differences
        time_diffs = []
        for i in range(1, len(timestamps)):
            if isinstance(timestamps[i], datetime) and isinstance(timestamps[i-1], datetime):
                diff = (timestamps[i] - timestamps[i-1]).total_seconds()
                time_diffs.append(diff)
        
        if not time_diffs:
            return detected
        
        avg_diff = statistics.mean(time_diffs)
        
        # Detect burst pattern (rapid-fire requests)
        if avg_diff < 1.0 and len(events) >= 5:
            detected.append({
                'pattern_type': 'burst_attack',
                'confidence': 0.9,
                'evidence': events,
                'severity': 4,
                'description': f"Detected burst pattern: {len(events)} events in {sum(time_diffs):.1f} seconds",
            })
        
        # Detect regular intervals (automated tool)
        if len(time_diffs) >= 5:
            std_dev = statistics.stdev(time_diffs)
            if std_dev < 0.5 and avg_diff < 10.0:
                detected.append({
                    'pattern_type': 'automated_tool',
                    'confidence': 0.85,
                    'evidence': events,
                    'severity': 3,
                    'description': f"Detected automated tool: regular intervals ({avg_diff:.2f}s ± {std_dev:.2f}s)",
                })
        
        return detected
    
    async def _detect_frequency_anomalies(self, events: List[AccessEvent]) -> List[Dict[str, Any]]:
        """Detect frequency-based anomalies."""
        if len(events) < 5:
            return []
        
        detected = []
        
        # Analyze resource access frequency
        resource_counts = Counter(e.resource for e in events)
        
        # Detect focused targeting (same resource accessed many times)
        for resource, count in resource_counts.items():
            if count >= 5:
                detected.append({
                    'pattern_type': 'focused_targeting',
                    'confidence': min(1.0, count / 10.0),
                    'evidence': [e for e in events if e.resource == resource][:5],
                    'severity': 3,
                    'description': f"Focused targeting of resource '{resource}' ({count} accesses)",
                })
        
        return detected
    
    def _contains_subsequence(self, sequence: List[str], pattern: List[str]) -> bool:
        """Check if sequence contains pattern as subsequence."""
        pattern_len = len(pattern)
        for i in range(len(sequence) - pattern_len + 1):
            if all(p.lower() in sequence[i + j].lower() for j, p in enumerate(pattern)):
                return True
        return False
    
    def _deduplicate_patterns(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate pattern detections."""
        seen = set()
        unique = []
        
        for pattern in patterns:
            key = (pattern['pattern_type'], pattern['severity'])
            if key not in seen:
                seen.add(key)
                unique.append(pattern)
        
        return unique
    
    async def predict_next_action(
        self,
        current_pattern: Dict[str, Any],
        events: List[AccessEvent]
    ) -> Dict[str, Any]:
        """
        Predict next action based on detected pattern.
        """
        pattern_type = current_pattern.get('pattern_type', 'unknown')
        
        # Prediction based on attack lifecycle
        predictions = {
            'reconnaissance': {
                'predicted_action': 'exploitation_attempt',
                'probability': 0.7,
                'alternatives': [
                    {'action': 'continued_scanning', 'probability': 0.2},
                    {'action': 'abort', 'probability': 0.1},
                ],
                'reasoning': 'Reconnaissance typically precedes exploitation',
            },
            'port_scan': {
                'predicted_action': 'service_enumeration',
                'probability': 0.8,
                'alternatives': [
                    {'action': 'vulnerability_scan', 'probability': 0.15},
                    {'action': 'abort', 'probability': 0.05},
                ],
                'reasoning': 'Port scanning usually followed by service enumeration',
            },
            'sql_injection': {
                'predicted_action': 'data_exfiltration',
                'probability': 0.85,
                'alternatives': [
                    {'action': 'privilege_escalation', 'probability': 0.1},
                    {'action': 'abort', 'probability': 0.05},
                ],
                'reasoning': 'Successful SQL injection typically leads to data exfiltration',
            },
            'privilege_escalation': {
                'predicted_action': 'lateral_movement',
                'probability': 0.75,
                'alternatives': [
                    {'action': 'data_exfiltration', 'probability': 0.2},
                    {'action': 'persistence', 'probability': 0.05},
                ],
                'reasoning': 'Privilege escalation enables lateral movement',
            },
        }
        
        # Return prediction or default
        return predictions.get(pattern_type, {
            'predicted_action': 'unknown',
            'probability': 0.5,
            'alternatives': [],
            'reasoning': 'Insufficient data for prediction',
        })
    
    async def calculate_anomaly_score(
        self,
        events: List[AccessEvent],
        baseline: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate statistical anomaly score.
        """
        if not events:
            return 0.0
        
        anomaly_factors = []
        
        # 1. Event frequency anomaly
        if baseline and 'avg_event_count' in baseline:
            avg_count = baseline['avg_event_count']
            std_count = baseline.get('std_event_count', 1.0)
            z_score = abs(len(events) - avg_count) / (std_count + 0.1)
            frequency_anomaly = min(1.0, z_score / 3.0)  # 3-sigma rule
            anomaly_factors.append(frequency_anomaly)
        
        # 2. Action diversity anomaly
        unique_actions = len(set(e.action for e in events))
        diversity_ratio = unique_actions / len(events)
        # Very low diversity (repetitive) or very high diversity (scanning) is anomalous
        diversity_anomaly = abs(diversity_ratio - 0.5) * 2
        anomaly_factors.append(diversity_anomaly)
        
        # 3. Resource sensitivity anomaly
        sensitive_keywords = ['shadow', 'passwd', 'ssh', 'root', 'admin', 'internal']
        sensitive_accesses = sum(
            1 for e in events 
            if any(k in str(e.resource).lower() for k in sensitive_keywords)
        )
        sensitivity_anomaly = min(1.0, sensitive_accesses / len(events) * 2)
        anomaly_factors.append(sensitivity_anomaly)
        
        # Combined anomaly score
        if not anomaly_factors:
            return 0.0
        
        return sum(anomaly_factors) / len(anomaly_factors)


# Singleton instance
enhanced_pattern_recognizer = EnhancedPatternRecognizer()
