"""
Manual Integration Test for Enhanced Reasoning Components

This script manually tests the core functionality of the enhanced reasoning system
without requiring pytest infrastructure.
"""

import asyncio
from datetime import datetime, timedelta
from src.schemas.events import AccessEvent, IntentClassification
from src.engine.reasoning.enhanced_threat_assessor import EnhancedThreatAssessor
from src.engine.reasoning.enhanced_response_selector import EnhancedResponseSelector
from src.engine.reasoning.enhanced_pattern_recognizer import EnhancedPatternRecognizer


async def test_threat_assessor():
    """Test threat assessor with different event types."""
    print("\n" + "="*60)
    print("🎯 TESTING ENHANCED THREAT ASSESSOR")
    print("="*60)
    
    assessor = EnhancedThreatAssessor()
    
    # Test 1: Benign events
    print("\n📋 Test 1: Benign Events")
    benign_events = [
        AccessEvent(
            actor_id="user_123",
            action="read",
            resource="/api/public/data",
            context={"description": "Normal API access"}
        ),
        AccessEvent(
            actor_id="user_123",
            action="list",
            resource="/api/public/users",
            context={"description": "Browsing users"}
        ),
    ]
    
    result = await assessor.assess_threat(benign_events, {'actor_history': {}, 'persona': 'UNKNOWN'})
    print(f"   Intent: {result.intent_type}")
    print(f"   Threat Level: {result.threat_level}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   ✅ PASS" if result.intent_type == "BENIGN" else "   ❌ FAIL")
    
    # Test 2: Adversarial events
    print("\n📋 Test 2: Adversarial Events")
    adversarial_events = [
        AccessEvent(
            actor_id="attacker",
            action="read",
            resource="/etc/shadow",
            context={"description": "Attempting to read system files"}
        ),
        AccessEvent(
            actor_id="attacker",
            action="sudo",
            resource="/etc/passwd",
            context={"description": "Privilege escalation"}
        ),
    ]
    
    result = await assessor.assess_threat(adversarial_events, {'actor_history': {}, 'persona': 'BLACK_HAT'})
    print(f"   Intent: {result.intent_type}")
    print(f"   Threat Level: {result.threat_level}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Reasoning: {result.reasoning[:100]}...")
    print(f"   ✅ PASS" if result.intent_type == "ADVERSARIAL" and result.threat_level >= 4 else "   ❌ FAIL")


async def test_pattern_recognizer():
    """Test pattern recognizer with attack sequences."""
    print("\n" + "="*60)
    print("🔍 TESTING ENHANCED PATTERN RECOGNIZER")
    print("="*60)
    
    recognizer = EnhancedPatternRecognizer()
    
    # Test 1: SQL Injection pattern
    print("\n📋 Test 1: SQL Injection Pattern")
    sql_events = [
        AccessEvent(
            actor_id="attacker",
            action="query",
            resource="/api/users?id=1' OR '1'='1",
            context={"description": "SQL injection attempt"}
        ),
        AccessEvent(
            actor_id="attacker",
            action="query",
            resource="/api/data?filter='; DROP TABLE users--",
            context={"description": "SQL injection attempt"}
        ),
    ]
    
    patterns = await recognizer.detect_patterns(sql_events)
    print(f"   Detected {len(patterns)} patterns")
    for pattern in patterns:
        print(f"   - {pattern['pattern_type']}: confidence {pattern['confidence']:.2f}")
    print(f"   ✅ PASS" if len(patterns) > 0 else "   ❌ FAIL")
    
    # Test 2: Burst attack
    print("\n📋 Test 2: Burst Attack Pattern")
    burst_events = [
        AccessEvent(
            actor_id="bot",
            action="request",
            resource="/api/endpoint",
            context={"description": "Rapid requests"},
            timestamp=datetime.now() + timedelta(milliseconds=i*100)
        )
        for i in range(15)
    ]
    
    patterns = await recognizer.detect_patterns(burst_events)
    print(f"   Detected {len(patterns)} patterns")
    for pattern in patterns[:3]:
        print(f"   - {pattern['pattern_type']}: {pattern['description']}")
    print(f"   ✅ PASS" if any('burst' in p['pattern_type'] or 'automated' in p['pattern_type'] or 'repetitive' in p['pattern_type'] for p in patterns) else "   ❌ FAIL")
    
    # Test 3: Next action prediction
    if patterns:
        print("\n📋 Test 3: Next Action Prediction")
        prediction = await recognizer.predict_next_action(patterns[0], burst_events)
        print(f"   Predicted Action: {prediction['predicted_action']}")
        print(f"   Probability: {prediction['probability']:.2f}")
        print(f"   Reasoning: {prediction['reasoning']}")
        print(f"   ✅ PASS")


async def test_response_selector():
    """Test response selector with different threat levels."""
    print("\n" + "="*60)
    print("🛡️  TESTING ENHANCED RESPONSE SELECTOR")
    print("="*60)
    
    selector = EnhancedResponseSelector()
    available_defenses = ['block_ip', 'deep_scan', 'medusa', 'psyops', 'event_horizon', 'hallucination']
    
    # Test 1: Low threat response
    print("\n📋 Test 1: Low Threat Response")
    low_threat = IntentClassification(
        intent_type="SUSPICIOUS",
        confidence=0.6,
        reasoning="Minor anomaly",
        threat_level=2,
        suggested_action="MONITOR",
        persona_classification="UNKNOWN"
    )
    
    response = await selector.select_response(
        low_threat,
        available_defenses,
        {'actor_id': 'test', 'system_load': 0.3, 'active_defenses': []}
    )
    
    print(f"   Primary Defense: {response['primary_defense']}")
    print(f"   Secondary Defenses: {response['secondary_defenses']}")
    print(f"   ✅ PASS" if response['primary_defense'] in ['block_ip', 'deep_scan'] else "   ❌ FAIL")
    
    # Test 2: High threat response
    print("\n📋 Test 2: High Threat Response")
    high_threat = IntentClassification(
        intent_type="ADVERSARIAL",
        confidence=0.95,
        reasoning="Critical system file access",
        threat_level=5,
        suggested_action="ESCALATE",
        persona_classification="BLACK_HAT"
    )
    
    response = await selector.select_response(
        high_threat,
        available_defenses,
        {'actor_id': 'attacker', 'system_load': 0.3, 'active_defenses': []}
    )
    
    print(f"   Primary Defense: {response['primary_defense']}")
    print(f"   Secondary Defenses: {response['secondary_defenses']}")
    print(f"   Parameters: {response['parameters']}")
    print(f"   ✅ PASS" if response['primary_defense'] in ['event_horizon', 'hallucination'] else "   ❌ FAIL")
    
    # Test 3: Escalation path
    print("\n📋 Test 3: Escalation Path")
    escalation = await selector.get_escalation_path({'primary_defense': 'block_ip'}, 2)
    print(f"   Escalation steps: {len(escalation)}")
    for i, step in enumerate(escalation[:3]):
        print(f"   {i+1}. {step['defense']} - {step['trigger_condition']}")
    print(f"   ✅ PASS" if len(escalation) > 0 else "   ❌ FAIL")


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 ENHANCED REASONING COMPONENTS - INTEGRATION TEST")
    print("="*60)
    
    try:
        await test_threat_assessor()
        await test_pattern_recognizer()
        await test_response_selector()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
