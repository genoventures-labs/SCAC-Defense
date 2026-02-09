"""
Test Suite for Enhanced Pattern Recognizer

Tests the pattern detection, prediction, and anomaly detection capabilities
of the EnhancedPatternRecognizer.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from src.schemas.events import AccessEvent
from src.engine.reasoning.enhanced_pattern_recognizer import EnhancedPatternRecognizer


@pytest.fixture
def pattern_recognizer():
    """Create pattern recognizer instance for testing."""
    return EnhancedPatternRecognizer()


@pytest.fixture
def port_scan_events():
    """Create port scanning event sequence."""
    return [
        AccessEvent(
            actor_id="scanner",
            action="scan",
            resource=f"/api/port_{i}",
            context="Port scanning",
            timestamp=datetime.now() + timedelta(seconds=i)
        )
        for i in range(10)
    ]


@pytest.fixture
def sql_injection_events():
    """Create SQL injection event sequence."""
    return [
        AccessEvent(
            actor_id="attacker",
            action="query",
            resource="/api/users?id=1' OR '1'='1",
            context="SQL injection attempt",
            timestamp=datetime.now()
        ),
        AccessEvent(
            actor_id="attacker",
            action="query",
            resource="/api/data?filter='; DROP TABLE users--",
            context="SQL injection attempt",
            timestamp=datetime.now() + timedelta(seconds=2)
        ),
    ]


@pytest.fixture
def burst_attack_events():
    """Create burst attack event sequence."""
    return [
        AccessEvent(
            actor_id="bot",
            action="request",
            resource=f"/api/endpoint",
            context="Rapid requests",
            timestamp=datetime.now() + timedelta(milliseconds=i*100)
        )
        for i in range(20)
    ]


@pytest.fixture
def attack_chain_events():
    """Create full attack chain (recon -> exploit -> exfil)."""
    base_time = datetime.now()
    return [
        # Reconnaissance
        AccessEvent(actor_id="attacker", action="scan", resource="/api", context="", timestamp=base_time),
        AccessEvent(actor_id="attacker", action="enumerate", resource="/api/admin", context="", timestamp=base_time + timedelta(seconds=5)),
        AccessEvent(actor_id="attacker", action="list", resource="/api/users", context="", timestamp=base_time + timedelta(seconds=10)),
        # Exploitation
        AccessEvent(actor_id="attacker", action="inject", resource="/api/login", context="", timestamp=base_time + timedelta(seconds=20)),
        AccessEvent(actor_id="attacker", action="execute", resource="/bin/sh", context="", timestamp=base_time + timedelta(seconds=25)),
        # Exfiltration
        AccessEvent(actor_id="attacker", action="download", resource="/data/secrets.db", context="", timestamp=base_time + timedelta(seconds=35)),
        AccessEvent(actor_id="attacker", action="copy", resource="/data/credentials", context="", timestamp=base_time + timedelta(seconds=40)),
    ]


class TestPatternRecognizer:
    """Test suite for EnhancedPatternRecognizer."""
    
    @pytest.mark.asyncio
    async def test_port_scan_detection(self, pattern_recognizer, port_scan_events):
        """Test detection of port scanning pattern."""
        patterns = await pattern_recognizer.detect_patterns(port_scan_events)
        
        # Should detect port_scan or reconnaissance pattern
        pattern_types = [p['pattern_type'] for p in patterns]
        assert any('scan' in pt or 'reconnaissance' in pt for pt in pattern_types)
        
        print(f"✅ Detected {len(patterns)} patterns in port scan:")
        for p in patterns[:3]:
            print(f"   - {p['pattern_type']}: {p['description']} (confidence: {p['confidence']:.2f})")
    
    @pytest.mark.asyncio
    async def test_sql_injection_detection(self, pattern_recognizer, sql_injection_events):
        """Test detection of SQL injection pattern."""
        patterns = await pattern_recognizer.detect_patterns(sql_injection_events)
        
        # Should detect SQL injection pattern
        pattern_types = [p['pattern_type'] for p in patterns]
        assert any('sql_injection' in pt for pt in pattern_types)
        
        print(f"✅ Detected SQL injection pattern")
        for p in patterns:
            if 'sql_injection' in p['pattern_type']:
                print(f"   Confidence: {p['confidence']:.2f}")
                print(f"   Severity: {p['severity']}")
    
    @pytest.mark.asyncio
    async def test_burst_attack_detection(self, pattern_recognizer, burst_attack_events):
        """Test detection of burst attack pattern."""
        patterns = await pattern_recognizer.detect_patterns(burst_attack_events)
        
        # Should detect burst or automated tool pattern
        pattern_types = [p['pattern_type'] for p in patterns]
        assert any('burst' in pt or 'automated' in pt or 'repetitive' in pt for pt in pattern_types)
        
        print(f"✅ Detected burst/automated pattern")
        for p in patterns:
            if 'burst' in p['pattern_type'] or 'automated' in p['pattern_type']:
                print(f"   {p['pattern_type']}: {p['description']}")
    
    @pytest.mark.asyncio
    async def test_attack_chain_detection(self, pattern_recognizer, attack_chain_events):
        """Test detection of full attack chain."""
        patterns = await pattern_recognizer.detect_patterns(attack_chain_events)
        
        # Should detect multiple patterns
        assert len(patterns) >= 2
        
        print(f"✅ Detected {len(patterns)} patterns in attack chain:")
        for p in patterns:
            print(f"   - {p['pattern_type']}: severity {p['severity']}")
    
    @pytest.mark.asyncio
    async def test_next_action_prediction(self, pattern_recognizer, port_scan_events):
        """Test prediction of next action."""
        patterns = await pattern_recognizer.detect_patterns(port_scan_events)
        
        if patterns:
            prediction = await pattern_recognizer.predict_next_action(patterns[0], port_scan_events)
            
            assert 'predicted_action' in prediction
            assert 'probability' in prediction
            assert 0.0 <= prediction['probability'] <= 1.0
            assert 'reasoning' in prediction
            
            print(f"✅ Next action prediction:")
            print(f"   Action: {prediction['predicted_action']}")
            print(f"   Probability: {prediction['probability']:.2f}")
            print(f"   Reasoning: {prediction['reasoning']}")
    
    @pytest.mark.asyncio
    async def test_anomaly_score_calculation(self, pattern_recognizer, burst_attack_events):
        """Test anomaly score calculation."""
        baseline = {
            'avg_event_count': 5,
            'std_event_count': 2.0
        }
        
        anomaly_score = await pattern_recognizer.calculate_anomaly_score(burst_attack_events, baseline)
        
        assert 0.0 <= anomaly_score <= 1.0
        assert anomaly_score >= 0.5  # Burst should be anomalous
        
        print(f"✅ Anomaly score for burst attack: {anomaly_score:.2f}")
    
    @pytest.mark.asyncio
    async def test_attack_phase_identification(self, pattern_recognizer, attack_chain_events):
        """Test identification of attack phase."""
        patterns = await pattern_recognizer.detect_patterns(attack_chain_events)
        
        # Test different portions of the attack chain
        recon_phase = await pattern_recognizer.identify_attack_phase(attack_chain_events[:3], patterns)
        exploit_phase = await pattern_recognizer.identify_attack_phase(attack_chain_events[3:5], patterns)
        exfil_phase = await pattern_recognizer.identify_attack_phase(attack_chain_events[5:], patterns)
        
        assert recon_phase == "reconnaissance"
        assert exploit_phase in ["exploitation", "installation"]
        assert exfil_phase == "actions_on_objectives"
        
        print(f"✅ Attack phases identified:")
        print(f"   Early: {recon_phase}")
        print(f"   Middle: {exploit_phase}")
        print(f"   Late: {exfil_phase}")
    
    @pytest.mark.asyncio
    async def test_attack_signature_building(self, pattern_recognizer, sql_injection_events):
        """Test building attack signature for future detection."""
        patterns = await pattern_recognizer.detect_patterns(sql_injection_events)
        
        signature = await pattern_recognizer.build_attack_signature(sql_injection_events, patterns)
        
        assert 'signature_id' in signature
        assert 'event_sequence' in signature
        assert 'pattern_types' in signature
        assert 'indicators' in signature
        
        print(f"✅ Attack signature built:")
        print(f"   ID: {signature['signature_id']}")
        print(f"   Patterns: {signature['pattern_types']}")
        print(f"   Indicators: {signature['indicators']}")
    
    @pytest.mark.asyncio
    async def test_focused_targeting_detection(self, pattern_recognizer):
        """Test detection of focused targeting (same resource accessed repeatedly)."""
        focused_events = [
            AccessEvent(
                actor_id="attacker",
                action="read",
                resource="/api/admin/secrets",
                context="",
                timestamp=datetime.now() + timedelta(seconds=i)
            )
            for i in range(8)
        ]
        
        patterns = await pattern_recognizer.detect_patterns(focused_events)
        
        pattern_types = [p['pattern_type'] for p in patterns]
        assert any('focused' in pt or 'repetitive' in pt for pt in pattern_types)
        
        print(f"✅ Detected focused targeting pattern")
    
    @pytest.mark.asyncio
    async def test_empty_events(self, pattern_recognizer):
        """Test handling of empty event list."""
        patterns = await pattern_recognizer.detect_patterns([])
        
        assert patterns == []
        print(f"✅ Empty events handled correctly")
    
    @pytest.mark.asyncio
    async def test_sequence_pattern_matching(self, pattern_recognizer, attack_chain_events):
        """Test n-gram sequence pattern matching."""
        patterns = await pattern_recognizer.detect_patterns(attack_chain_events)
        
        # Should detect sequence-based patterns
        sequence_patterns = [p for p in patterns if 'sequence' in p['pattern_type']]
        
        if sequence_patterns:
            print(f"✅ Detected {len(sequence_patterns)} sequence patterns")
            for p in sequence_patterns:
                print(f"   - {p['pattern_type']}: {p['description']}")
        else:
            print(f"✅ Sequence detection executed (no matches for this input)")


if __name__ == "__main__":
    # Run tests
    print("🧪 Running Enhanced Pattern Recognizer Tests...\n")
    pytest.main([__file__, "-v", "-s"])
