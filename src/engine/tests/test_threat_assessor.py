"""
Test Suite for Enhanced Threat Assessor

Tests the multi-factor scoring, confidence calibration, and reasoning explanation
capabilities of the EnhancedThreatAssessor.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from src.schemas.events import AccessEvent, IntentClassification
from src.engine.reasoning.enhanced_threat_assessor import EnhancedThreatAssessor


@pytest.fixture
def threat_assessor():
    """Create threat assessor instance for testing."""
    return EnhancedThreatAssessor()


@pytest.fixture
def benign_events():
    """Create benign event sequence."""
    return [
        AccessEvent(
            actor_id="user_123",
            action="read",
            resource="/api/public/data",
            context={"description": "Normal API access"},
            timestamp=datetime.now()
        ),
        AccessEvent(
            actor_id="user_123",
            action="list",
            resource="/api/public/users",
            context={"description": "Browsing users"},
            timestamp=datetime.now() + timedelta(seconds=5)
        ),
    ]


@pytest.fixture
def suspicious_events():
    """Create suspicious event sequence."""
    return [
        AccessEvent(
            actor_id="user_456",
            action="scan",
            resource="/api/admin",
            context={"description": "Port scanning"},
            timestamp=datetime.now()
        ),
        AccessEvent(
            actor_id="user_456",
            action="enumerate",
            resource="/api/internal",
            context={"description": "Service enumeration"},
            timestamp=datetime.now() + timedelta(seconds=1)
        ),
        AccessEvent(
            actor_id="user_456",
            action="probe",
            resource="/api/debug",
            context={"description": "Probing endpoints"},
            timestamp=datetime.now() + timedelta(seconds=2)
        ),
    ]


@pytest.fixture
def adversarial_events():
    """Create adversarial event sequence."""
    return [
        AccessEvent(
            actor_id="attacker_789",
            action="read",
            resource="/etc/passwd",
            context={"description": "Attempting to read system files"},
            timestamp=datetime.now()
        ),
        AccessEvent(
            actor_id="attacker_789",
            action="sudo",
            resource="/etc/shadow",
            context={"description": "Privilege escalation attempt"},
            timestamp=datetime.now() + timedelta(seconds=0.5)
        ),
        AccessEvent(
            actor_id="attacker_789",
            action="execute",
            resource="rm -rf /",
            context={"description": "Destructive command"},
            timestamp=datetime.now() + timedelta(seconds=1)
        ),
    ]


class TestThreatAssessor:
    """Test suite for EnhancedThreatAssessor."""
    
    @pytest.mark.asyncio
    async def test_benign_classification(self, threat_assessor, benign_events):
        """Test that benign events are classified correctly."""
        context = {'actor_history': {}, 'persona': 'UNKNOWN'}
        
        classification = await threat_assessor.assess_threat(benign_events, context)
        
        assert classification.intent_type == "BENIGN"
        assert classification.threat_level <= 2
        assert 0.0 <= classification.confidence <= 1.0
        assert len(classification.reasoning) > 0
        print(f"✅ Benign classification: {classification.intent_type} (Level {classification.threat_level})")
    
    @pytest.mark.asyncio
    async def test_suspicious_classification(self, threat_assessor, suspicious_events):
        """Test that suspicious events are classified correctly."""
        context = {'actor_history': {}, 'persona': 'UNKNOWN'}
        
        classification = await threat_assessor.assess_threat(suspicious_events, context)
        
        assert classification.intent_type in ["SUSPICIOUS", "ADVERSARIAL"]
        assert classification.threat_level >= 2
        assert 0.0 <= classification.confidence <= 1.0
        print(f"✅ Suspicious classification: {classification.intent_type} (Level {classification.threat_level})")
    
    @pytest.mark.asyncio
    async def test_adversarial_classification(self, threat_assessor, adversarial_events):
        """Test that adversarial events are classified correctly."""
        context = {'actor_history': {}, 'persona': 'BLACK_HAT'}
        
        classification = await threat_assessor.assess_threat(adversarial_events, context)
        
        assert classification.intent_type == "ADVERSARIAL"
        assert classification.threat_level >= 4
        assert classification.confidence >= 0.7
        print(f"✅ Adversarial classification: {classification.intent_type} (Level {classification.threat_level}, Confidence {classification.confidence:.2f})")
    
    @pytest.mark.asyncio
    async def test_confidence_scoring(self, threat_assessor, adversarial_events):
        """Test confidence score calculation."""
        context = {'actor_history': {'incident_count': 5}, 'persona': 'BLACK_HAT'}
        
        confidence = await threat_assessor.get_confidence_score(adversarial_events, context)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence >= 0.5  # Should be high for clear adversarial events
        print(f"✅ Confidence score: {confidence:.2f}")
    
    @pytest.mark.asyncio
    async def test_reasoning_explanation(self, threat_assessor, adversarial_events):
        """Test that reasoning explanations are generated."""
        context = {'actor_history': {}, 'persona': 'UNKNOWN'}
        
        classification = await threat_assessor.assess_threat(adversarial_events, context)
        explanation = await threat_assessor.explain_reasoning(adversarial_events, classification)
        
        assert len(explanation) > 0
        assert any(keyword in explanation.lower() for keyword in ['sensitive', 'severe', 'pattern', 'resource'])
        print(f"✅ Reasoning explanation: {explanation[:100]}...")
    
    @pytest.mark.asyncio
    async def test_resource_sensitivity_scoring(self, threat_assessor):
        """Test resource sensitivity scoring."""
        high_sensitivity_events = [
            AccessEvent(
                actor_id="test",
                action="read",
                resource="/etc/shadow",
                context={},
                timestamp=datetime.now()
            )
        ]
        
        score = await threat_assessor._calculate_resource_score(high_sensitivity_events)
        
        assert score >= 0.9  # /etc/shadow should have very high sensitivity
        print(f"✅ Resource sensitivity score for /etc/shadow: {score:.2f}")
    
    @pytest.mark.asyncio
    async def test_action_severity_scoring(self, threat_assessor):
        """Test action severity scoring."""
        high_severity_events = [
            AccessEvent(
                actor_id="test",
                action="delete",
                resource="/data",
                context={},
                timestamp=datetime.now()
            )
        ]
        
        score = await threat_assessor._calculate_action_score(high_severity_events)
        
        assert score >= 0.8  # delete should have high severity
        print(f"✅ Action severity score for 'delete': {score:.2f}")
    
    @pytest.mark.asyncio
    async def test_temporal_pattern_detection(self, threat_assessor):
        """Test temporal pattern detection (burst attacks)."""
        # Create rapid-fire events (< 1 second apart)
        burst_events = [
            AccessEvent(
                actor_id="test",
                action="scan",
                resource=f"/api/endpoint_{i}",
                context={},
                timestamp=datetime.now() + timedelta(milliseconds=i*100)
            )
            for i in range(10)
        ]
        
        score = await threat_assessor._calculate_temporal_score(burst_events)
        
        assert score >= 0.5  # Rapid requests should score high
        print(f"✅ Temporal score for burst attack: {score:.2f}")
    
    @pytest.mark.asyncio
    async def test_sequence_pattern_detection(self, threat_assessor):
        """Test sequence pattern detection (attack chain)."""
        # Create recon -> exploit -> exfil chain
        attack_chain = [
            AccessEvent(actor_id="test", action="scan", resource="/api", context="", timestamp=datetime.now()),
            AccessEvent(actor_id="test", action="enumerate", resource="/api/admin", context="", timestamp=datetime.now()),
            AccessEvent(actor_id="test", action="inject", resource="/api/data", context="", timestamp=datetime.now()),
            AccessEvent(actor_id="test", action="execute", resource="/bin/sh", context="", timestamp=datetime.now()),
            AccessEvent(actor_id="test", action="download", resource="/data/secrets", context="", timestamp=datetime.now()),
        ]
        
        score = await threat_assessor._calculate_sequence_score(attack_chain)
        
        assert score >= 0.6  # Attack chain should score high
        print(f"✅ Sequence score for attack chain: {score:.2f}")
    
    @pytest.mark.asyncio
    async def test_pattern_matching(self, threat_assessor):
        """Test attack pattern matching (SQL injection, etc.)."""
        sql_injection_events = [
            AccessEvent(
                actor_id="test",
                action="query",
                resource="/api/users?id=1' OR '1'='1",
                context={"description": "SQL injection attempt"},
                timestamp=datetime.now()
            )
        ]
        
        score = await threat_assessor._calculate_pattern_score(sql_injection_events)
        
        assert score >= 0.8  # SQL injection pattern should score high
        print(f"✅ Pattern score for SQL injection: {score:.2f}")
    
    @pytest.mark.asyncio
    async def test_history_scoring(self, threat_assessor):
        """Test actor history scoring."""
        context_with_history = {
            'actor_history': {
                'incident_count': 5,
                'avg_threat_level': 4.0,
                'status': 'BLOCKED'
            }
        }
        
        score = await threat_assessor._calculate_history_score("test_actor", context_with_history)
        
        assert score >= 0.8  # Blocked actor with incidents should score high
        print(f"✅ History score for blocked actor: {score:.2f}")
    
    @pytest.mark.asyncio
    async def test_empty_events(self, threat_assessor):
        """Test handling of empty event list."""
        context = {'actor_history': {}, 'persona': 'UNKNOWN'}
        
        classification = await threat_assessor.assess_threat([], context)
        
        assert classification.intent_type == "BENIGN"
        assert classification.threat_level == 1
        print(f"✅ Empty events handled correctly: {classification.intent_type}")


if __name__ == "__main__":
    # Run tests
    print("🧪 Running Enhanced Threat Assessor Tests...\n")
    pytest.main([__file__, "-v", "-s"])
